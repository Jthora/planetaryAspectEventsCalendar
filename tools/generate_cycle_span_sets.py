from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

SCRIPT_ROOT = Path(__file__).resolve().parent.parent
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from ics import Calendar

from daily_transit.ics_writer import fold_ical_lines, serialize_calendar

LOGGER = logging.getLogger(__name__)
DEFAULT_CYCLE_TYPES = "ingress,synodic_phase,retro_interval,station,perihelion_aphelion"
DEFAULT_PHASE_ANGLES = "0,90,180,270"
DEFAULT_PRODUCT_ID = "-//HelioNext Span Sets//EN"


def _parse_ratio(raw: str) -> Tuple[int, int, int]:
    try:
        parts = [int(p.strip()) for p in raw.split(",") if p.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid ratio '{raw}'; use comma-separated integers like 1,1,1") from exc
    if len(parts) != 3 or any(p <= 0 for p in parts):
        raise argparse.ArgumentTypeError(f"Invalid ratio '{raw}'; expected three positive integers, e.g. 1,1,1")
    return tuple(parts)  # type: ignore[return-value]


def parse_date(raw: str) -> datetime:
    return datetime.fromisoformat(raw)


def _to_utc(dt):
    if dt is None:
        return None
    if hasattr(dt, "to"):
        return dt.to("UTC").naive
    if hasattr(dt, "astimezone"):
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _is_span_event(ev) -> bool:
    categories = {c.lower() for c in (ev.categories or [])}
    name = (ev.name or "").lower()
    return "ingress_span" in categories or "synodic_phase_span" in categories or "span" in name


def _is_retro_interval(ev) -> bool:
    categories = {c.lower() for c in (ev.categories or [])}
    return "retro_interval" in categories


def _event_duration_days(ev) -> float:
    end = _to_utc(ev.end)
    start = _to_utc(ev.begin)
    if end is None or start is None:
        return 0.0
    delta = end - start
    return delta.total_seconds() / 86400.0


def _event_overlaps(ev, window_start: datetime, window_end: datetime) -> bool:
    start = _to_utc(ev.begin)
    end = _to_utc(ev.end) or start
    return start <= window_end and end >= window_start


def _write_ics(events: List, path: Path, product_id: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    ics_text = serialize_calendar(events, product_id)
    folded = fold_ical_lines(ics_text)
    path.write_text(folded)
    LOGGER.info("Wrote %d events to %s", len(events), path)


def _run_generator(
    start: datetime,
    end: datetime,
    output_path: Path,
    retro_padding_days: float,
    clamp_intervals: bool,
    derive_spans: bool,
    cycle_types: str,
    phase_angles: str,
    extra_args: Iterable[str] = (),
):
    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent.parent / "DailyTransitAspectCalendarGenerator.py"),
        "--cycle-engine",
        "helionext-cycles",
        "--cycle-types",
        cycle_types,
        "--cycle-phase-angles",
        phase_angles,
        "--cycle-retro-padding-days",
        str(retro_padding_days),
        "--start",
        start.date().isoformat(),
        "--end",
        end.date().isoformat(),
        "--output",
        str(output_path),
        "--skip-aspect-detection",
        "--no-aspects",
        "--cycle-derive-spans",
    ]
    if clamp_intervals:
        cmd.append("--cycle-clamp-intervals")
    cmd.extend(extra_args)
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Generate span-based ICS sets (long vs short)")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD for source generation")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD for source generation")
    parser.add_argument("--output-dir", default="output/span_sets", help="Root directory for generated ICS files")
    parser.add_argument("--long-threshold-days", type=float, default=120.0, help="Duration (days) at or above which spans/intervals go to long bucket (threshold mode)")
    parser.add_argument("--medium-threshold-days", type=float, default=30.0, help="Duration (days) at or above which spans/intervals go to medium bucket (threshold mode)")
    parser.add_argument("--retro-padding-days", type=float, default=30.0, help="Retro padding days for source generation")
    parser.add_argument("--slice-years", type=int, default=1, help="Year span per short-file slice (1=yearly, 5=five-year blocks)")
    parser.add_argument("--medium-slice-years", type=int, default=5, help="Year span per medium-file slice")
    parser.add_argument("--product-id", default=DEFAULT_PRODUCT_ID, help="ICS PRODID to embed")
    parser.add_argument("--cycle-types", default=DEFAULT_CYCLE_TYPES, help="Cycle types to request from generator")
    parser.add_argument("--cycle-phase-angles", default=DEFAULT_PHASE_ANGLES, help="Phase angles to request from generator")
    parser.add_argument("--base-ics", help="Optional pre-generated ICS to split (skip source generation)")
    parser.add_argument("--keep-base", action="store_true", help="Keep the combined source ICS on disk")
    parser.add_argument("--distribution-mode", choices=["threshold", "quantile"], default="threshold", help="Bucket strategy: threshold (default) or quantile to even out counts")
    parser.add_argument("--target-ratio", type=_parse_ratio, default=(1, 1, 1), help="Comma-separated long,medium,short ratio used in quantile mode, e.g. 1,1,1")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(asctime)s - %(levelname)s - %(message)s")

    start_dt = parse_date(args.start)
    end_dt = parse_date(args.end)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    base_ics_path = Path(args.base_ics) if args.base_ics else output_root / "base_combined.ics"

    if not args.base_ics:
        LOGGER.info("Generating combined ICS for %s to %s", start_dt.date(), end_dt.date())
        _run_generator(
            start_dt,
            end_dt,
            base_ics_path,
            retro_padding_days=args.retro_padding_days,
            clamp_intervals=True,
            derive_spans=True,
            cycle_types=args.cycle_types,
            phase_angles=args.cycle_phase_angles,
        )

    LOGGER.info("Loading source ICS: %s", base_ics_path)
    cal = Calendar(base_ics_path.read_text())
    events = list(cal.events)
    LOGGER.info("Loaded %d events", len(events))

    long_events: List = []
    medium_events: List = []
    short_events: List = []

    if args.distribution_mode == "threshold":
        long_threshold = args.long_threshold_days
        medium_threshold = args.medium_threshold_days
        if medium_threshold >= long_threshold:
            LOGGER.warning(
                "medium-threshold-days (%.1f) >= long-threshold-days (%.1f); adjusting medium to long-1 day",
                medium_threshold,
                long_threshold,
            )
            medium_threshold = max(0.0, long_threshold - 1)

        for ev in events:
            duration_days = _event_duration_days(ev)
            if (_is_span_event(ev) or _is_retro_interval(ev)) and duration_days >= long_threshold:
                long_events.append(ev)
            elif (_is_span_event(ev) or _is_retro_interval(ev)) and duration_days >= medium_threshold:
                medium_events.append(ev)
            else:
                short_events.append(ev)
    else:
        ratio_long, ratio_medium, ratio_short = args.target_ratio
        total_weight = ratio_long + ratio_medium + ratio_short
        total_events = len(events)
        if total_weight <= 0 or total_events == 0:
            LOGGER.warning("No events or invalid ratio; skipping quantile distribution")
            short_events = events
        else:
            raw_targets = [
                (total_events * ratio_long) / total_weight,
                (total_events * ratio_medium) / total_weight,
                (total_events * ratio_short) / total_weight,
            ]
            base_targets = [int(x) for x in raw_targets]
            remainder = total_events - sum(base_targets)
            # Distribute remainder to buckets with largest fractional parts.
            fractional_order = sorted(
                enumerate([x - base for x, base in zip(raw_targets, base_targets)]), key=lambda item: item[1], reverse=True
            )
            for idx, _ in fractional_order:
                if remainder <= 0:
                    break
                base_targets[idx] += 1
                remainder -= 1

            durations = sorted((( _event_duration_days(ev), ev) for ev in events), key=lambda t: t[0], reverse=True)
            long_count, medium_count, _ = base_targets
            long_events = [ev for _, ev in durations[:long_count]]
            medium_events = [ev for _, ev in durations[long_count : long_count + medium_count]]
            short_events = [ev for _, ev in durations[long_count + medium_count :]]
            LOGGER.info(
                "Quantile mode targets=%s assigned long=%d medium=%d short=%d (total=%d)",
                base_targets,
                len(long_events),
                len(medium_events),
                len(short_events),
                total_events,
            )

    long_path = output_root / "long_spans.ics"
    _write_ics(long_events, long_path, args.product_id)

    medium_slice_years = max(1, args.medium_slice_years)
    current = start_dt
    while current <= end_dt:
        slice_start = datetime(current.year, current.month, current.day)
        slice_end_year = min(current.year + medium_slice_years - 1, end_dt.year)
        slice_end = datetime(slice_end_year, 12, 31, 23, 59, 59)
        slice_events = [ev for ev in medium_events if _event_overlaps(ev, slice_start, slice_end)]
        label = f"{slice_start.year}-{slice_end_year}" if medium_slice_years > 1 else f"{slice_start.year}"
        slice_path = output_root / f"medium_spans_{label}.ics"
        _write_ics(slice_events, slice_path, args.product_id)
        next_year = current.year + medium_slice_years
        current = datetime(next_year, 1, 1)

    slice_years = max(1, args.slice_years)
    current = start_dt
    while current <= end_dt:
        slice_start = datetime(current.year, current.month, current.day)
        slice_end_year = min(current.year + slice_years - 1, end_dt.year)
        slice_end = datetime(slice_end_year, 12, 31, 23, 59, 59)
        slice_events = [ev for ev in short_events if _event_overlaps(ev, slice_start, slice_end)]
        label = f"{slice_start.year}-{slice_end_year}" if slice_years > 1 else f"{slice_start.year}"
        slice_path = output_root / f"short_spans_{label}.ics"
        _write_ics(slice_events, slice_path, args.product_id)
        next_year = current.year + slice_years
        current = datetime(next_year, 1, 1)

    if not args.keep_base and not args.base_ics:
        try:
            base_ics_path.unlink()
        except OSError:
            pass


if __name__ == "__main__":
    main()
