from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from daily_transit.aspect_detection import signed_min_diff, wrap360
from daily_transit.constants import EPHEMERIS_NAME_MAP
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent, cycle_sort_key
from daily_transit.cycles.refine_metrics import record_refine_sample
from daily_transit.config import GeneratorConfig

logger = logging.getLogger(__name__)

TIME_TOLERANCE_SECONDS = 1.0
MAX_REFINEMENT_ITERS = 14
MAX_FRACTIONAL_BACKOFF = 0.6


def station_strength_from_rates(rate_before: float, rate_after: float) -> float:
    """Simple station strength metric: sum of magnitudes before/after crossing."""
    return abs(rate_before) + abs(rate_after)


def _probe_hours_for_body(body: str, user_probe: Optional[float]) -> float:
    if user_probe is not None:
        return user_probe
    if body == "Moon":
        return 2.0
    if body in {"Mercury", "Venus"}:
        return 6.0
    if body in {"Mars", "Sun"}:
        return 12.0
    if body in {"Jupiter", "Saturn"}:
        return 18.0
    return 24.0


def _lon_at(
    eph,
    ts,
    earth,
    body: str,
    dt: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> float:
    key = (body, dt)
    cached = pos_cache.get(key)
    if cached is not None:
        metrics["pos_cache_hits"] += 1
        return cached
    metrics["pos_cache_misses"] += 1
    eph_key = EPHEMERIS_NAME_MAP.get(body, body.lower())
    if eph_key not in eph:
        raise KeyError(f"Ephemeris missing body {body}")
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lon = earth.at(t).observe(eph[eph_key]).apparent().ecliptic_latlon()[1].degrees
    metrics["ephem_calls"] += 1
    wrapped = wrap360(lon)
    pos_cache[key] = wrapped
    return wrapped


def _velocity_sign(
    eph,
    ts,
    earth,
    body: str,
    dt: datetime,
    probe_hours: float,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> float:
    future = dt + timedelta(hours=probe_hours)
    lon_now = _lon_at(eph, ts, earth, body, dt, pos_cache, metrics)
    lon_future = _lon_at(eph, ts, earth, body, future, pos_cache, metrics)
    delta = signed_min_diff(lon_future, lon_now)
    # Velocity sign only; magnitude not used beyond refinement
    return delta / (probe_hours or 1.0)


def _refine_station(
    eph,
    ts,
    earth,
    body: str,
    probe_hours: float,
    left: datetime,
    right: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> Tuple[datetime, int]:
    l, r = (left, right) if left <= right else (right, left)
    sign_l = _velocity_sign(eph, ts, earth, body, l, probe_hours, pos_cache, metrics)
    sign_r = _velocity_sign(eph, ts, earth, body, r, probe_hours, pos_cache, metrics)
    best_time = l if abs(sign_l) <= abs(sign_r) else r
    iter_count = 0

    for _ in range(MAX_REFINEMENT_ITERS):
        iter_count += 1
        span = (r - l).total_seconds()
        if span <= TIME_TOLERANCE_SECONDS:
            break
        secant_offset = 0.0
        if sign_r != sign_l:
            secant_offset = sign_r * span / (sign_r - sign_l)
            max_jump = span * MAX_FRACTIONAL_BACKOFF
            secant_offset = max(min(secant_offset, max_jump), -max_jump)
        mid = r - timedelta(seconds=secant_offset) if secant_offset else l + timedelta(seconds=span / 2)
        sign_mid = _velocity_sign(eph, ts, earth, body, mid, probe_hours, pos_cache, metrics)
        if abs(sign_mid) < abs(_velocity_sign(eph, ts, earth, body, best_time, probe_hours, pos_cache, metrics)):
            best_time = mid
        if sign_l == 0 or (sign_l > 0) != (sign_mid > 0):
            r = mid
            sign_r = sign_mid
        else:
            l = mid
            sign_l = sign_mid

    return best_time, iter_count


def detect_retro_and_stations(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    generator_config: GeneratorConfig,
    cycle_config: CycleConfig,
    metrics: Dict[str, int],
    pos_cache: Optional[Dict[Tuple[str, datetime], float]] = None,
) -> List[CycleEvent]:
    if not cycle_config.cycle_types or not ({"retro_interval", "station"} & set(cycle_config.cycle_types)):
        return []

    merge_window_seconds = cycle_config.merge_window_hours * 3600.0 if cycle_config.merge_window_hours else None

    pos_cache = pos_cache if pos_cache is not None else {}
    events: List[CycleEvent] = []
    earth = eph["earth"]

    planet_names = list(cycle_config.cycle_planets) if cycle_config.cycle_planets else [body for body, _glyph in generator_config.planets]

    for body in planet_names:
        probe_hours = _probe_hours_for_body(body, cycle_config.retro_probe_hours or generator_config.retrograde_probe_hours)
        dt_cursor = start_dt
        step_minutes = max(30, int(probe_hours * 30))
        prev_dt: Optional[datetime] = None
        prev_sign: Optional[float] = None
        interval_start: Optional[datetime] = None

        while dt_cursor <= end_dt:
            sign_now = _velocity_sign(eph, ts, earth, body, dt_cursor, probe_hours, pos_cache, metrics)
            if prev_sign is not None:
                # Entering retrograde
                if prev_sign >= 0 and sign_now < 0:
                    try:
                        station_start, iter_count = _refine_station(
                            eph, ts, earth, body, probe_hours, prev_dt, dt_cursor, pos_cache, metrics
                        )
                        metrics["refine_calls"] += 1
                        metrics["refine_iterations"] += iter_count
                        record_refine_sample(
                            metrics,
                            {
                                "kind": "station",
                                "body": body,
                                "direction": "forward_to_retro",
                                "iter_count": iter_count,
                                "span_seconds": abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else 0.0,
                                "label": f"{body} fwd->retro",
                            },
                            cycle_config.timing_debug,
                        )
                        convergence_status = "ok"
                        uncertainty_seconds = None
                        rate_before = _velocity_sign(eph, ts, earth, body, prev_dt, probe_hours, pos_cache, metrics)
                        rate_after = _velocity_sign(eph, ts, earth, body, dt_cursor, probe_hours, pos_cache, metrics)
                        station_strength = station_strength_from_rates(rate_before, rate_after)
                    except Exception:
                        station_start = dt_cursor
                        metrics["refine_failures"] += 1
                        convergence_status = "fallback"
                        uncertainty_seconds = abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else None
                        station_strength = None
                    interval_start = station_start
                    if "station" in cycle_config.cycle_types:
                        events.append(
                            CycleEvent(
                                event_type="station",
                                body=body,
                                station_direction="forward_to_retro",
                                start_time_utc=station_start,
                                end_time_utc=station_start,
                                ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                                source_engine=cycle_config.engine,
                                merge_window_seconds=merge_window_seconds,
                                convergence_status=convergence_status,
                                uncertainty_seconds=uncertainty_seconds,
                                station_strength=station_strength,
                            )
                        )
                # Exiting retrograde
                if prev_sign < 0 and sign_now >= 0 and interval_start is not None:
                    try:
                        station_end, iter_count = _refine_station(
                            eph, ts, earth, body, probe_hours, prev_dt, dt_cursor, pos_cache, metrics
                        )
                        metrics["refine_calls"] += 1
                        metrics["refine_iterations"] += iter_count
                        record_refine_sample(
                            metrics,
                            {
                                "kind": "station",
                                "body": body,
                                "direction": "retro_to_forward",
                                "iter_count": iter_count,
                                "span_seconds": abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else 0.0,
                                "label": f"{body} retro->fwd",
                            },
                            cycle_config.timing_debug,
                        )
                        convergence_status = "ok"
                        uncertainty_seconds = None
                        rate_before = _velocity_sign(eph, ts, earth, body, prev_dt, probe_hours, pos_cache, metrics)
                        rate_after = _velocity_sign(eph, ts, earth, body, dt_cursor, probe_hours, pos_cache, metrics)
                        station_strength = station_strength_from_rates(rate_before, rate_after)
                    except Exception:
                        station_end = dt_cursor
                        metrics["refine_failures"] += 1
                        convergence_status = "fallback"
                        uncertainty_seconds = abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else None
                        station_strength = None

                    if "retro_interval" in cycle_config.cycle_types:
                        events.append(
                            CycleEvent(
                                event_type="retro_interval",
                                body=body,
                                start_time_utc=interval_start,
                                end_time_utc=station_end,
                                retrograde=True,
                                ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                                source_engine=cycle_config.engine,
                                merge_window_seconds=merge_window_seconds,
                                convergence_status=convergence_status,
                                uncertainty_seconds=uncertainty_seconds,
                                station_strength=station_strength,
                            )
                        )
                    if "station" in cycle_config.cycle_types:
                        events.append(
                            CycleEvent(
                                event_type="station",
                                body=body,
                                station_direction="retro_to_forward",
                                start_time_utc=station_end,
                                end_time_utc=station_end,
                                ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                                source_engine=cycle_config.engine,
                                merge_window_seconds=merge_window_seconds,
                                convergence_status=convergence_status,
                                uncertainty_seconds=uncertainty_seconds,
                                station_strength=station_strength,
                            )
                        )
                    interval_start = None

            prev_dt = dt_cursor
            prev_sign = sign_now
            dt_cursor += timedelta(minutes=step_minutes)

    events.sort(key=cycle_sort_key)
    return events
