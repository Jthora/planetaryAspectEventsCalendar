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
from typing import Dict, List, Tuple

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

from daily_transit.aspect_detection import AspectEvent, detect_aspects
from daily_transit.config import GeneratorConfig
from daily_transit.constants import DEFAULT_PLANETS, EPHEMERIS_NAME_MAP
from daily_transit.ics_builder import build_aspect_event, build_daily_summary, build_lunar_phase_event
from daily_transit.lunar_phases import compute_lunar_phases


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily transit + aspect ICS (tropical).")
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--output', default='transit_aspects.ics', help='Output ICS filename')
    parser.add_argument('--ephemeris', default='de440s.bsp', help='SPK ephemeris file (Skyfield)')
    parser.add_argument('--orb', type=float, default=1.5, help='Orb in degrees (default 1.5)')
    parser.add_argument('--timezone', default='UTC', help='Timezone for event timestamps (default UTC)')
    parser.add_argument('--aspects', choices=['major', 'all'], default='major', help='Scope of aspects to include')
    parser.add_argument('--daily-summary', action='store_true', help='Include daily transit chart summary events')
    parser.add_argument('--no-aspects', action='store_true', help='Skip individual aspect events (only summaries if enabled)')
    parser.add_argument('--status', default='CONFIRMED', help='ICS STATUS field value (default CONFIRMED)')
    parser.add_argument('--product-id', default='-//Daily Transit Aspect Generator//EN', help='VCALENDAR PRODID')
    parser.add_argument('--thunderbird-friendly', action='store_true', help='Add explicit UID/DTSTAMP/CREATED for Thunderbird syncing')
    parser.add_argument('--coarse-step-mins', type=int, default=60, help='Minutes between coarse scan samples (default 60)')
    parser.add_argument('--refine-step-mins', type=int, default=5, help='Minutes between refinement samples (default 5)')
    parser.add_argument('--merge-window-hours', type=float, default=4.0, help='Merge duplicate aspect hits within this many hours (default 4)')
    parser.add_argument('--inclusive-end', action='store_true', help='Include aspects occurring exactly at the end boundary (<= end date + 00:00)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose console logging')
    parser.add_argument('--planets', help='Comma-separated list of planets to include (default: available planets)')
    parser.add_argument('--ascii-only', action='store_true', help='Use ASCII labels instead of glyphs in output')
    parser.add_argument('--retrograde-probe-hours', type=float, default=6.0, help='Hours ahead to probe for retrograde detection (default 6)')
    parser.add_argument('--log', default='daily_transit_aspects.log', help='Log file path')
    parser.add_argument('--lunar-phases', action='store_true', help='Include lunar phase events in the calendar output')
    parser.add_argument('--timing-debug', action='store_true', help='Emit detailed timing diagnostics during detection')
    parser.add_argument(
        '--interpretation-mode',
        choices=['standard', 'business'],
        default='standard',
        help='Select interpretation tone for aspect descriptions (default standard)'
    )
    return parser.parse_args()


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


def fold_ical_lines(ics_text: str, limit: int = 75) -> str:
    def fold_line(line: str) -> List[str]:
        if not line:
            return ['']
        folded: List[str] = []
        current = ''
        for ch in line:
            candidate = current + ch
            if len(candidate.encode('utf-8')) <= limit:
                current = candidate
                continue
            if current:
                folded.append(current)
            current = ' ' + ch
        folded.append(current)
        return folded

    raw_lines = ics_text.splitlines()
    folded_lines: List[str] = []
    for raw_line in raw_lines:
        folded_lines.extend(fold_line(raw_line))
    return "\r\n".join(folded_lines) + "\r\n"


def serialize_calendar(events: List, product_id: str) -> str:
    normalized_prodid = product_id if product_id else '-//Daily Transit Aspect Generator//EN'
    if not normalized_prodid.startswith('-//'):
        normalized_prodid = f"-//{normalized_prodid}"
    lines: List[str] = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        f'PRODID:{normalized_prodid}',
        'CALSCALE:GREGORIAN',
    ]
    for event in events:
        event_lines = event.serialize().strip().splitlines()
        lines.extend(event_lines)
    lines.append('END:VCALENDAR')
    raw_text = "\r\n".join(lines)
    if not raw_text.endswith("\r\n"):
        raw_text += "\r\n"
    return raw_text


def load_ephemeris(ephemeris_path: str):
    try:
        return load_file(ephemeris_path)
    except FileNotFoundError as e:
        logging.error(f"Ephemeris file not found: {ephemeris_path}")
        raise


def select_aspects(scope: str) -> Dict[str, float]:
    all_aspects = astrological_aspects.get('aspect_degrees', {})
    if scope == 'major':
        keep = {k: v for k, v in all_aspects.items() if k in {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}}
        return keep
    return all_aspects


def main():
    args = parse_args()
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

    config = GeneratorConfig(
        start_date=start_date,
        end_date=end_date,
        timezone=tz,
        orb=args.orb,
        aspect_degrees=aspect_degrees,
        planets=active_planets,
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
    )

    logging.info(
        "Scanning for aspects with coarse step %s min and refine step %s min (orb %.2f°)",
        config.coarse_step_mins,
        config.refine_step_mins,
        config.orb,
    )

    detection_end = config.end_date + timedelta(days=1)
    aspects = detect_aspects(
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
        timing_debug=config.timing_debug,
    )
    logging.info("Detected %s aspect events within orb %.2f°.", len(aspects), config.orb)

    collected_events: List = []

    # Add aspect events
    if not args.no_aspects:
        window_start = config.start_date
        exclusive_cutoff = config.end_date + timedelta(days=1)
        inclusive_cutoff = exclusive_cutoff - timedelta(seconds=1)
        for ev in aspects:
            if ev.time < window_start:
                continue
            if config.inclusive_end:
                if ev.time > inclusive_cutoff:
                    continue
            else:
                if ev.time >= exclusive_cutoff:
                    continue
            collected_events.append(
                build_aspect_event(
                    ev,
                    config.timezone,
                    config.status,
                    config.thunderbird_friendly,
                    config.planets,
                    astrological_aspects.get('aspect_meanings', {}),
                    config.interpretation_mode,
                    config.ascii_only,
                )
            )

    # Daily summaries
    if args.daily_summary:
        current = config.start_date
        while current <= config.end_date:
            aspects_today = [a for a in aspects if a.time.date() == current.date()]
            collected_events.append(
                build_daily_summary(
                    current,
                    config.timezone,
                    eph,
                    ts,
                    aspects_today,
                    config.status,
                    config.thunderbird_friendly,
                    config.planets,
                    astrological_aspects.get('aspect_meanings', {}),
                    config.interpretation_mode,
                    config.ascii_only,
                )
            )
            current += timedelta(days=1)

    if config.include_lunar_phases:
        lunar_phase_events = compute_lunar_phases(
            eph,
            ts,
            config.start_date,
            config.end_date,
        )
        logging.info("Detected %s lunar phase events in range.", len(lunar_phase_events))
        for phase_event in lunar_phase_events:
            collected_events.append(
                build_lunar_phase_event(
                    phase_event,
                    config.timezone,
                    config.status,
                    config.thunderbird_friendly,
                    config.ascii_only,
                )
            )

    collected_events.sort(key=_event_sort_key)

    # Write ICS
    try:
        raw_calendar = serialize_calendar(collected_events, config.product_id)
        folded_text = fold_ical_lines(raw_calendar)
        with open(args.output, 'w') as f:
            f.write(folded_text)
        logging.info("ICS written: %s", args.output)
    except Exception as e:
        logging.error(f"Failed to write ICS: {e}")
        print("Failed to write ICS file; see log.")


if __name__ == '__main__':
    main()
