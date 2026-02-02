from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from daily_transit.aspect_detection import signed_min_diff, wrap360
from daily_transit.constants import EPHEMERIS_NAME_MAP
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent, cycle_sort_key
from daily_transit.cycles.helpers import sign_after_ayanamsa
from daily_transit.cycles.refine_metrics import record_refine_sample
from daily_transit.cycles.step_tables import ingress_step_minutes, ingress_step_minutes_with_overrides
from daily_transit.config import GeneratorConfig

logger = logging.getLogger(__name__)

TIME_TOLERANCE_SECONDS = 1.0
MAX_REFINEMENT_ITERS = 14
MAX_FRACTIONAL_BACKOFF = 0.6


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
        hits_by_body = metrics.setdefault("pos_cache_hits_by_body", {})
        hits_by_body[body] = hits_by_body.get(body, 0) + 1
        return cached
    metrics["pos_cache_misses"] += 1
    misses_by_body = metrics.setdefault("pos_cache_misses_by_body", {})
    misses_by_body[body] = misses_by_body.get(body, 0) + 1
    eph_key = EPHEMERIS_NAME_MAP.get(body, body.lower())
    if eph_key not in eph:
        raise KeyError(f"Ephemeris missing body {body}")
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lon = earth.at(t).observe(eph[eph_key]).apparent().ecliptic_latlon()[1].degrees
    metrics["ephem_calls"] += 1
    calls_by_body = metrics.setdefault("ephem_calls_by_body", {})
    calls_by_body[body] = calls_by_body.get(body, 0) + 1
    wrapped = wrap360(lon)
    pos_cache[key] = wrapped
    return wrapped


def _adjusted_longitude(raw_lon: float, ayanamsa_offset: float) -> float:
    return wrap360(raw_lon - ayanamsa_offset) if ayanamsa_offset else wrap360(raw_lon)


def _target_for_sign(sign: str) -> float:
    order = (
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    )
    index = order.index(sign)
    return float(index * 30)


def _refine_ingress(
    eph,
    ts,
    earth,
    body: str,
    ayanamsa_offset: float,
    left: datetime,
    right: datetime,
    target_deg: float,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> Tuple[datetime, float, float, int]:
    best_time = left
    best_delta = float("inf")
    best_adj = None
    iter_count = 0
    l, r = (left, right) if left <= right else (right, left)

    raw_l = _lon_at(eph, ts, earth, body, l, pos_cache, metrics)
    raw_r = _lon_at(eph, ts, earth, body, r, pos_cache, metrics)
    adj_l = _adjusted_longitude(raw_l, ayanamsa_offset)
    adj_r = _adjusted_longitude(raw_r, ayanamsa_offset)
    f_l = signed_min_diff(adj_l, target_deg)
    f_r = signed_min_diff(adj_r, target_deg)
    for _ in range(MAX_REFINEMENT_ITERS):
        iter_count += 1
        span = (r - l).total_seconds()
        if span <= TIME_TOLERANCE_SECONDS:
            break

        if f_r != f_l:
            secant_offset = f_r * span / (f_r - f_l)
            # clamp to avoid overshoot; limit fractional jump relative to span
            max_jump = span * MAX_FRACTIONAL_BACKOFF
            secant_offset = max(min(secant_offset, max_jump), -max_jump)
            try_time = r - timedelta(seconds=secant_offset)
        else:
            try_time = l + timedelta(seconds=span / 2)

        if try_time < l or try_time > r:
            try_time = l + timedelta(seconds=span / 2)

        raw_try = _lon_at(eph, ts, earth, body, try_time, pos_cache, metrics)
        adj_try = _adjusted_longitude(raw_try, ayanamsa_offset)
        f_try = signed_min_diff(adj_try, target_deg)

        if abs(f_try) < best_delta:
            best_time = try_time
            best_delta = abs(f_try)
            best_adj = adj_try

        mid = l + timedelta(seconds=span / 2)
        raw_mid = _lon_at(eph, ts, earth, body, mid, pos_cache, metrics)
        adj_mid = _adjusted_longitude(raw_mid, ayanamsa_offset)
        f_mid = signed_min_diff(adj_mid, target_deg)
        if abs(f_mid) < best_delta:
            best_time = mid
            best_delta = abs(f_mid)
            best_adj = adj_mid

        if f_l * f_try <= 0:
            r, raw_r, adj_r, f_r = try_time, raw_try, adj_try, f_try
        elif f_try * f_r <= 0:
            l, raw_l, adj_l, f_l = try_time, raw_try, adj_try, f_try
        elif f_l * f_mid <= 0:
            r, raw_r, adj_r, f_r = mid, raw_mid, adj_mid, f_mid
        else:
            l, raw_l, adj_l, f_l = mid, raw_mid, adj_mid, f_mid

    if best_adj is None:
        best_adj = adj_l
    delta_seconds = abs((best_time - left).total_seconds())
    return best_time, best_adj, delta_seconds, iter_count


def detect_ingresses(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    generator_config: GeneratorConfig,
    cycle_config: CycleConfig,
    metrics: Dict[str, int],
    pos_cache: Optional[Dict[Tuple[str, datetime], float]] = None,
    sep_cache: Optional[Dict] = None,
) -> List[CycleEvent]:
    if not cycle_config.cycle_types or "ingress" not in cycle_config.cycle_types:
        return []

    earth = eph["earth"]
    ayanamsa_offset_fn = None
    if cycle_config.ayanamsa:
        from daily_transit.ayanamsa import get_ayanamsa_offset  # local import to avoid cycles

        def ayanamsa_offset_fn(dt: datetime) -> float:
            return get_ayanamsa_offset(dt, cycle_config.ayanamsa)

    allowed_signs = set(cycle_config.ingress_signs) if cycle_config.ingress_signs else None
    merge_window_seconds = None
    if cycle_config.merge_window_hours is not None:
        merge_window_seconds = cycle_config.merge_window_hours * 3600.0

    pos_cache = pos_cache if pos_cache is not None else {}
    events: List[CycleEvent] = []

    override_map = getattr(cycle_config, "ingress_step_overrides", None)

    planet_names = list(cycle_config.cycle_planets) if cycle_config.cycle_planets else [body for body, _glyph in generator_config.planets]

    base_start = getattr(generator_config, "start_date", start_dt)

    for body in planet_names:
        step_minutes = ingress_step_minutes_with_overrides(body, override_map)
        dt_cursor = start_dt
        prev_dt: Optional[datetime] = None
        prev_sign: Optional[str] = None
        prev_adj: Optional[float] = None
        prev_offset: float = 0.0

        # Backfill: seed the window with the sign occupied at the window start so spans include leading occupancy.
        if start_dt == base_start:
            raw_start = _lon_at(eph, ts, earth, body, start_dt, pos_cache, metrics)
            offset_start = ayanamsa_offset_fn(start_dt) if ayanamsa_offset_fn else 0.0
            adj_start = _adjusted_longitude(raw_start, offset_start)
            sign_start = sign_after_ayanamsa(adj_start)
            if not allowed_signs or sign_start in allowed_signs:
                events.append(
                    CycleEvent(
                        event_type="ingress",
                        body=body,
                        sign=sign_start,
                        start_time_utc=start_dt,
                        end_time_utc=start_dt,
                        ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                        source_engine=cycle_config.engine,
                        adjusted_longitude=adj_start,
                        raw_longitude=raw_start,
                        merge_window_seconds=merge_window_seconds,
                        convergence_status="backfill",
                        computation_notes="ingress_backfill_start",
                    )
                )
            prev_dt = start_dt
            prev_sign = sign_start
            prev_adj = adj_start
            prev_offset = offset_start

        while dt_cursor <= end_dt:
            raw_lon = _lon_at(eph, ts, earth, body, dt_cursor, pos_cache, metrics)
            ayanamsa_offset = ayanamsa_offset_fn(dt_cursor) if ayanamsa_offset_fn else 0.0
            adj_lon = _adjusted_longitude(raw_lon, ayanamsa_offset)
            current_sign = sign_after_ayanamsa(adj_lon)

            if prev_dt is not None and prev_adj is not None:
                delta = abs(signed_min_diff(adj_lon, prev_adj))
                if delta > 40.0:
                    mid_dt = prev_dt + (dt_cursor - prev_dt) / 2
                    if mid_dt > prev_dt and mid_dt < dt_cursor:
                        raw_mid = _lon_at(eph, ts, earth, body, mid_dt, pos_cache, metrics)
                        mid_offset = ayanamsa_offset_fn(mid_dt) if ayanamsa_offset_fn else 0.0
                        mid_adj = _adjusted_longitude(raw_mid, mid_offset)
                        mid_sign = sign_after_ayanamsa(mid_adj)

                        if mid_sign != prev_sign:
                            target_deg = _target_for_sign(mid_sign)
                            try:
                                refined_time, refined_adj, _, iter_count = _refine_ingress(
                                    eph,
                                    ts,
                                    earth,
                                    body,
                                    prev_offset,
                                    prev_dt,
                                    mid_dt,
                                    target_deg,
                                    pos_cache,
                                    metrics,
                                )
                                metrics["refine_calls"] += 1
                                metrics["refine_iterations"] += iter_count
                                record_refine_sample(
                                    metrics,
                                    {
                                        "kind": "ingress",
                                        "body": body,
                                        "sign": mid_sign,
                                        "iter_count": iter_count,
                                        "span_seconds": abs((mid_dt - prev_dt).total_seconds()) if prev_dt else 0.0,
                                        "label": f"{body}->{mid_sign}",
                                    },
                                    cycle_config.timing_debug,
                                )
                                convergence_status = "ok"
                                uncertainty_seconds = None
                            except Exception:
                                refined_time = mid_dt
                                refined_adj = mid_adj
                                metrics["refine_failures"] += 1
                                convergence_status = "fallback"
                                uncertainty_seconds = abs((mid_dt - prev_dt).total_seconds()) if prev_dt else None

                            ev = CycleEvent(
                                event_type="ingress",
                                body=body,
                                sign=mid_sign,
                                start_time_utc=refined_time,
                                end_time_utc=refined_time,
                                ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                                source_engine=cycle_config.engine,
                                adjusted_longitude=refined_adj,
                                raw_longitude=raw_mid,
                                merge_window_seconds=merge_window_seconds,
                                convergence_status=convergence_status,
                                uncertainty_seconds=uncertainty_seconds,
                            )
                            events.append(ev)

                        prev_dt = mid_dt
                        prev_sign = mid_sign
                        prev_offset = mid_offset
                        prev_adj = mid_adj
                        continue

            if prev_sign is not None and current_sign != prev_sign:
                if allowed_signs and current_sign not in allowed_signs:
                    prev_dt = dt_cursor
                    prev_sign = current_sign
                    prev_adj = adj_lon
                    prev_offset = ayanamsa_offset
                    dt_cursor += timedelta(minutes=step_minutes)
                    continue

                target_deg = _target_for_sign(current_sign)
                try:
                    refined_time, refined_adj, _, iter_count = _refine_ingress(
                        eph,
                        ts,
                        earth,
                        body,
                        prev_offset,
                        prev_dt,
                        dt_cursor,
                        target_deg,
                        pos_cache,
                        metrics,
                    )
                    metrics["refine_calls"] += 1
                    metrics["refine_iterations"] += iter_count
                    record_refine_sample(
                        metrics,
                        {
                            "kind": "ingress",
                            "body": body,
                            "sign": current_sign,
                            "iter_count": iter_count,
                            "span_seconds": abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else 0.0,
                            "label": f"{body}->{current_sign}",
                        },
                        cycle_config.timing_debug,
                    )
                    convergence_status = "ok"
                    uncertainty_seconds = None
                except Exception:
                    refined_time = dt_cursor
                    refined_adj = adj_lon
                    metrics["refine_failures"] += 1
                    convergence_status = "fallback"
                    uncertainty_seconds = abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else None

                ev = CycleEvent(
                    event_type="ingress",
                    body=body,
                    sign=current_sign,
                    start_time_utc=refined_time,
                    end_time_utc=refined_time,
                    ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                    source_engine=cycle_config.engine,
                    adjusted_longitude=refined_adj,
                    raw_longitude=raw_lon,
                    merge_window_seconds=merge_window_seconds,
                    convergence_status=convergence_status,
                    uncertainty_seconds=uncertainty_seconds,
                )
                events.append(ev)

            prev_dt = dt_cursor
            prev_sign = current_sign
            prev_adj = adj_lon
            prev_offset = ayanamsa_offset
            dt_cursor += timedelta(minutes=step_minutes)

    events.sort(key=cycle_sort_key)
    return events
