from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..aspect_detection import (
    AspectEvent,
    is_retrograde,
    merge_aspect_events,
    signed_min_diff,
    wrap360,
)
from ..constants import EPHEMERIS_NAME_MAP
from ..config import GeneratorConfig

# Tolerances and limits (aligned to docs/HelioNext/build)
TIME_TOLERANCE_SECONDS = 0.5
MAX_SOLVER_ITERS = 12
MIN_STEP_MINUTES = 5


def _pair_step_minutes(pair: Tuple[str, str], minor_enabled: bool, tertiary_enabled: bool) -> int:
    p1, p2 = pair
    if "Moon" in pair:
        return 5 if (minor_enabled or tertiary_enabled) else 15
    inner = {"Mercury", "Venus"}
    outers = {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}
    if p1 in inner or p2 in inner:
        return 30
    if p1 in outers and p2 in outers:
        return 240
    return 60


def _lon_at(
    eph,
    earth,
    ts,
    planet: str,
    dt: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    metrics: Dict[str, int],
) -> float:
    key = (planet, dt)
    if key in pos_cache:
        metrics["pos_cache_hits"] += 1
        return pos_cache[key]
    metrics["pos_cache_misses"] += 1
    eph_key = EPHEMERIS_NAME_MAP.get(planet, planet.lower())
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lon = earth.at(t).observe(eph[eph_key]).apparent().ecliptic_latlon()[1].degrees
    metrics["ephem_calls"] += 1
    lon_wrapped = wrap360(lon)
    pos_cache[key] = lon_wrapped
    return lon_wrapped


def _eval_rel(
    eph,
    earth,
    ts,
    planet1: str,
    planet2: str,
    dt: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    sep_cache: Dict[Tuple[str, str, datetime], float],
    metrics: Dict[str, int],
) -> float:
    key = (planet1, planet2, dt)
    if key in sep_cache:
        metrics["sep_cache_hits"] += 1
        return sep_cache[key]
    metrics["sep_cache_misses"] += 1
    lon1 = _lon_at(eph, earth, ts, planet1, dt, pos_cache, metrics)
    lon2 = _lon_at(eph, earth, ts, planet2, dt, pos_cache, metrics)
    rel = wrap360(lon2 - lon1)
    sep_cache[key] = rel
    return rel


def _refine_time(
    eph,
    earth,
    ts,
    planet1: str,
    planet2: str,
    target_deg: float,
    t0: datetime,
    t1: datetime,
    pos_cache: Dict[Tuple[str, datetime], float],
    sep_cache: Dict[Tuple[str, str, datetime], float],
    metrics: Dict[str, int],
) -> Tuple[datetime, float, float, int]:
    """Bracketed solver using bisection/secant hybrid on signed_min_diff."""

    def f(dt: datetime) -> Tuple[float, float]:
        rel = _eval_rel(eph, earth, ts, planet1, planet2, dt, pos_cache, sep_cache, metrics)
        val = signed_min_diff(rel, target_deg)
        return rel, val

    rel0, f0 = f(t0)
    rel1, f1 = f(t1)
    best_time, best_rel, best_delta = (t0, rel0, abs(f0)) if abs(f0) <= abs(f1) else (t1, rel1, abs(f1))

    left, right = (t0, t1) if t0 <= t1 else (t1, t0)

    iter_count = 0
    for _ in range(MAX_SOLVER_ITERS):
        iter_count += 1
        span = (right - left).total_seconds()
        if span <= TIME_TOLERANCE_SECONDS:
            break

        # Secant step when possible
        if f1 != f0:
            secant_offset = f1 * span / (f1 - f0)
            secant_time = right - timedelta(seconds=secant_offset)
        else:
            secant_time = left + timedelta(seconds=span / 2)

        rel_sec, f_sec = f(secant_time)
        if abs(f_sec) < best_delta:
            best_time, best_rel, best_delta = secant_time, rel_sec, abs(f_sec)

        # Bisection fallback
        mid = left + timedelta(seconds=span / 2)
        rel_mid, f_mid = f(mid)
        if abs(f_mid) < best_delta:
            best_time, best_rel, best_delta = mid, rel_mid, abs(f_mid)

        # Update bracket: prefer secant point if it flips sign; else use mid
        if f0 * f_sec <= 0:
            right, rel1, f1 = secant_time, rel_sec, f_sec
        elif f_sec * f1 <= 0:
            left, rel0, f0 = secant_time, rel_sec, f_sec
        elif f0 * f_mid <= 0:
            right, rel1, f1 = mid, rel_mid, f_mid
        else:
            left, rel0, f0 = mid, rel_mid, f_mid

    metrics["refine_iterations"] += iter_count
    metrics["refine_calls"] += 1
    # If we exited without reaching tolerance or no bracket sign change, count as failure/fallback
    if (right - left).total_seconds() > TIME_TOLERANCE_SECONDS:
        metrics["refine_failures"] += 1
        metrics["refine_failure_examples"] = metrics.get("refine_failure_examples", 0) + 1
    return best_time, best_rel, abs(signed_min_diff(best_rel, target_deg)), iter_count


def detect_aspects(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    config: GeneratorConfig,
    metrics_out: Optional[Dict[str, int]] = None,
) -> List[AspectEvent]:
    orb = config.orb
    aspect_degrees = config.aspect_degrees
    planets = config.planets
    if not aspect_degrees:
        logging.warning("No aspect degrees provided; detection will emit no events.")
        return []

    # Enable tighter steps if minor/tertiary are included
    minor_enabled = any(name not in {"Conjunction", "Opposition", "Trine", "Square", "Sextile"} for name in aspect_degrees)
    tertiary_enabled = minor_enabled  # treat same for stepping heuristics

    earth = eph['earth']
    events: List[AspectEvent] = []
    metrics: Dict[str, int] = {
        "ephem_calls": 0,
        "pos_cache_hits": 0,
        "pos_cache_misses": 0,
        "sep_cache_hits": 0,
        "sep_cache_misses": 0,
        "refine_calls": 0,
        "refine_iterations": 0,
        "refine_failures": 0,
        "skipped_out_of_orb": 0,
    }

    for p1_index in range(len(planets)):
        for p2_index in range(p1_index + 1, len(planets)):
            p1 = planets[p1_index][0]
            p2 = planets[p2_index][0]
            step_minutes = max(MIN_STEP_MINUTES, _pair_step_minutes((p1, p2), minor_enabled, tertiary_enabled))
            dt_prev = None
            rel_prev: Dict[str, Tuple[float, float]] = {}
            dt = start_dt
            pos_cache: Dict[Tuple[str, datetime], float] = {}
            sep_cache: Dict[Tuple[str, str, datetime], float] = {}
            while dt <= end_dt:
                rel = _eval_rel(eph, earth, ts, p1, p2, dt, pos_cache, sep_cache, metrics)
                for aspect_name, target_deg in aspect_degrees.items():
                    f_val = signed_min_diff(rel, target_deg)
                    abs_f = abs(f_val)
                    prev_entry = rel_prev.get(aspect_name)
                    if prev_entry is None:
                        rel_prev[aspect_name] = (abs_f, f_val)
                        continue

                    prev_abs, prev_f = prev_entry
                    entered_orb = prev_abs > orb and abs_f <= orb
                    sign_change = prev_f == 0 or (prev_f < 0 < f_val) or (prev_f > 0 > f_val)
                    turning_point = prev_abs <= abs_f and prev_abs <= (orb * 3.0)
                    gate = (min(prev_abs, abs_f) <= (orb * 3.0)) or sign_change
                    if gate and (entered_orb or sign_change or turning_point):
                        # Clamp bracket to window start to avoid emitting events before the requested range.
                        t0 = dt_prev if dt_prev is not None else dt - timedelta(minutes=step_minutes)
                        if t0 < start_dt:
                            t0 = start_dt
                        t1 = dt
                        refined_time, raw_sep, delta, _iters = _refine_time(
                            eph,
                            earth,
                            ts,
                            p1,
                            p2,
                            target_deg,
                            t0,
                            t1,
                            pos_cache,
                            sep_cache,
                            metrics,
                        )
                        if refined_time < start_dt or refined_time > end_dt:
                            if config.timing_debug:
                                logging.debug(
                                    "HelioNext skipping %s-%s %s at %s (out of window %s-%s)",
                                    p1,
                                    p2,
                                    aspect_name,
                                    refined_time.isoformat(),
                                    start_dt.isoformat(),
                                    end_dt.isoformat(),
                                )
                            rel_prev[aspect_name] = (abs_f, f_val)
                            continue
                        if delta > orb + 1e-6:
                            metrics["skipped_out_of_orb"] += 1
                            rel_prev[aspect_name] = (abs_f, f_val)
                            continue
                        retro1 = is_retrograde(
                            eph,
                            earth,
                            ts,
                            p1,
                            refined_time,
                            config.retrograde_probe_hours,
                        )
                        retro2 = is_retrograde(
                            eph,
                            earth,
                            ts,
                            p2,
                            refined_time,
                            config.retrograde_probe_hours,
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
                        if config.timing_debug:
                            logging.debug(
                                "HelioNext hit %s-%s %s at %s Δ=%.6f (step=%sm)",
                                p1,
                                p2,
                                aspect_name,
                                refined_time.isoformat(),
                                delta,
                                step_minutes,
                            )

                    rel_prev[aspect_name] = (abs_f, f_val)

                dt_prev = dt
                dt = dt + timedelta(minutes=step_minutes)

    # Apply per-pair merge window to collapse near-duplicates for the same aspect.
    merged_events = merge_aspect_events(events, config.merge_window_hours, config.timing_debug)
    if config.timing_debug:
        logging.debug("HelioNext merge collapsed %d -> %d", len(events), len(merged_events))
    events = merged_events

    events.sort(key=lambda e: e.time)
    if config.timing_debug:
        logging.debug(
            "HelioNext metrics: ephem=%d pos_hits=%d pos_miss=%d sep_hits=%d sep_miss=%d refine_calls=%d refine_iters=%d refine_failures=%d skipped_out_of_orb=%d",
            metrics["ephem_calls"],
            metrics["pos_cache_hits"],
            metrics["pos_cache_misses"],
            metrics["sep_cache_hits"],
            metrics["sep_cache_misses"],
            metrics["refine_calls"],
            metrics["refine_iterations"],
            metrics["refine_failures"],
            metrics["skipped_out_of_orb"],
        )
    if metrics_out is not None:
        metrics_out.update(metrics)
    return events
