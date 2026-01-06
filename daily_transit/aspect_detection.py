from __future__ import annotations

from dataclasses import dataclass
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from skyfield.api import Loader

from .constants import DEFAULT_PLANETS, EPHEMERIS_NAME_MAP

FAST_RELATIVE_SPEED_THRESHOLD = 2.0  # degrees per hour
MIN_COARSE_STEP_MINUTES = 5
MIN_PROBE_HOURS = 0.25


def _compute_relative_speed(prev_rel: float, current_rel: float, delta_hours: float) -> float:
    if delta_hours <= 0:
        return 0.0
    diff = signed_min_diff(current_rel, prev_rel)
    return abs(diff) / delta_hours


def _adaptive_step_minutes(
    base_minutes: int,
    max_relative_speed: Optional[float],
) -> int:
    min_allowed = min(base_minutes, MIN_COARSE_STEP_MINUTES)
    if not max_relative_speed or max_relative_speed <= FAST_RELATIVE_SPEED_THRESHOLD:
        return max(min_allowed, base_minutes)
    scaled = base_minutes * (FAST_RELATIVE_SPEED_THRESHOLD / max_relative_speed)
    bounded = max(min_allowed, min(base_minutes, int(round(scaled))))
    return max(min_allowed, bounded)


def _dynamic_probe_hours(base_probe: float, approx_speed: Optional[float]) -> float:
    if approx_speed is None or approx_speed <= 0:
        return max(MIN_PROBE_HOURS, min(base_probe, 3.0))
    adaptive = 2.0 / max(approx_speed, 0.1)
    return max(MIN_PROBE_HOURS, min(base_probe, adaptive))


def _pair_merge_window_hours(pair: Tuple[str, str], base_merge_hours: float) -> float:
    window = base_merge_hours
    if "Moon" in pair:
        window = min(window, 3.5)
    elif any(body in {"Mercury", "Venus"} for body in pair):
        window = min(window, 1.0)
    return max(window, 0.0833)  # never below ~5 minutes


def merge_aspect_events(
    events: List[AspectEvent],
    merge_window_hours: float,
    timing_debug: bool = False,
) -> List[AspectEvent]:
    grouped: Dict[Tuple[str, str, str], List[AspectEvent]] = {}
    for ev in events:
        key = (ev.planet1, ev.planet2, ev.aspect)
        grouped.setdefault(key, []).append(ev)

    merged: List[AspectEvent] = []

    for key, ev_list in grouped.items():
        ev_list.sort(key=lambda e: e.time)
        cluster: List[AspectEvent] = []
        pair_window = timedelta(hours=_pair_merge_window_hours((key[0], key[1]), merge_window_hours))
        if timing_debug:
            logging.debug(
                "Merge window for %s-%s: %s",
                key[0],
                key[1],
                pair_window,
            )
        for ev in ev_list:
            if not cluster:
                cluster.append(ev)
                continue
            if ev.time - cluster[-1].time <= pair_window:
                cluster.append(ev)
            else:
                best = min(cluster, key=lambda x: (x.delta, x.time))
                merged.append(best)
                cluster = [ev]
        if cluster:
            best = min(cluster, key=lambda x: (x.delta, x.time))
            merged.append(best)

    merged.sort(key=lambda e: e.time)
    if timing_debug:
        logging.debug("Total merged aspects: %s", len(merged))
    return merged


@dataclass
class AspectEvent:
    time: datetime
    planet1: str
    planet2: str
    aspect: str
    exact_degrees: float
    raw_separation: float
    delta: float
    planet1_retrograde: bool
    planet2_retrograde: bool


def wrap360(angle: float) -> float:
    return angle % 360.0


def signed_min_diff(angle: float, target: float) -> float:
    diff = (angle - target + 180) % 360 - 180
    return diff


def minimal_abs_separation(rel_angle: float, target: float) -> float:
    return abs(signed_min_diff(rel_angle, target))


def datetime_range(start_dt: datetime, end_dt: datetime, step: timedelta):
    cur = start_dt
    while cur <= end_dt:
        yield cur
        cur += step


def to_timescale(ts: Loader.timescale, dt: datetime):
    return ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)


def raw_separation_at(eph, earth, ts, planet1: str, planet2: str, dt: datetime) -> float:
    name1 = EPHEMERIS_NAME_MAP.get(planet1, planet1.lower())
    name2 = EPHEMERIS_NAME_MAP.get(planet2, planet2.lower())
    t = to_timescale(ts, dt)
    lon1 = earth.at(t).observe(eph[name1]).apparent().ecliptic_latlon()[1].degrees
    lon2 = earth.at(t).observe(eph[name2]).apparent().ecliptic_latlon()[1].degrees
    return wrap360(lon2 - lon1)


def ecliptic_longitude(eph, earth, ts, planet: str, dt: datetime) -> float:
    key = EPHEMERIS_NAME_MAP.get(planet, planet.lower())
    t = to_timescale(ts, dt)
    return wrap360(earth.at(t).observe(eph[key]).apparent().ecliptic_latlon()[1].degrees)


def is_retrograde(
    eph,
    earth,
    ts,
    planet: str,
    dt: datetime,
    probe_hours: float,
    approx_speed: Optional[float] = None,
) -> bool:
    window_hours = _dynamic_probe_hours(probe_hours, approx_speed)
    delta = timedelta(hours=window_hours)
    if delta.total_seconds() < 60:
        delta = timedelta(seconds=60)

    lon_before = ecliptic_longitude(eph, earth, ts, planet, dt - delta)
    lon_now = ecliptic_longitude(eph, earth, ts, planet, dt)
    lon_after = ecliptic_longitude(eph, earth, ts, planet, dt + delta)

    forward_diff = (lon_after - lon_now + 540.0) % 360.0 - 180.0
    backward_diff = (lon_now - lon_before + 540.0) % 360.0 - 180.0
    return forward_diff < 0 and backward_diff < 0


def planet_pairs(planets: List[Tuple[str, str]] = None) -> List[Tuple[str, str]]:
    base = planets or DEFAULT_PLANETS
    names = [p[0] for p in base]
    return [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))]


def refine_exact_time(
    eph,
    ts,
    planet1: str,
    planet2: str,
    target_deg: float,
    t1: datetime,
    t2: datetime,
    refine_step_mins: int,
    ternary_iterations: int = 8,
) -> Tuple[datetime, float, float]:
    earth = eph['earth']

    def evaluate(dt: datetime) -> Tuple[float, float]:
        raw_sep = raw_separation_at(eph, earth, ts, planet1, planet2, dt)
        delta_val = minimal_abs_separation(raw_sep, target_deg)
        return raw_sep, delta_val

    best_time = t1
    best_raw, best_delta = evaluate(t1)
    end_raw, end_delta = evaluate(t2)
    if end_delta < best_delta:
        best_time, best_raw, best_delta = t2, end_raw, end_delta

    left = t1
    right = t2
    min_step_seconds = max(60, refine_step_mins * 60)

    for _ in range(ternary_iterations):
        span_seconds = (right - left).total_seconds()
        if span_seconds <= min_step_seconds:
            break
        left_third = left + timedelta(seconds=span_seconds / 3)
        right_third = right - timedelta(seconds=span_seconds / 3)
        raw_left, delta_left = evaluate(left_third)
        raw_right, delta_right = evaluate(right_third)
        if delta_left < delta_right:
            right = right_third
        else:
            left = left_third
        if delta_left < best_delta:
            best_time, best_raw, best_delta = left_third, raw_left, delta_left
        if delta_right < best_delta:
            best_time, best_raw, best_delta = right_third, raw_right, delta_right

    step = timedelta(seconds=min_step_seconds)
    cur = left
    while cur <= right:
        raw_cur, delta_cur = evaluate(cur)
        if delta_cur < best_delta:
            best_time, best_raw, best_delta = cur, raw_cur, delta_cur
        cur += step

    raw_right_final, delta_right_final = evaluate(right)
    if delta_right_final < best_delta:
        best_time, best_raw, best_delta = right, raw_right_final, delta_right_final

    fine_window = timedelta(seconds=max(60, min_step_seconds))
    fine_start = max(best_time - fine_window, left)
    fine_end = min(best_time + fine_window, right)

    current = fine_start
    best_delta_seconds = best_delta
    while current <= fine_end:
        raw_cur, delta_cur = evaluate(current)
        if delta_cur < best_delta_seconds:
            best_time, best_raw, best_delta = current, raw_cur, delta_cur
            best_delta_seconds = delta_cur
        current += timedelta(seconds=1)

    return best_time, best_raw, best_delta


def detect_aspects(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    orb: float,
    aspect_degrees: Dict[str, float],
    planets: List[Tuple[str, str]],
    coarse_step_mins: int,
    refine_step_mins: int,
    merge_window_hours: float,
    retrograde_probe_hours: float,
    timing_debug: bool = False,
) -> List[AspectEvent]:
    if not aspect_degrees:
        logging.warning("No aspect degrees provided; detection will emit no events.")
        return []
    pairs = planet_pairs(planets)
    base_step_minutes = coarse_step_mins
    events: List[AspectEvent] = []
    prev_state: Dict[Tuple[str, str, str], Tuple[float, float]] = {}
    prev_time: Optional[datetime] = None
    prev_longitudes: Dict[str, float] = {}
    skipped_candidates: set[Tuple[str, str, str]] = set()

    earth = eph['earth']

    dt = start_dt
    while dt <= end_dt:
        t = to_timescale(ts, dt)
        longitudes: Dict[str, float] = {}
        for name, _glyph in planets:
            key = EPHEMERIS_NAME_MAP.get(name, name.lower())
            if key not in eph:
                continue
            astrometric = earth.at(t).observe(eph[key])
            lon = astrometric.apparent().ecliptic_latlon()[1].degrees
            longitudes[name] = wrap360(lon)

        planet_speeds: Dict[str, float] = {}
        max_relative_speed: Optional[float] = None
        if prev_time is not None and prev_longitudes:
            delta_hours = max((dt - prev_time).total_seconds() / 3600.0, 1e-6)
            for name, lon in longitudes.items():
                if name in prev_longitudes:
                    diff = signed_min_diff(lon, prev_longitudes[name])
                    planet_speeds[name] = abs(diff) / delta_hours
            for p1, p2 in pairs:
                if (
                    p1 in longitudes
                    and p2 in longitudes
                    and p1 in prev_longitudes
                    and p2 in prev_longitudes
                ):
                    prev_rel = wrap360(prev_longitudes[p2] - prev_longitudes[p1])
                    curr_rel = wrap360(longitudes[p2] - longitudes[p1])
                    rel_speed = _compute_relative_speed(prev_rel, curr_rel, delta_hours)
                    if max_relative_speed is None or rel_speed > max_relative_speed:
                        max_relative_speed = rel_speed
                    if timing_debug:
                        logging.debug(
                            "Relative speed %s-%s: %.3f°/hr over %.2f hr",
                            p1,
                            p2,
                            rel_speed,
                            delta_hours,
                        )

        if prev_time is not None:
            for p1, p2 in pairs:
                if p1 not in longitudes or p2 not in longitudes:
                    continue
                rel = wrap360(longitudes[p2] - longitudes[p1])
                for aspect_name, target_deg in aspect_degrees.items():
                    key = (p1, p2, aspect_name)
                    signed_diff = signed_min_diff(rel, target_deg)
                    abs_diff = abs(signed_diff)
                    prev_entry = prev_state.get(key)
                    if prev_entry is None:
                        prev_state[key] = (abs_diff, signed_diff)
                        continue

                    prev_abs, prev_signed = prev_entry
                    entered_orb = (prev_abs > orb) and (abs_diff <= orb)
                    sign_change = (prev_signed == 0) or (prev_signed < 0 < signed_diff) or (prev_signed > 0 > signed_diff)
                    turning_point = prev_abs <= abs_diff and prev_abs <= (orb * 3.0)
                    gate = min(prev_abs, abs_diff) <= (orb * 3.0)

                    if gate and (entered_orb or sign_change or turning_point):
                        refined_time, raw_sep, delta = refine_exact_time(
                            eph, ts, p1, p2, target_deg, prev_time, dt, refine_step_mins
                        )
                        boundary_hit = abs((refined_time - dt).total_seconds()) <= 1
                        if (
                            entered_orb
                            and not sign_change
                            and delta > (orb * 0.5)
                            and boundary_hit
                        ):
                            if timing_debug:
                                logging.debug(
                                    "Skipping entry candidate for %s-%s %s at %s Δ=%.6f (boundary)",
                                    p1,
                                    p2,
                                    aspect_name,
                                    refined_time.isoformat(),
                                    delta,
                                )
                            prev_state[key] = (abs_diff, signed_diff)
                            continue
                        if delta > orb + 1e-6:
                            key_warning = (p1, p2, aspect_name)
                            if timing_debug:
                                log_fn = logging.debug
                            else:
                                log_fn = None
                            if key_warning not in skipped_candidates:
                                skipped_candidates.add(key_warning)
                                if log_fn:
                                    log_fn(
                                        "Discarding %s-%s %s candidate Δ=%.6f outside orb %.6f",
                                        p1,
                                        p2,
                                        aspect_name,
                                        delta,
                                        orb,
                                    )
                            elif log_fn:
                                log_fn(
                                    "Discarding %s-%s %s candidate Δ=%.6f outside orb %.6f",
                                    p1,
                                    p2,
                                    aspect_name,
                                    delta,
                                    orb,
                                )
                            prev_state[key] = (abs_diff, signed_diff)
                            continue
                        retro1 = is_retrograde(
                            eph,
                            earth,
                            ts,
                            p1,
                            refined_time,
                            retrograde_probe_hours,
                            planet_speeds.get(p1),
                        )
                        retro2 = is_retrograde(
                            eph,
                            earth,
                            ts,
                            p2,
                            refined_time,
                            retrograde_probe_hours,
                            planet_speeds.get(p2),
                        )
                        events.append(
                            AspectEvent(
                                time=refined_time,
                                planet1=p1,
                                planet2=p2,
                                aspect=aspect_name,
                                exact_degrees=target_deg,
                                raw_separation=raw_sep,
                                delta=delta,
                                planet1_retrograde=retro1,
                                planet2_retrograde=retro2,
                            )
                        )
                        if timing_debug:
                            logging.debug(
                                "Detected %s-%s %s at %s Δ=%.6f (rel speed %.3f°/hr)",
                                p1,
                                p2,
                                aspect_name,
                                refined_time.isoformat(),
                                delta,
                                max_relative_speed or 0.0,
                            )

                    prev_state[key] = (abs_diff, signed_diff)
        else:
            for p1, p2 in pairs:
                if p1 not in longitudes or p2 not in longitudes:
                    continue
                rel = wrap360(longitudes[p2] - longitudes[p1])
                for aspect_name, target_deg in aspect_degrees.items():
                    abs_diff = minimal_abs_separation(rel, target_deg)
                    signed_diff = signed_min_diff(rel, target_deg)
                    prev_state[(p1, p2, aspect_name)] = (abs_diff, signed_diff)

        prev_time = dt
        prev_longitudes = longitudes

        if dt >= end_dt:
            break

        step_minutes = _adaptive_step_minutes(base_step_minutes, max_relative_speed)
        if timing_debug:
            logging.debug(
                "Advancing timeline from %s by %s minutes (max relative speed %.3f°/hr)",
                dt.isoformat(),
                step_minutes,
                (max_relative_speed or 0.0),
            )

        dt = dt + timedelta(minutes=step_minutes)

    merged = merge_aspect_events(events, merge_window_hours, timing_debug)
    return merged
