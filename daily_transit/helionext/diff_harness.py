from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from daily_transit.engine_factory import get_detection_engine
from daily_transit.aspect_detection import detect_aspects as legacy_detect, AspectEvent
from daily_transit.aspect_detection import wrap360, signed_min_diff
from daily_transit.config import GeneratorConfig
from daily_transit.constants import EPHEMERIS_NAME_MAP


def _event_key(ev: AspectEvent) -> Tuple[str, str, str]:
    bodies = tuple(sorted([ev.planet1, ev.planet2]))
    return (ev.aspect, bodies[0], bodies[1])


def _to_serializable(ev: AspectEvent) -> Dict:
    d = asdict(ev)
    d["time_iso"] = ev.time.isoformat()
    d["time"] = ev.time.isoformat()
    d["planet1_retrograde"] = bool(ev.planet1_retrograde)
    d["planet2_retrograde"] = bool(ev.planet2_retrograde)
    return d


def _lon_at(eph, ts, planet: str, dt: datetime) -> float:
    key = EPHEMERIS_NAME_MAP.get(planet, planet.lower())
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    lon = eph['earth'].at(t).observe(eph[key]).apparent().ecliptic_latlon()[1].degrees
    return wrap360(lon)


def _is_station(
    eph,
    ts,
    planet: str,
    dt: datetime,
    window_hours: float = 12.0,
    epsilon_deg_per_day: float = 0.01,
) -> bool:
    """Approximate station: low speed and sign change over a window.

    Velocity is approximated using position differences before/after the window.
    """
    if eph is None or ts is None:
        return False
    delta = timedelta(hours=window_hours)
    before = dt - delta
    after = dt + delta
    lon_before = _lon_at(eph, ts, planet, before)
    lon_now = _lon_at(eph, ts, planet, dt)
    lon_after = _lon_at(eph, ts, planet, after)

    rate1 = signed_min_diff(lon_now, lon_before) / window_hours  # deg/hour
    rate2 = signed_min_diff(lon_after, lon_now) / window_hours  # deg/hour
    rate1_dpd = abs(rate1 * 24.0)
    near_zero = rate1_dpd <= epsilon_deg_per_day
    sign_change = rate1 == 0 or rate2 == 0 or (rate1 < 0 < rate2) or (rate1 > 0 > rate2)
    return near_zero and sign_change


def run_dual(
    config: GeneratorConfig,
    eph,
    ts,
    detection_end: datetime,
    time_tolerance_s: float = 2.0,
    delta_tolerance_deg: float = 0.005,
) -> Dict:
    legacy_start = time.perf_counter()
    legacy_events = legacy_detect(
        eph,
        ts,
        config.start_date,
        detection_end,
        config.orb,
        config.aspect_degrees,
        config.planets,
        config.coarse_step_mins,
        config.refine_step_mins,
        config.merge_window_hours,
        config.retrograde_probe_hours,
        timing_debug=False,
    )
    legacy_runtime_s = time.perf_counter() - legacy_start
    helio_engine = get_detection_engine("helionext")
    helio_start = time.perf_counter()
    helio_events = helio_engine.detect(eph, ts, config, detection_end)
    helio_runtime_s = time.perf_counter() - helio_start

    legacy_map: Dict[Tuple[str, str, str], List[AspectEvent]] = {}
    for ev in legacy_events:
        legacy_map.setdefault(_event_key(ev), []).append(ev)

    helio_map: Dict[Tuple[str, str, str], List[AspectEvent]] = {}
    for ev in helio_events:
        helio_map.setdefault(_event_key(ev), []).append(ev)

    matches: List[Dict] = []
    missing: List[Dict] = []
    extra: List[Dict] = []
    mismatches: List[Dict] = []
    max_time_delta = 0.0

    all_keys = set(legacy_map.keys()) | set(helio_map.keys())

    for key in all_keys:
        legacy_list = list(legacy_map.get(key, []))
        helio_list = helio_map.get(key, [])

        if not legacy_list and helio_list:
            for ev in helio_list:
                extra.append(_to_serializable(ev))
            continue

        if legacy_list and not helio_list:
            for ev in legacy_list:
                missing.append(_to_serializable(ev))
            continue

        # Greedy pairing: consume the closest legacy event for each helionext event.
        unmatched_legacy = legacy_list[:]
        for ev in helio_list:
            if not unmatched_legacy:
                extra.append(_to_serializable(ev))
                continue

            # Find the closest legacy event by time.
            closest_idx = 0
            closest_delta = abs((unmatched_legacy[0].time - ev.time).total_seconds())
            for idx in range(1, len(unmatched_legacy)):
                candidate_delta = abs((unmatched_legacy[idx].time - ev.time).total_seconds())
                if candidate_delta < closest_delta:
                    closest_delta = candidate_delta
                    closest_idx = idx

            legacy_ev = unmatched_legacy.pop(closest_idx)

            legacy_station = [
                bool(_is_station(eph, ts, legacy_ev.planet1, legacy_ev.time)),
                bool(_is_station(eph, ts, legacy_ev.planet2, legacy_ev.time)),
            ]
            helio_station = [
                bool(_is_station(eph, ts, ev.planet1, ev.time)),
                bool(_is_station(eph, ts, ev.planet2, ev.time)),
            ]
            delta_s = abs((legacy_ev.time - ev.time).total_seconds())
            max_time_delta = max(max_time_delta, delta_s)
            legacy_retro = [bool(legacy_ev.planet1_retrograde), bool(legacy_ev.planet2_retrograde)]
            helio_retro = [bool(ev.planet1_retrograde), bool(ev.planet2_retrograde)]
            delta_deg_diff = abs(legacy_ev.delta - ev.delta)
            within_time = delta_s <= time_tolerance_s
            retro_match = legacy_retro == helio_retro
            within_delta = delta_deg_diff <= delta_tolerance_deg
            station_match = legacy_station == helio_station

            if within_time and retro_match and within_delta and station_match:
                matches.append(_to_serializable(ev))
            else:
                reason = "time_delta"
                if within_time is False:
                    reason = "time_delta"
                elif retro_match is False:
                    reason = "retro_flag"
                elif station_match is False:
                    reason = "station_flag"
                elif within_delta is False:
                    reason = "delta_deg"

                mismatches.append(
                    {
                        "aspect": ev.aspect,
                        "bodies": [ev.planet1, ev.planet2],
                        "legacy_time": legacy_ev.time.isoformat(),
                        "helionext_time": ev.time.isoformat(),
                        "delta_time_s": delta_s,
                        "legacy_delta_deg": legacy_ev.delta,
                        "helionext_delta_deg": ev.delta,
                        "delta_deg_diff": delta_deg_diff,
                        "legacy_retro": legacy_retro,
                        "helionext_retro": helio_retro,
                        "legacy_station": legacy_station,
                        "helionext_station": helio_station,
                        "reason": reason,
                    }
                )

        # Any remaining legacy events were not paired.
        for ev in unmatched_legacy:
            missing.append(_to_serializable(ev))

    reason_counts: Dict[str, int] = {}
    for m in mismatches:
        reason = m.get("reason", "unknown")
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    return {
        "matches": matches,
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "reason_counts": reason_counts,
        "max_time_delta_s": max_time_delta,
        "legacy_count": len(legacy_events),
        "helionext_count": len(helio_events),
        "time_tolerance_s": time_tolerance_s,
        "delta_tolerance_deg": delta_tolerance_deg,
        "legacy_runtime_s": legacy_runtime_s,
        "helionext_runtime_s": helio_runtime_s,
    }


def write_reports(report: Dict, base_path: str):
    with open(f"{base_path}_report.json", "w") as f:
        json.dump(report, f, indent=2)
