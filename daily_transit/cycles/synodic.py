from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from skyfield.errors import EphemerisRangeError

from daily_transit.aspect_detection import signed_min_diff, wrap360
from daily_transit.constants import EPHEMERIS_NAME_MAP
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent, cycle_sort_key
from daily_transit.cycles.helpers import sign_after_ayanamsa
from daily_transit.cycles.refine_metrics import record_refine_sample
from daily_transit.cycles.step_tables import synodic_pair_key, synodic_pair_step_minutes_with_overrides
from daily_transit.config import GeneratorConfig

logger = logging.getLogger(__name__)

TIME_TOLERANCE_SECONDS = 1.0
MAX_REFINEMENT_ITERS = 14
MAX_FRACTIONAL_BACKOFF = 0.6
MAX_SEPARATION_JUMP_DEG = 120.0
ANCHOR_MAX_YEARS = 700  # generous horizon to find very slow outer pairs
ANCHOR_STEP_DAYS = 90   # coarse step for anchor search to limit ephem calls


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
        metrics["pos_cache_hits"] = metrics.get("pos_cache_hits", 0) + 1
        hits_by_body = metrics.setdefault("pos_cache_hits_by_body", {})
        hits_by_body[body] = hits_by_body.get(body, 0) + 1
        return cached
    metrics["pos_cache_misses"] = metrics.get("pos_cache_misses", 0) + 1
    misses_by_body = metrics.setdefault("pos_cache_misses_by_body", {})
    misses_by_body[body] = misses_by_body.get(body, 0) + 1
    eph_key = EPHEMERIS_NAME_MAP.get(body, body.lower())
    if eph_key not in eph:
        raise KeyError(f"Ephemeris missing body {body}")
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lon = earth.at(t).observe(eph[eph_key]).apparent().ecliptic_latlon()[1].degrees
    metrics["ephem_calls"] = metrics.get("ephem_calls", 0) + 1
    calls_by_body = metrics.setdefault("ephem_calls_by_body", {})
    calls_by_body[body] = calls_by_body.get(body, 0) + 1
    wrapped = wrap360(lon)
    pos_cache[key] = wrapped
    return wrapped


def _adjusted_longitude(raw_lon: float, ayanamsa_offset: float) -> float:
    return wrap360(raw_lon - ayanamsa_offset) if ayanamsa_offset else wrap360(raw_lon)


def _synodic_separation(
    eph,
    ts,
    earth,
    body1: str,
    body2: str,
    dt: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
    ayanamsa_offset: float,
    sep_cache: Optional[Dict[Tuple[str, str, datetime, float], float]] = None,
) -> float:
    cache = sep_cache if sep_cache is not None else None
    cache_key = None
    if cache is not None:
        cache_key = (body1, body2, dt, round(ayanamsa_offset, 9))
        cached = cache.get(cache_key)
        if cached is not None:
            metrics["sep_cache_hits"] = metrics.get("sep_cache_hits", 0) + 1
            hits_by_pair = metrics.setdefault("sep_cache_hits_by_pair", {})
            hits_key = synodic_pair_key(body1, body2)
            hits_by_pair[hits_key] = hits_by_pair.get(hits_key, 0) + 1
            return cached
        metrics["sep_cache_misses"] = metrics.get("sep_cache_misses", 0) + 1
        misses_by_pair = metrics.setdefault("sep_cache_misses_by_pair", {})
        misses_key = synodic_pair_key(body1, body2)
        misses_by_pair[misses_key] = misses_by_pair.get(misses_key, 0) + 1

    lon1 = _lon_at(eph, ts, earth, body1, dt, pos_cache, metrics)
    lon2 = _lon_at(eph, ts, earth, body2, dt, pos_cache, metrics)
    adj1 = _adjusted_longitude(lon1, ayanamsa_offset)
    adj2 = _adjusted_longitude(lon2, ayanamsa_offset)
    sep = wrap360(adj2 - adj1)
    if cache is not None and cache_key is not None:
        cache[cache_key] = sep
    return sep


def _refine_synodic(
    eph,
    ts,
    earth,
    body1: str,
    body2: str,
    ayanamsa_offset_fn,
    left: datetime,
    right: datetime,
    target_deg: float,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> Tuple[datetime, float, float, int]:
    best_time = left
    best_sep = None
    best_delta_deg = float("inf")
    iter_count = 0
    l, r = (left, right) if left <= right else (right, left)

    def f(dt: datetime) -> float:
        offset = ayanamsa_offset_fn(dt) if ayanamsa_offset_fn else 0.0
        sep = _synodic_separation(eph, ts, earth, body1, body2, dt, pos_cache, metrics, offset)
        return signed_min_diff(sep, target_deg), sep

    f_l, sep_l = f(l)
    f_r, sep_r = f(r)
    if abs(f_l) <= abs(f_r):
        best_time, best_sep, best_delta_deg = l, sep_l, abs(f_l)
    else:
        best_time, best_sep, best_delta_deg = r, sep_r, abs(f_r)

    for _ in range(MAX_REFINEMENT_ITERS):
        iter_count += 1
        span = (r - l).total_seconds()
        if span <= TIME_TOLERANCE_SECONDS:
            break

        if f_r != f_l:
            secant_offset = f_r * span / (f_r - f_l)
            max_jump = span * MAX_FRACTIONAL_BACKOFF
            secant_offset = max(min(secant_offset, max_jump), -max_jump)
            try_time = r - timedelta(seconds=secant_offset)
        else:
            try_time = l + timedelta(seconds=span / 2)

        if try_time < l or try_time > r:
            try_time = l + timedelta(seconds=span / 2)

        f_try, sep_try = f(try_time)
        if abs(f_try) < best_delta_deg:
            best_time, best_sep, best_delta_deg = try_time, sep_try, abs(f_try)

        mid = l + timedelta(seconds=span / 2)
        f_mid, sep_mid = f(mid)
        if abs(f_mid) < best_delta_deg:
            best_time, best_sep, best_delta_deg = mid, sep_mid, abs(f_mid)

        if f_l * f_try <= 0:
            r, sep_r, f_r = try_time, sep_try, f_try
        elif f_try * f_r <= 0:
            l, sep_l, f_l = try_time, sep_try, f_try
        elif f_l * f_mid <= 0:
            r, sep_r, f_r = mid, sep_mid, f_mid
        else:
            l, sep_l, f_l = mid, sep_mid, f_mid

    if best_sep is None:
        best_sep = sep_l
    delta_seconds = abs((best_time - left).total_seconds())
    return best_time, best_sep, best_delta_deg, iter_count


def _find_conjunction_anchor(
    eph,
    ts,
    earth,
    body1: str,
    body2: str,
    ayanamsa_offset_fn,
    start_dt: datetime,
    direction: int,
    pos_cache: Dict[Tuple[str, datetime], float],
    sep_cache: Optional[Dict[Tuple[str, str, datetime, float], float]],
    metrics: Dict[str, int],
) -> Optional[Tuple[datetime, float, float, int]]:
    """Find nearest conjunction in one direction for a pair.

    Searches from start_dt outward (direction +/-1) with coarse steps until a
    sign flip around 0° separation is found, then refines.
    """

    horizon = timedelta(days=ANCHOR_MAX_YEARS * 365)
    step = timedelta(days=ANCHOR_STEP_DAYS * max(1, abs(direction))) * (1 if direction >= 0 else -1)

    def separation_at(dt: datetime) -> Tuple[float, float]:
        offset = ayanamsa_offset_fn(dt) if ayanamsa_offset_fn else 0.0
        raw = _synodic_separation(eph, ts, earth, body1, body2, dt, pos_cache, metrics, offset, sep_cache=sep_cache)
        return raw, signed_min_diff(raw, 0.0)

    prev_dt = start_dt
    prev_raw, prev_val = separation_at(prev_dt)
    cursor = prev_dt + step

    while abs(cursor - start_dt) <= horizon:
        try:
            raw, val = separation_at(cursor)
        except EphemerisRangeError:
            metrics["synodic_anchor_out_of_range"] = metrics.get("synodic_anchor_out_of_range", 0) + 1
            return None
        crosses_zero_band = (
            prev_raw <= 60.0
            or raw <= 60.0
            or (prev_raw >= 300.0 and raw <= 60.0)
            or (raw >= 300.0 and prev_raw <= 60.0)
        )
        if (val == 0 or (prev_val != 0 and (val > 0) != (prev_val > 0))) and crosses_zero_band:
            try:
                refined_time, refined_sep, best_delta_deg, iter_count = _refine_synodic(
                    eph,
                    ts,
                    earth,
                    body1,
                    body2,
                    ayanamsa_offset_fn,
                    prev_dt,
                    cursor,
                    0.0,
                    pos_cache,
                    metrics,
                )
                return refined_time, refined_sep, best_delta_deg, iter_count
            except Exception:
                metrics["synodic_anchor_refine_failures"] = metrics.get("synodic_anchor_refine_failures", 0) + 1
                return None
        prev_dt = cursor
        prev_val = val
        prev_raw = raw
        cursor += step

    metrics["synodic_anchor_not_found"] = metrics.get("synodic_anchor_not_found", 0) + 1
    return None


def detect_synodic_phases(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    generator_config: GeneratorConfig,
    cycle_config: CycleConfig,
    metrics: Dict[str, int],
        pos_cache: Optional[Dict[Tuple[str, datetime], float]] = None,
        sep_cache: Optional[Dict[Tuple[str, str, datetime, float], float]] = None,
) -> List[CycleEvent]:
    if not cycle_config.cycle_types or "synodic_phase" not in cycle_config.cycle_types:
        return []

    phase_angles_raw = cycle_config.phase_angles or []
    if cycle_config.synodic_mode == "conjunction_only":
        phase_angles_raw = [0.0]
    if not phase_angles_raw:
        return []

    normalized_phases: List[float] = []
    seen = set()
    for angle in phase_angles_raw:
        norm = 0.0 if math.isclose(angle, 360.0, abs_tol=1e-9) else angle
        if norm in seen:
            continue
        seen.add(norm)
        normalized_phases.append(norm)
    normalized_phases.sort()

    earth = eph["earth"]
    ayanamsa_offset_fn = None
    if cycle_config.ayanamsa:
        from daily_transit.ayanamsa import get_ayanamsa_offset  # local import to avoid cycles

        def ayanamsa_offset_fn(dt: datetime) -> float:
            return get_ayanamsa_offset(dt, cycle_config.ayanamsa)

    merge_window_seconds = None
    if cycle_config.merge_window_hours is not None:
        merge_window_seconds = cycle_config.merge_window_hours * 3600.0

    pos_cache = pos_cache if pos_cache is not None else {}
    sep_cache = sep_cache if sep_cache is not None else {}
    events: List[CycleEvent] = []

    override_map = getattr(cycle_config, "synodic_pair_step_overrides", None)

    if cycle_config.cycle_planets:
        planet_names: List[str] = list(cycle_config.cycle_planets)
    else:
        planet_names = [p[0] for p in generator_config.planets]

    allowed_pairs = None
    if cycle_config.synodic_pairs:
        allowed_pairs = set(cycle_config.synodic_pairs)

    for idx in range(len(planet_names)):
        for jdx in range(idx + 1, len(planet_names)):
            body1 = planet_names[idx]
            body2 = planet_names[jdx]
            pair_key = synodic_pair_key(body1, body2)
            if allowed_pairs is not None and pair_key not in allowed_pairs:
                continue
            step_minutes = synodic_pair_step_minutes_with_overrides(body1, body2, override_map)
            if cycle_config.synodic_step_scale and cycle_config.synodic_step_scale != 1.0:
                step_minutes = max(1, int(step_minutes * cycle_config.synodic_step_scale))
            step_minutes = min(step_minutes, max(1, cycle_config.synodic_step_cap_minutes))
            dt_cursor = start_dt
            prev_vals: Dict[float, Tuple[datetime, float]] = {}
            prev_sep: Optional[float] = None
            prev_dt: Optional[datetime] = None
            pair_events = 0

            while dt_cursor <= end_dt:
                offset = ayanamsa_offset_fn(dt_cursor) if ayanamsa_offset_fn else 0.0
                sep = _synodic_separation(
                    eph,
                    ts,
                    earth,
                    body1,
                    body2,
                    dt_cursor,
                    pos_cache,
                    metrics,
                    offset,
                    sep_cache=sep_cache,
                )

                if prev_sep is not None and prev_dt is not None:
                    jump = abs(signed_min_diff(sep, prev_sep))
                    if jump > MAX_SEPARATION_JUMP_DEG:
                        mid_dt = prev_dt + (dt_cursor - prev_dt) / 2
                        if mid_dt > prev_dt and mid_dt < dt_cursor:
                            dt_cursor = mid_dt
                            step_minutes = max(1, step_minutes // 2)
                            continue

                for phase in normalized_phases:
                    val = signed_min_diff(sep, phase)
                    prev_entry = prev_vals.get(phase)
                    if prev_entry is not None:
                        prev_dt, prev_val = prev_entry
                        sign_flip = (val > 0) != (prev_val > 0) and val != 0 and prev_val != 0
                        if val == 0 or sign_flip:
                            try:
                                refined_time, refined_sep, best_delta_deg, iter_count = _refine_synodic(
                                    eph,
                                    ts,
                                    earth,
                                    body1,
                                    body2,
                                    ayanamsa_offset_fn,
                                    prev_dt,
                                    dt_cursor,
                                    phase,
                                    pos_cache,
                                    metrics,
                                )
                                metrics["refine_calls"] = metrics.get("refine_calls", 0) + 1
                                metrics["refine_iterations"] = metrics.get("refine_iterations", 0) + iter_count
                                record_refine_sample(
                                    metrics,
                                    {
                                        "kind": "synodic",
                                        "pair": synodic_pair_key(body1, body2),
                                        "phase": phase,
                                        "iter_count": iter_count,
                                        "span_seconds": abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else 0.0,
                                        "label": f"{body1}|{body2}@{phase}",
                                        "delta_deg": best_delta_deg,
                                    },
                                    cycle_config.timing_debug,
                                )
                                convergence_status = "ok"
                                uncertainty_seconds = None
                            except Exception:
                                refined_time = dt_cursor
                                refined_sep = sep
                                metrics["refine_failures"] = metrics.get("refine_failures", 0) + 1
                                convergence_status = "fallback"
                                uncertainty_seconds = abs((dt_cursor - prev_dt).total_seconds()) if prev_dt else None
                                best_delta_deg = abs(signed_min_diff(sep, phase))

                            max_delta = cycle_config.synodic_max_delta_deg if hasattr(cycle_config, "synodic_max_delta_deg") else 0.0
                            if max_delta and best_delta_deg is not None and abs(best_delta_deg) > max_delta:
                                metrics.setdefault("synodic_dropped_delta", 0)
                                metrics["synodic_dropped_delta"] += 1
                            else:
                                raw_lon1 = _lon_at(eph, ts, earth, body1, refined_time, pos_cache, metrics)
                                raw_lon2 = _lon_at(eph, ts, earth, body2, refined_time, pos_cache, metrics)
                                offset = ayanamsa_offset_fn(refined_time) if ayanamsa_offset_fn else 0.0
                                adj1 = _adjusted_longitude(raw_lon1, offset)
                                adj2 = _adjusted_longitude(raw_lon2, offset)
                                sign1 = sign_after_ayanamsa(adj1)
                                sign2 = sign_after_ayanamsa(adj2)

                                events.append(
                                    CycleEvent(
                                        event_type="synodic_phase",
                                        body1=body1,
                                        body2=body2,
                                        phase_angle=phase,
                                        start_time_utc=refined_time,
                                        end_time_utc=refined_time,
                                        ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                                        source_engine=cycle_config.engine,
                                        separation_deg=refined_sep,
                                        delta_deg=best_delta_deg,
                                        merge_window_seconds=merge_window_seconds,
                                        convergence_status=convergence_status,
                                        uncertainty_seconds=uncertainty_seconds,
                                        raw_longitude=raw_lon1,
                                        adjusted_longitude=adj1,
                                        raw_longitude_body2=raw_lon2,
                                        adjusted_longitude_body2=adj2,
                                        start_sign=sign1,
                                        end_sign=sign2,
                                    )
                                )
                                pair_events += 1

                    prev_vals[phase] = (dt_cursor, val)

                dt_cursor += timedelta(minutes=step_minutes)
                prev_sep = sep
                prev_dt = dt_cursor

            # If no conjunction was found within the window, backfill anchors just outside it.
            if pair_events == 0 and normalized_phases == [0.0]:
                anchor_hits = []
                for direction in (-1, 1):
                    anchor = _find_conjunction_anchor(
                        eph,
                        ts,
                        earth,
                        body1,
                        body2,
                        ayanamsa_offset_fn,
                        start_dt if direction < 0 else end_dt,
                        direction,
                        pos_cache,
                        sep_cache,
                        metrics,
                    )
                    if anchor is None:
                        continue
                    refined_time, refined_sep, best_delta_deg, iter_count = anchor
                    raw_lon1 = _lon_at(eph, ts, earth, body1, refined_time, pos_cache, metrics)
                    raw_lon2 = _lon_at(eph, ts, earth, body2, refined_time, pos_cache, metrics)
                    offset = ayanamsa_offset_fn(refined_time) if ayanamsa_offset_fn else 0.0
                    adj1 = _adjusted_longitude(raw_lon1, offset)
                    adj2 = _adjusted_longitude(raw_lon2, offset)
                    sign1 = sign_after_ayanamsa(adj1)
                    sign2 = sign_after_ayanamsa(adj2)
                    events.append(
                        CycleEvent(
                            event_type="synodic_phase",
                            body1=body1,
                            body2=body2,
                            phase_angle=0.0,
                            start_time_utc=refined_time,
                            end_time_utc=refined_time,
                            ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                            source_engine=cycle_config.engine,
                            separation_deg=refined_sep,
                            delta_deg=best_delta_deg,
                            merge_window_seconds=merge_window_seconds,
                            convergence_status="anchor",
                            raw_longitude=raw_lon1,
                            adjusted_longitude=adj1,
                            raw_longitude_body2=raw_lon2,
                            adjusted_longitude_body2=adj2,
                            start_sign=sign1,
                            end_sign=sign2,
                            computation_notes="synodic_anchor_outside_window",
                        )
                    )
                    anchor_hits.append(direction)
                if anchor_hits:
                    metrics["synodic_anchor_added"] = metrics.get("synodic_anchor_added", 0) + len(anchor_hits)

    events.sort(key=cycle_sort_key)
    return events
