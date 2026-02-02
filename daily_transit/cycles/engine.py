from __future__ import annotations

import json
import logging
import math
import sys
from datetime import datetime, timedelta
from time import perf_counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from daily_transit.config import GeneratorConfig
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.cache import BoundedCache
from daily_transit.cycles.dto import CycleEvent, cycle_sort_key
from daily_transit.cycles.distance import detect_distance_extrema
from daily_transit.cycles.ingress import detect_ingresses
from daily_transit.cycles.retro import detect_retro_and_stations
from daily_transit.cycles.synodic import detect_synodic_phases

logger = logging.getLogger(__name__)

CHUNK_OVERLAP_HOURS = 12


def _run_cycle_detectors(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    config: GeneratorConfig,
    cycle_config: CycleConfig,
    metrics: Dict[str, int],
    shared_pos_cache: Dict[Tuple[str, datetime], float],
    shared_sep_cache: Dict[Tuple[str, str, datetime, float], float],
    retro_padding_days: float,
) -> List[CycleEvent]:
    window_events: List[CycleEvent] = []

    stage_runtime = metrics.setdefault("stage_runtime_seconds", {})

    def _time_stage(name: str, fn):
        start = perf_counter()
        result = fn()
        stage_runtime[name] = stage_runtime.get(name, 0.0) + (perf_counter() - start)
        return result

    try:
        window_events.extend(
            _time_stage(
                "ingress",
                lambda: detect_ingresses(
                    eph,
                    ts,
                    start_dt,
                    end_dt,
                    config,
                    cycle_config,
                    metrics,
                    pos_cache=shared_pos_cache,
                    sep_cache=shared_sep_cache,
                ),
            )
        )
        window_events.extend(
            _time_stage(
                "synodic",
                lambda: detect_synodic_phases(
                    eph,
                    ts,
                    start_dt,
                    end_dt,
                    config,
                    cycle_config,
                    metrics,
                    pos_cache=shared_pos_cache,
                    sep_cache=shared_sep_cache,
                ),
            )
        )
        window_events.extend(
            _time_stage(
                "retro_station",
                lambda: detect_retro_and_stations(
                    eph,
                    ts,
                    start_dt - timedelta(days=retro_padding_days) if retro_padding_days > 0 else start_dt,
                    end_dt + timedelta(days=retro_padding_days) if retro_padding_days > 0 else end_dt,
                    config,
                    cycle_config,
                    metrics,
                    pos_cache=shared_pos_cache,
                ),
            )
        )
        window_events.extend(
            _time_stage(
                "distance_extrema",
                lambda: detect_distance_extrema(
                    eph,
                    ts,
                    start_dt,
                    end_dt,
                    config,
                    cycle_config,
                    metrics,
                ),
            )
        )
    except KeyError as exc:
        message = str(exc)
        if cycle_config.missing_body_policy == "skip":
            logger.warning("Skipping cycle detection: %s", message)
            skipped = metrics.setdefault("skipped_bodies", [])
            skipped.append(message)
            return []
        raise

    return window_events


def _dedupe_events(events: List[CycleEvent]) -> List[CycleEvent]:
    deduped: List[CycleEvent] = []
    seen = set()
    for ev in sorted(events, key=cycle_sort_key):
        key = (
            ev.event_type,
            ev.body,
            ev.body1,
            ev.body2,
            ev.sign,
            round(ev.phase_angle, 6) if ev.phase_angle is not None else None,
            ev.start_time_utc,
            ev.end_time_utc,
            ev.ayanamsa_mode,
            ev.retrograde,
            ev.station_direction,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(ev)
    return deduped


def _derive_ingress_spans(events: List[CycleEvent], window_start: datetime, window_end: datetime) -> List[CycleEvent]:
    spans: List[CycleEvent] = []
    by_body: Dict[str, List[CycleEvent]] = {}
    for ev in events:
        if ev.event_type != "ingress" or not ev.body:
            continue
        by_body.setdefault(ev.body, []).append(ev)

    for ingress_events in by_body.values():
        ingress_events.sort(key=lambda e: e.start_time_utc)
        for idx, ev in enumerate(ingress_events):
            next_start = ingress_events[idx + 1].start_time_utc if idx + 1 < len(ingress_events) else window_end
            span_start = max(ev.start_time_utc, window_start)
            span_end = min(next_start, window_end)
            if span_end <= span_start:
                continue
            next_sign = ingress_events[idx + 1].sign if idx + 1 < len(ingress_events) else None
            spans.append(
                CycleEvent(
                    event_type="ingress_span",
                    start_time_utc=span_start,
                    end_time_utc=span_end,
                    body=ev.body,
                    sign=ev.sign,
                    start_sign=ev.sign,
                    end_sign=next_sign,
                    ayanamsa_mode=ev.ayanamsa_mode,
                    source_engine=ev.source_engine,
                    schema_version=ev.schema_version,
                    merge_window_seconds=ev.merge_window_seconds,
                )
            )

    return spans


def _derive_synodic_phase_spans(events: List[CycleEvent], window_start: datetime, window_end: datetime) -> List[CycleEvent]:
    spans: List[CycleEvent] = []
    by_pair: Dict[Tuple[str, str], List[CycleEvent]] = {}

    for ev in events:
        if ev.event_type != "synodic_phase" or not ev.body1 or not ev.body2:
            continue
        by_pair.setdefault((ev.body1, ev.body2), []).append(ev)

    for phase_events in by_pair.values():
        phase_events.sort(key=lambda e: e.start_time_utc)
        if len(phase_events) < 2:
            continue
        unique_phases = {round(ev.phase_angle or 0.0, 6) for ev in phase_events if ev.phase_angle is not None}
        conjunction_only = len(unique_phases) == 1
        for idx, ev in enumerate(phase_events):
            next_ev = phase_events[idx + 1] if idx + 1 < len(phase_events) else None
            next_start = next_ev.start_time_utc if next_ev else window_end
            span_start = max(ev.start_time_utc, window_start)
            span_end = min(next_start, window_end)
            if span_end <= span_start:
                continue
            phase_start = ev.phase_angle if ev.phase_angle is not None else 0.0
            if conjunction_only:
                phase_end = phase_start + 360.0
            else:
                phase_end = (
                    next_ev.phase_angle
                    if next_ev and next_ev.phase_angle is not None
                    else phase_events[0].phase_angle if phase_events[0].phase_angle is not None else phase_start
                )
            spans.append(
                CycleEvent(
                    event_type="synodic_phase_span",
                    start_time_utc=span_start,
                    end_time_utc=span_end,
                    body1=ev.body1,
                    body2=ev.body2,
                    phase_angle=phase_start,
                    phase_start_deg=phase_start,
                    phase_end_deg=phase_end,
                    start_sign=ev.start_sign,
                    end_sign=next_ev.start_sign if next_ev else ev.start_sign,
                    ayanamsa_mode=ev.ayanamsa_mode,
                    source_engine=ev.source_engine,
                    schema_version=ev.schema_version,
                    merge_window_seconds=ev.merge_window_seconds,
                )
            )

    return spans


def _derive_span_events(events: List[CycleEvent], window_start: datetime, window_end: datetime) -> List[CycleEvent]:
    spans: List[CycleEvent] = []
    spans.extend(_derive_ingress_spans(events, window_start, window_end))
    spans.extend(_derive_synodic_phase_spans(events, window_start, window_end))
    return spans


def _merge_retro_intervals(events: List[CycleEvent]) -> List[CycleEvent]:
    merged: List[CycleEvent] = []
    retro_events = [ev for ev in events if ev.event_type == "retro_interval" and ev.body]
    retro_events.sort(key=lambda ev: (ev.body, ev.start_time_utc))
    idx = 0
    while idx < len(retro_events):
        current = retro_events[idx]
        start = current.start_time_utc
        end = current.end_time_utc or current.start_time_utc
        j = idx + 1
        while j < len(retro_events):
            nxt = retro_events[j]
            nxt_end = nxt.end_time_utc or nxt.start_time_utc
            if nxt.body != current.body:
                break
            if nxt.start_time_utc <= end:
                end = max(end, nxt_end)
                j += 1
                continue
            break
        merged.append(
            CycleEvent(
                event_type="retro_interval",
                start_time_utc=start,
                end_time_utc=end,
                body=current.body,
                retrograde=current.retrograde,
                ayanamsa_mode=current.ayanamsa_mode,
                source_engine=current.source_engine,
                schema_version=current.schema_version,
                merge_window_seconds=current.merge_window_seconds,
            )
        )
        idx = j

    if not merged:
        return events

    other = [ev for ev in events if ev.event_type != "retro_interval"]
    return other + merged


def _filter_events_to_window(
    events: List[CycleEvent],
    window_start: datetime,
    window_end: datetime,
    metrics: Dict[str, int],
    clamp_intervals: bool = False,
    timing_debug: bool = False,
) -> List[CycleEvent]:
    filtered: List[CycleEvent] = []
    drops = 0
    clamped = 0
    for ev in events:
        ev_end = ev.end_time_utc or ev.start_time_utc
        if ev.event_type == "retro_interval" and clamp_intervals:
            # If entirely outside, drop
            if ev_end < window_start or ev.start_time_utc > window_end:
                if timing_debug:
                    logger.info(
                        "Drop retro interval %s outside window [%s, %s] start=%s end=%s",
                        ev.body,
                        window_start.isoformat(),
                        window_end.isoformat(),
                        ev.start_time_utc.isoformat(),
                        ev_end.isoformat(),
                    )
                drops += 1
                continue
            new_start = max(ev.start_time_utc, window_start)
            new_end = min(ev_end, window_end)
            if new_end < new_start:
                if timing_debug:
                    logger.info(
                        "Drop retro interval %s inverted after clamp [%s, %s] start=%s end=%s",
                        ev.body,
                        window_start.isoformat(),
                        window_end.isoformat(),
                        new_start.isoformat(),
                        new_end.isoformat(),
                    )
                drops += 1
                continue
            if new_start != ev.start_time_utc or new_end != ev_end:
                orig_start = ev.start_time_utc
                orig_end = ev_end
                ev = CycleEvent(**{**ev.__dict__, "start_time_utc": new_start, "end_time_utc": new_end})
                clamped += 1
                if timing_debug:
                    logger.info(
                        "Clamp retro interval %s from [%s, %s] to [%s, %s] within [%s, %s]",
                        ev.body,
                        orig_start.isoformat(),
                        orig_end.isoformat(),
                        new_start.isoformat(),
                        new_end.isoformat(),
                        window_start.isoformat(),
                        window_end.isoformat(),
                    )
        else:
            # Keep anchor events even when they fall just outside the requested window;
            # they serve as out-of-window markers for pairs with no in-window hits.
            if ev.convergence_status == "anchor" and ev.event_type == "synodic_phase":
                filtered.append(ev)
                continue
            if ev.start_time_utc < window_start or ev_end > window_end:
                drops += 1
                continue
        filtered.append(ev)

    if drops:
        metrics["boundary_drops"] = metrics.get("boundary_drops", 0) + drops
    if clamped:
        metrics["boundary_clamped"] = metrics.get("boundary_clamped", 0) + clamped
    return filtered


def _format_progress_line(
    chunk_idx: int,
    chunk_total: int,
    chunk_start: datetime,
    chunk_end: datetime,
    percent: float,
    elapsed_seconds: float,
    ephem_calls: int,
    stage_deltas: Dict[str, float],
) -> str:
    stage_bits = []
    for name in ("ingress", "synodic", "retro_station", "distance_extrema"):
        val = stage_deltas.get(name)
        if val:
            stage_bits.append(f"{name}:{val:.1f}s")
    stage_txt = " " + " ".join(stage_bits) if stage_bits else ""
    return (
        f"[cycles] {chunk_idx}/{chunk_total} {chunk_start.date()}->{chunk_end.date()} "
        f"{percent:5.1f}% elapsed {elapsed_seconds/60:.1f}m ephem {ephem_calls}{stage_txt}"
    )


def detect_cycles(
    eph,
    ts,
    start_dt: datetime,
    end_dt: datetime,
    config: GeneratorConfig,
    metrics_out: Optional[Dict[str, int]] = None,
) -> List[CycleEvent]:
    cycle_config = config.cycle_config
    if cycle_config is None or cycle_config.engine == "off":
        return []

    metrics: Dict[str, int] = {
        "ephem_calls": 0,
        "pos_cache_hits": 0,
        "pos_cache_misses": 0,
        "refine_calls": 0,
        "refine_iterations": 0,
        "refine_failures": 0,
        "sep_cache_hits": 0,
        "sep_cache_misses": 0,
        "runtime_seconds": 0.0,
        "stage_runtime_seconds": {},
        "chunk_count": 0,
        "ephem_calls_by_body": {},
        "pos_cache_hits_by_body": {},
        "pos_cache_misses_by_body": {},
        "sep_cache_hits_by_pair": {},
        "sep_cache_misses_by_pair": {},
        "cycle_counts": {},
        "skipped_bodies": [],
        "boundary_drops": 0,
        "boundary_clamped": 0,
    }

    events: List[CycleEvent] = []
    shared_pos_cache: BoundedCache = BoundedCache(cycle_config.pos_cache_max_entries)
    shared_sep_cache: BoundedCache = BoundedCache(cycle_config.sep_cache_max_entries)

    chunk_span_days = cycle_config.chunk_span_days
    total_start = perf_counter()

    progress_enabled = bool(getattr(cycle_config, "cycle_progress", True))
    is_tty = sys.stdout.isatty()
    progress_enabled = progress_enabled and is_tty
    total_seconds_span = max(1.0, (end_dt - start_dt).total_seconds())
    chunk_idx = 0
    chunk_total = 1
    last_progress_len = 0
    if chunk_span_days is not None and chunk_span_days > 0:
        chunk_total = max(1, math.ceil((end_dt - start_dt).total_seconds() / (chunk_span_days * 86400.0)))

    if chunk_span_days is None or chunk_span_days <= 0:
        events.extend(
            _filter_events_to_window(
                _run_cycle_detectors(
                    eph,
                    ts,
                    start_dt,
                    end_dt,
                    config,
                    cycle_config,
                    metrics,
                    shared_pos_cache,
                    shared_sep_cache,
                    cycle_config.retro_padding_days or 0.0,
                ),
                start_dt,
                end_dt,
                metrics,
                clamp_intervals=bool(getattr(cycle_config, "clamp_intervals", False)),
                timing_debug=bool(getattr(cycle_config, "timing_debug", False)),
            )
        )
        metrics["chunk_count"] = metrics.get("chunk_count", 0) + 1
        chunk_idx = 1
        if progress_enabled:
            line = _format_progress_line(
                chunk_idx,
                chunk_total,
                start_dt,
                end_dt,
                100.0,
                perf_counter() - total_start,
                metrics.get("ephem_calls", 0),
                metrics.get("stage_runtime_seconds", {}),
            )
            pad = " " * max(0, last_progress_len - len(line))
            sys.stdout.write("\r" + line + pad)
            sys.stdout.flush()
            last_progress_len = len(line)
    else:
        chunk_delta = timedelta(days=chunk_span_days)
        overlap = timedelta(hours=CHUNK_OVERLAP_HOURS)
        cursor = start_dt
        while cursor <= end_dt:
            chunk_start = cursor
            chunk_end = min(chunk_start + chunk_delta, end_dt)
            metrics["chunk_count"] = metrics.get("chunk_count", 0) + 1
            chunk_idx += 1
            stage_before = dict(metrics.get("stage_runtime_seconds", {}))
            chunk_start_perf = perf_counter()
            events.extend(
                _filter_events_to_window(
                    _run_cycle_detectors(
                        eph,
                        ts,
                        chunk_start,
                        chunk_end,
                        config,
                        cycle_config,
                        metrics,
                        shared_pos_cache,
                        shared_sep_cache,
                        cycle_config.retro_padding_days or 0.0,
                    ),
                    chunk_start,
                    chunk_end,
                    metrics,
                    clamp_intervals=bool(getattr(cycle_config, "clamp_intervals", False)),
                    timing_debug=bool(getattr(cycle_config, "timing_debug", False)),
                )
            )

            if progress_enabled:
                stage_after = metrics.get("stage_runtime_seconds", {})
                deltas: Dict[str, float] = {}
                for key, val in stage_after.items():
                    prev = stage_before.get(key, 0.0)
                    delta = val - prev
                    if delta > 0:
                        deltas[key] = delta
                percent = min(100.0, ((chunk_end - start_dt).total_seconds() / total_seconds_span) * 100.0)
                elapsed = perf_counter() - total_start
                line = _format_progress_line(chunk_idx, chunk_total, chunk_start, chunk_end, percent, elapsed, metrics.get("ephem_calls", 0), deltas)
                pad = " " * max(0, last_progress_len - len(line))
                sys.stdout.write("\r" + line + pad)
                sys.stdout.flush()
                last_progress_len = len(line)

            if chunk_end >= end_dt:
                break

            next_cursor = chunk_end - overlap
            if next_cursor <= chunk_start:
                next_cursor = chunk_end
            cursor = next_cursor

    metrics["runtime_seconds"] = metrics.get("runtime_seconds", 0.0) + (perf_counter() - total_start)
    metrics["pos_cache_evictions"] = getattr(shared_pos_cache, "evictions", 0)
    metrics["sep_cache_evictions"] = getattr(shared_sep_cache, "evictions", 0)

    if progress_enabled and last_progress_len > 0:
        sys.stdout.write("\n")
        sys.stdout.flush()

    if cycle_config.timing_debug:
        logger.info(
            "Cycle metrics ephem=%d pos_hits=%d pos_miss=%d sep_hits=%d sep_miss=%d refine_calls=%d refine_iters=%d refine_failures=%d",
            metrics.get("ephem_calls", 0),
            metrics.get("pos_cache_hits", 0),
            metrics.get("pos_cache_misses", 0),
            metrics.get("sep_cache_hits", 0),
            metrics.get("sep_cache_misses", 0),
            metrics.get("refine_calls", 0),
            metrics.get("refine_iterations", 0),
            metrics.get("refine_failures", 0),
        )
        samples = metrics.get("refine_samples", [])
        for sample in samples:
            logger.info(
                "Slow refine kind=%s iter=%d span_s=%.1f label=%s",
                sample.get("kind", ""),
                sample.get("iter_count", 0),
                sample.get("span_seconds", 0.0),
                sample.get("label", ""),
            )

    events = _dedupe_events(events)

    if bool(getattr(cycle_config, "derive_spans", False)):
        span_events = _derive_span_events(events, start_dt, end_dt)
        if span_events:
            events = _dedupe_events(events + span_events)

    if bool(getattr(cycle_config, "clamp_intervals", False)):
        events = _merge_retro_intervals(events)

    counts: Dict[str, int] = {}
    for ev in events:
        counts[ev.event_type] = counts.get(ev.event_type, 0) + 1
    metrics["cycle_counts"] = counts

    metrics["config_snapshot"] = {
        "planets": [body for body, _glyph in config.planets],
        "cycle_types": cycle_config.cycle_types,
        "phase_angles": cycle_config.phase_angles,
        "ingress_signs": cycle_config.ingress_signs,
        "ayanamsa": cycle_config.ayanamsa or config.ayanamsa,
        "merge_window_hours": cycle_config.merge_window_hours,
        "chunk_span_days": cycle_config.chunk_span_days,
        "pos_cache_max_entries": cycle_config.pos_cache_max_entries,
        "sep_cache_max_entries": cycle_config.sep_cache_max_entries,
        "missing_body_policy": cycle_config.missing_body_policy,
        "retro_probe_hours": cycle_config.retro_probe_hours or config.retrograde_probe_hours,
        "retro_padding_days": cycle_config.retro_padding_days,
        "clamp_intervals": cycle_config.clamp_intervals,
        "derive_spans": cycle_config.derive_spans,
        "start_utc": start_dt.isoformat(),
        "end_utc": end_dt.isoformat(),
    }

    if metrics_out is not None:
        metrics_out.update(metrics)

    if cycle_config.metrics_path:
        _write_cycle_metrics(cycle_config.metrics_path, metrics)
        logger.info(
            "Cycle metrics summary runtime=%.2fs ephem=%d refine_calls=%d refine_failures=%d counts=%s path=%s",
            metrics.get("runtime_seconds", 0.0),
            metrics.get("ephem_calls", 0),
            metrics.get("refine_calls", 0),
            metrics.get("refine_failures", 0),
            metrics.get("cycle_counts", {}),
            cycle_config.metrics_path,
        )

    return events


def _write_cycle_metrics(path: str, metrics: Dict[str, int]):
    try:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(metrics, indent=2, sort_keys=True))
    except Exception as exc:
        logger.warning("Failed to write cycle metrics to %s: %s", path, exc)
