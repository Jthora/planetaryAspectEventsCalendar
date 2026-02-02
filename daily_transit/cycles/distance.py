from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from daily_transit.constants import EPHEMERIS_NAME_MAP
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent, cycle_sort_key
from daily_transit.cycles.refine_metrics import record_refine_sample
from daily_transit.config import GeneratorConfig

TIME_TOLERANCE_SECONDS = 5.0
MAX_REFINEMENT_ITERS = 18

logger = logging.getLogger(__name__)


class DistanceUnavailable(Exception):
    pass


def _distance_au(eph, ts, earth, body: str, dt: datetime) -> float:
    eph_key = EPHEMERIS_NAME_MAP.get(body, body.lower())
    if eph_key not in eph:
        raise DistanceUnavailable(f"Ephemeris missing body {body}")
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return earth.at(t).observe(eph[eph_key]).apparent().distance().au


def _handle_missing_body(body: str, policy: str, metrics: Dict[str, int]) -> str:
    if policy == "skip":
        metrics["distance_skipped_missing"] = metrics.get("distance_skipped_missing", 0) + 1
        logger.warning("Skipping distance extrema for missing body %s", body)
        return "skip"
    raise KeyError(f"Ephemeris missing body {body}")


def _refine_extremum(
    eph,
    ts,
    earth,
    body: str,
    left: datetime,
    right: datetime,
    *,
    find_min: bool,
) -> Tuple[datetime, float, int, float]:
    l, r = (left, right) if left <= right else (right, left)
    best_dt = l
    best_val = _distance_au(eph, ts, earth, body, l)
    iter_count = 0

    for _ in range(MAX_REFINEMENT_ITERS):
        iter_count += 1
        span = (r - l).total_seconds()
        if span <= TIME_TOLERANCE_SECONDS:
            break
        mid = l + timedelta(seconds=span / 2)
        val_mid = _distance_au(eph, ts, earth, body, mid)
        val_r = _distance_au(eph, ts, earth, body, r)

        if (find_min and val_mid < best_val) or (not find_min and val_mid > best_val):
            best_val = val_mid
            best_dt = mid

        if find_min:
            if val_mid <= val_r:
                r = mid
            else:
                l = mid
        else:
            if val_mid >= val_r:
                r = mid
            else:
                l = mid

    residual_span = abs((r - l).total_seconds())
    return best_dt, best_val, iter_count, residual_span


def detect_distance_extrema(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    generator_config: GeneratorConfig,
    cycle_config: CycleConfig,
    metrics: Dict[str, int],
) -> List[CycleEvent]:
    if not cycle_config.cycle_types or not {"perihelion_aphelion"} & set(cycle_config.cycle_types):
        return []

    merge_window_seconds = cycle_config.merge_window_hours * 3600.0 if cycle_config.merge_window_hours else None
    policy = cycle_config.missing_body_policy or "fail"
    events: List[CycleEvent] = []
    earth = eph["earth"]

    for body, _glyph in generator_config.planets:
        try:
            _distance_au(eph, ts, earth, body, start_dt)
        except DistanceUnavailable:
            if _handle_missing_body(body, policy, metrics) == "skip":
                continue

        # Coarse scan: sample daily to find potential minima/maxima
        coarse_dt = start_dt
        coarse_samples: List[Tuple[datetime, float]] = []
        while coarse_dt <= end_dt:
            try:
                val = _distance_au(eph, ts, earth, body, coarse_dt)
                coarse_samples.append((coarse_dt, val))
            except DistanceUnavailable:
                if _handle_missing_body(body, policy, metrics) == "skip":
                    coarse_samples = []
                    break
                raise
            coarse_dt += timedelta(days=1)

        for idx in range(1, len(coarse_samples) - 1):
            prev_dt, prev_val = coarse_samples[idx - 1]
            curr_dt, curr_val = coarse_samples[idx]
            next_dt, next_val = coarse_samples[idx + 1]

            # Detect local minima/maxima
            if prev_val >= curr_val <= next_val:
                find_min = True
            elif prev_val <= curr_val >= next_val:
                find_min = False
            else:
                continue

            try:
                refined_dt, refined_val, iter_count, residual_span = _refine_extremum(
                    eph,
                    ts,
                    earth,
                    body,
                    prev_dt,
                    next_dt,
                    find_min=find_min,
                )
                metrics["refine_calls"] = metrics.get("refine_calls", 0) + 1
                metrics["refine_iterations"] = metrics.get("refine_iterations", 0) + iter_count
                record_refine_sample(
                    metrics,
                    {
                        "kind": "distance_extremum",
                        "body": body,
                        "iter_count": iter_count,
                        "span_seconds": residual_span,
                        "label": f"{body} {'min' if find_min else 'max'}",
                    },
                    cycle_config.timing_debug,
                )
                convergence_status = "ok"
                uncertainty_seconds = residual_span / 2.0 if residual_span > TIME_TOLERANCE_SECONDS else None
            except Exception:
                refined_dt = curr_dt
                refined_val = curr_val
                metrics["refine_failures"] = metrics.get("refine_failures", 0) + 1
                convergence_status = "fallback"
                uncertainty_seconds = abs((next_dt - prev_dt).total_seconds()) / 2.0

            events.append(
                CycleEvent(
                    event_type="perihelion" if find_min else "aphelion",
                    body=body,
                    start_time_utc=refined_dt,
                    end_time_utc=refined_dt,
                    distance_au=refined_val,
                    ayanamsa_mode=cycle_config.ayanamsa or generator_config.ayanamsa,
                    source_engine=cycle_config.engine,
                    merge_window_seconds=merge_window_seconds,
                    convergence_status=convergence_status,
                    uncertainty_seconds=uncertainty_seconds,
                )
            )

    events.sort(key=cycle_sort_key)
    return events
