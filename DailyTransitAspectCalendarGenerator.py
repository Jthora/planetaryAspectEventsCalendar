"""
DailyTransitAspectCalendarGenerator
----------------------------------
Generates an ICS calendar containing:
  1. Exact planetary aspect events (tropical ecliptic, no ayanamsa correction).
  2. A daily transit chart summary event (00:00 UTC or user timezone) listing planetary positions and aspects occurring that day.

Foundations borrowed from existing project scripts:
  - Ephemeris + zodiac logic pattern:   LunarPhaseEventsCalendarGenerator.py
  - Aspect degree definitions:          astrological_dictionaries.astrological_aspects
  - ICS event construction style:       astrologicalCsvToIcsParser.py (adapted to ics library usage for consistency)
  - CLI + logging style:                filter_ics_by_year.py

Usage example:
  python DailyTransitAspectCalendarGenerator.py \
      --start 2025-01-01 --end 2025-01-07 \
      --output transit_aspects_2025w1.ics \
      --orb 1.5 --timezone UTC

Features:
  - Configurable orb (degrees) applied uniformly to all aspects.
  - Linear refinement of exact times within an hour window (and 5‑minute sub-steps) for better timing precision.
  - Daily event includes: formatted planetary positions, list of exact aspects that day with interpretations.
  - Aspect interpretation: pulls short meaning from dictionaries if available; falls back gracefully.
  - Supports major + selected minor aspects (configurable via --aspects scope: major|all).
    - Thunderbird friendly mode adds deterministic UID, CREATED, LAST-MODIFIED, STATUS (via --thunderbird-friendly / --status).

Limitations / Future Enhancements:
  - Currently uses a simple hourly scan; could be improved by root-finding per aspect pair for higher precision.
  - Moon moves fast; residual timing error after refinement typically < ~2 minutes but not guaranteed for extreme cases.
  - No graphical chart output (text only).
  - Does not yet include retrograde flags or house positions.
  - Does not yet fold long iCal lines (most clients handle; can add if needed).
"""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timedelta
from time import perf_counter
from typing import Dict, List, Optional, Tuple

import pytz
from skyfield.api import load_file, load

try:
    from astrological_dictionaries import astrological_aspects
except ImportError:  # Fallback minimal definition if the large dictionary file is absent
    astrological_aspects = {
        "aspect_degrees": {
            "Conjunction": 0.0,
            "Opposition": 180.0,
            "Trine": 120.0,
            "Square": 90.0,
            "Sextile": 60.0,
            "Quincunx": 150.0,
            "Semisextile": 30.0,
            "Semisquare": 45.0,
            "Sesquiquadrate": 135.0,
        },
        "aspect_meanings": {
            "Conjunction": "Fusion / concentrated focus of energies.",
            "Opposition": "Polarity seeking balance / awareness.",
            "Trine": "Ease, flow, supportive harmony.",
            "Square": "Dynamic tension prompting action.",
            "Sextile": "Opportunity requiring conscious activation.",
            "Quincunx": "Adjustment, reconfiguration of unrelated areas.",
            "Semisextile": "Subtle friction / mild adjustment.",
            "Semisquare": "Minor internal tension motivating tweaks.",
            "Sesquiquadrate": "Frictive follow‑up tension pushing refinement.",
        }
    }

from daily_transit.aspect_catalog import select_scope as select_catalog_scope
from daily_transit.aspect_detection import AspectEvent
from daily_transit.config import GeneratorConfig
from daily_transit.cli_args import parse_args, _validate_location_args, _warn_compact_daily_summary
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.engine_factory import get_cycle_detection_engine
from daily_transit.cycles.cli import build_cycle_config_from_args
from daily_transit.cycles.ics_builder import build_cycle_events
from daily_transit.constants import DEFAULT_PLANETS, EPHEMERIS_NAME_MAP
from daily_transit.ephemeris_validation import (
    build_body_coverage_index,
    validate_range_within_coverage,
)
from daily_transit.engine_factory import get_detection_engine
from daily_transit.ayanamsa import get_ayanamsa_offset
from daily_transit.houses import assign_houses
from daily_transit.ics_builder import (
    build_aspect_event,
    build_compact_aspect_event,
    build_daily_summary,
    build_lunar_phase_event,
    compute_body_longitudes,
)
from daily_transit.runtime import run_detection, build_events, write_calendar


def _format_hms(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours}h {minutes:02d}m {secs:02d}s"


def setup_logging(log_path: str, verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


from daily_transit.cli_args import parse_args, _validate_location_args, _warn_compact_daily_summary




def _event_priority(event) -> int:
    categories = {c for c in (event.categories or [])}
    if 'Daily Transit' in categories:
        return 0
    if 'Lunar Phase' in categories:
        return 1
    return 2


def _event_sort_key(event):
    priority = _event_priority(event)
    begin_dt = None
    if event.begin:
        try:
            begin_dt = event.begin.datetime
        except AttributeError:
            begin_dt = None
        except Exception:
            begin_dt = None
    timestamp = begin_dt.timestamp() if begin_dt else float('inf')
    return (
        priority,
        timestamp,
        event.name or '',
        event.uid or '',
    )


def load_ephemeris(ephemeris_path: str):
    try:
        return load_file(ephemeris_path)
    except FileNotFoundError as e:
        logging.error(f"Ephemeris file not found: {ephemeris_path}")
        raise


def select_aspects(scope: str) -> Dict[str, float]:
    catalog = select_catalog_scope(scope)
    if catalog is not None:
        return catalog

    all_aspects = astrological_aspects.get('aspect_degrees', {})
    if scope == 'major':
        keep = {k: v for k, v in all_aspects.items() if k in {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}}
        return keep
    if scope in {'all', 'complete'}:
        return all_aspects
    raise SystemExit(f"Unsupported aspect scope: {scope}")


def build_config_from_args(
    args: argparse.Namespace,
    aspect_degrees: Dict[str, float],
    planets: List[Tuple[str, str]],
    timezone: pytz.BaseTzInfo,
    *,
    start_date: datetime,
    end_date: datetime,
) -> GeneratorConfig:
    """Assemble GeneratorConfig from parsed CLI args."""
    return GeneratorConfig(
        start_date=start_date,
        end_date=end_date,
        timezone=timezone,
        orb=args.orb,
        aspect_degrees=aspect_degrees,
        planets=planets,
        coarse_step_mins=args.coarse_step_mins,
        refine_step_mins=args.refine_step_mins,
        merge_window_hours=args.merge_window_hours,
        inclusive_end=args.inclusive_end,
        status=args.status,
        thunderbird_friendly=args.thunderbird_friendly,
        product_id=args.product_id,
        verbose=args.verbose,
        ascii_only=args.ascii_only,
        retrograde_probe_hours=args.retrograde_probe_hours,
        include_lunar_phases=args.lunar_phases,
        timing_debug=args.timing_debug,
        interpretation_mode=args.interpretation_mode,
        engine=args.engine,
        engine_factory=get_detection_engine,
        mode=args.mode,
        ayanamsa=args.ayanamsa,
        latitude=args.lat,
        longitude=args.lon,
        elevation_m=args.elev,
        precision_deg=args.precision_deg,
        precision_time=args.precision_time,
        cycle_config=build_cycle_config_from_args(args),
        aspect_meanings=astrological_aspects.get('aspect_meanings', {}),
        args=args,
        build_cycle_events=build_cycle_events,
        event_sort_key=_event_sort_key,
        compute_body_longitudes_fn=compute_body_longitudes,
        assign_houses_fn=assign_houses,
    )


def main():
    start_total = perf_counter()
    args = parse_args()
    _validate_location_args(args)
    _warn_compact_daily_summary(args)
    setup_logging(args.log, args.verbose)

    try:
        start_date = datetime.strptime(args.start, '%Y-%m-%d')
        end_date = datetime.strptime(args.end, '%Y-%m-%d')
    except ValueError:
        raise SystemExit("Invalid date format. Use YYYY-MM-DD.")
    if end_date < start_date:
        raise SystemExit("End date must be >= start date.")

    tz = pytz.timezone(args.timezone)

    try:
        eph = load_ephemeris(args.ephemeris)
    except FileNotFoundError:
        print(f"Ephemeris file '{args.ephemeris}' not found.")
        return
    ts = load.timescale()

    available_planets: List[Tuple[str, str]] = []
    missing_planets: List[str] = []
    for name, glyph in DEFAULT_PLANETS:
        key = EPHEMERIS_NAME_MAP.get(name, name.lower())
        if key in eph:
            available_planets.append((name, glyph))
        else:
            missing_planets.append(name)
    outer_missing = [name for name in missing_planets if name in {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"}]
    if outer_missing:
        logging.warning(
            "Ephemeris '%s' omits outer planet data for: %s. Consider downloading a full kernel such as 'de441.bsp' for complete support.",
            args.ephemeris,
            ", ".join(outer_missing),
        )
    if args.planets:
        requested = [token.strip() for token in args.planets.split(',') if token.strip()]
        available_lookup = {name.lower(): (name, glyph) for name, glyph in available_planets}
        active_planets: List[Tuple[str, str]] = []
        missing_requested = [item for item in requested if item.lower() not in available_lookup]
        if missing_requested:
            message = (
                "Planet(s) "
                + ", ".join(missing_requested)
                + f" unavailable in ephemeris '{args.ephemeris}'. "
                "Fetch a more complete SPK kernel (e.g., de441.bsp) for outer planet coverage."
            )
            logging.error(message)
            raise SystemExit(message)
        for item in requested:
            key = item.lower()
            planet_tuple = available_lookup[key]
            if any(p[0].lower() == planet_tuple[0].lower() for p in active_planets):
                continue
            active_planets.append(planet_tuple)
        if not active_planets:
            raise SystemExit("No valid planets selected after filtering.")
    else:
        active_planets = available_planets
    if not active_planets:
        raise SystemExit("No supported planets found in ephemeris.")
    aspect_degrees = select_aspects(args.aspects)
    if not aspect_degrees:
        raise SystemExit("No aspects selected; aborting.")

    config = build_config_from_args(
        args,
        aspect_degrees,
        active_planets,
        tz,
        start_date=start_date,
        end_date=end_date,
    )

    detection_end = config.end_date + timedelta(days=1)

    coverage_keys = {EPHEMERIS_NAME_MAP.get(name, name.lower()) for name, _glyph in active_planets}
    coverage_keys.add("earth")
    label_by_key = {EPHEMERIS_NAME_MAP.get(name, name.lower()): name for name, _glyph in active_planets}
    label_by_key["earth"] = "Earth"

    coverage_index = build_body_coverage_index(eph, ts, coverage_keys)
    validate_range_within_coverage(coverage_index, config.start_date, detection_end, label_by_key=label_by_key)

    aspects, cycle_events = run_detection(eph, ts, config, detection_end)
    detect_elapsed = perf_counter() - start_total
    logging.debug(
        "Detection elapsed: %.2fs (coarse=%s min, refine=%s min, merge_window=%.1fh)",
        detect_elapsed,
        config.coarse_step_mins,
        config.refine_step_mins,
        config.merge_window_hours,
    )

    collected_events: List = []
    zodiac_context_cache: Dict[datetime, Dict[str, PlanetZodiacInfo]] = {}

    # Add aspect events
    collected_events = build_events(eph, ts, config, aspects, cycle_events)

    build_elapsed = perf_counter() - start_total
    logging.debug("Build elapsed (including detection): %.2fs for %d events", build_elapsed, len(collected_events))

    # Write ICS
    try:
        folded_text = write_calendar(collected_events, config.product_id)
        with open(args.output, 'w') as f:
            f.write(folded_text)
        logging.info("ICS written: %s", args.output)
        total_elapsed = perf_counter() - start_total
        logging.info(
            "Total runtime: %s (%.2fs) (events=%d)",
            _format_hms(total_elapsed),
            total_elapsed,
            len(collected_events),
        )
    except Exception as e:
        logging.error(f"Failed to write ICS: {e}")
        print("Failed to write ICS file; see log.")


if __name__ == '__main__':
    main()
