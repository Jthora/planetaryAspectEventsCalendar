from __future__ import annotations

import argparse
import logging
from typing import List, Optional

from daily_transit.cycles.cli import (
    parse_cycle_types,
    parse_ingress_signs,
    parse_phase_angles,
    parse_cycle_planets,
    parse_synodic_pairs,
)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate daily transit + aspect ICS (standard or compact).")
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True, help='End date (YYYY-MM-DD, inclusive)')
    parser.add_argument('--output', default='transit_aspects.ics', help='Output ICS filename')
    parser.add_argument('--ephemeris', default='de440s.bsp', help='SPK ephemeris file (Skyfield)')
    parser.add_argument('--orb', type=float, default=1.5, help='Orb in degrees (default 1.5)')
    parser.add_argument('--timezone', default='UTC', help='Timezone for event timestamps (default UTC)')
    parser.add_argument(
        '--aspect-scope', '--aspects',
        dest='aspects',
        choices=['major', 'all', 'complete'],
        default='major',
        help='Scope of aspects to include (major default; all uses legacy dictionary; complete uses curated catalog)'
    )
    parser.add_argument(
        '--mode', '--output-mode', '--compact',
        dest='mode',
        choices=['standard', 'compact'],
        default='standard',
        help='Output mode (compact requires ayanamsa and location inputs)'
    )
    parser.add_argument(
        '--engine',
        choices=['legacy', 'helionext'],
        default='legacy',
        help='Aspect detection engine (legacy default; helionext is the new engine under development)'
    )
    parser.add_argument(
        '--cycle-engine',
        choices=['off', 'helionext-cycles'],
        default='off',
        help='Cycle detection engine (off disables cycle generation)'
    )
    parser.add_argument(
        '--ayanamsa',
        choices=['tropical', 'lahiri', 'galactic_core'],
        default='tropical',
        help='Ayanamsa offset to apply (default tropical)'
    )
    parser.add_argument('--lat', type=float, help='Latitude in decimal degrees (required for compact mode)')
    parser.add_argument('--lon', type=float, help='Longitude in decimal degrees (required for compact mode)')
    parser.add_argument('--elev', type=float, default=0.0, help='Elevation in meters (optional; default 0)')
    parser.add_argument(
        '--precision-deg',
        dest='precision_deg',
        choices=['decimal', 'dms'],
        default='decimal',
        help='Angle precision format (default decimal)'
    )
    parser.add_argument(
        '--precision-time',
        dest='precision_time',
        choices=['seconds', 'minutes'],
        default='seconds',
        help='Time precision (default HH:MM:SS with seconds)'
    )
    parser.add_argument('--daily-summary', action='store_true', help='Include daily transit chart summary events')
    parser.add_argument('--no-aspects', action='store_true', help='Skip individual aspect events (only summaries if enabled)')
    parser.add_argument(
        '--skip-aspect-detection',
        action='store_true',
        help='Skip aspect detection entirely (useful for cycle-only perf runs)'
    )
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
        '--cycle-types',
        dest='cycle_types',
        help='Comma-separated cycle types (e.g., ingress,synodic_phase,retro_interval,station,perihelion_aphelion,lunar_node,lunar_apogee,lunar_perigee)'
    )
    parser.add_argument(
        '--cycle-planets',
        dest='cycle_planets',
        help='Comma-separated planet list to use for cycles only (overrides global planets for cycle scans)'
    )
    parser.add_argument(
        '--cycle-phase-angles',
        dest='cycle_phase_angles',
        help='Comma-separated degrees for synodic phase detection (default: 0,90,180,270)'
    )
    parser.add_argument(
        '--cycle-ingress-signs',
        dest='cycle_ingress_signs',
        help='Comma-separated signs for ingress detection (default: all signs)'
    )
    parser.add_argument(
        '--cycle-merge-window-hours',
        dest='cycle_merge_window_hours',
        type=float,
        default=None,
        help='Merge window (hours) for cycle event deduplication (default: per event type)'
    )
    parser.add_argument(
        '--cycle-retro-probe-hours',
        dest='cycle_retro_probe_hours',
        type=float,
        default=None,
        help='Probe window (hours) for retro/station cycle detection (default: retrograde-probe-hours)'
    )
    parser.add_argument(
        '--cycle-chunk-span-days',
        dest='cycle_chunk_span_days',
        type=int,
        default=None,
        help='Chunk span days for cycle detection (default 180); set 0 or negative to disable chunking'
    )
    parser.add_argument(
        '--cycle-pos-cache-max',
        dest='cycle_pos_cache_max',
        type=int,
        default=None,
        help='Max entries for cycle position cache (<=0 for unbounded; default 150000)'
    )
    parser.add_argument(
        '--cycle-sep-cache-max',
        dest='cycle_sep_cache_max',
        type=int,
        default=None,
        help='Max entries for cycle separation cache (<=0 for unbounded; default 80000)'
    )
    parser.add_argument(
        '--cycle-missing-body-policy',
        dest='cycle_missing_body_policy',
        choices=['fail', 'skip'],
        default='fail',
        help='Missing body handling for cycles (default fail)'
    )
    parser.add_argument(
        '--cycle-metrics-path',
        dest='cycle_metrics_path',
        default=None,
        help='Optional metrics JSON output for cycle detection'
    )
    parser.add_argument(
        '--cycle-timing-debug',
        dest='cycle_timing_debug',
        action='store_true',
        help='Emit detailed timing diagnostics during cycle detection'
    )
    parser.add_argument(
        '--cycle-retro-padding-days',
        dest='cycle_retro_padding_days',
        type=float,
        default=0.0,
        help='Apply this many days of padding before/after the window for retro detection only (default 0)'
    )
    parser.add_argument(
        '--cycle-clamp-intervals',
        dest='cycle_clamp_intervals',
        action='store_true',
        help='Clamp overlapping retro intervals to the requested window instead of dropping'
    )
    parser.add_argument(
        '--cycle-derive-spans',
        dest='cycle_derive_spans',
        action='store_true',
        help='Emit derived spans for ingress stays and synodic phase arcs (opt-in)'
    )
    parser.add_argument(
        '--cycle-synodic-pairs',
        dest='cycle_synodic_pairs',
        help="Comma-separated synodic pairs to scan, each as 'Body|Body' (e.g., Sun|Jupiter,Mars|Jupiter)"
    )
    parser.add_argument(
        '--cycle-synodic-step-scale',
        dest='cycle_synodic_step_scale',
        type=float,
        default=None,
        help='Multiplier applied to synodic step minutes (e.g., 2.0 doubles step size for long runs)'
    )
    parser.add_argument(
        '--cycle-synodic-mode',
        dest='cycle_synodic_mode',
        choices=['phases', 'conjunction_only'],
        help='Synodic mode: phases (0/90/180/270) or conjunction_only (full cycle anchor only)'
    )
    parser.add_argument(
        '--cycle-synodic-max-delta-deg',
        dest='cycle_synodic_max_delta_deg',
        type=float,
        default=3.0,
        help='Drop synodic hits whose |delta to target| exceeds this many degrees (default 3.0)'
    )
    parser.add_argument(
        '--cycle-synodic-step-cap-minutes',
        dest='cycle_synodic_step_cap_minutes',
        type=int,
        default=180,
        help='Cap synodic step size in minutes even after scaling (default 180)'
    )
    parser.add_argument(
        '--cycle-long-span-mode',
        dest='cycle_long_span_mode',
        action='store_true',
        help='Enable coarse defaults tuned for century-scale spans (larger chunks/caches, fewer phase angles)'
    )
    parser.add_argument(
        '--cycle-no-progress',
        dest='cycle_no_progress',
        action='store_true',
        help='Disable cycle progress heartbeat (enabled by default)'
    )
    parser.add_argument(
        '--interpretation-mode',
        choices=['standard', 'business', 'space_force', 'raves'],
        default='standard',
        help='Select interpretation tone for aspect descriptions (default standard)'
    )
    parsed = parser.parse_args(args=argv)
    _validate_cycle_args(parsed)
    _enforce_compact_cycle_policy(parsed)
    return parsed


def _validate_cycle_args(args: argparse.Namespace):
    if getattr(args, "cycle_engine", "off") == "off":
        return
    parse_cycle_types(getattr(args, "cycle_types", None))
    parse_phase_angles(getattr(args, "cycle_phase_angles", None))
    parse_cycle_planets(getattr(args, "cycle_planets", None))
    parse_synodic_pairs(getattr(args, "cycle_synodic_pairs", None))
    parse_ingress_signs(getattr(args, "cycle_ingress_signs", None))
    retro_padding = getattr(args, "cycle_retro_padding_days", 0.0)
    if retro_padding is not None and retro_padding < 0:
        raise SystemExit("cycle-retro-padding-days must be non-negative")


def _enforce_compact_cycle_policy(args: argparse.Namespace):
    if getattr(args, "mode", "standard") != "compact":
        return
    if getattr(args, "cycle_engine", "off") != "off":
        logging.warning("Compact mode does not emit cycle events; disabling cycle engine for this run.")
        args.cycle_engine = "off"


def _validate_location_args(args: argparse.Namespace):
    if args.mode != 'compact':
        return

    missing: List[str] = []
    if args.lat is None:
        missing.append('--lat')
    if args.lon is None:
        missing.append('--lon')
    if missing:
        raise SystemExit(f"Compact mode requires latitude/longitude: missing {' '.join(missing)}")

    if args.lat is not None and not (-90.0 <= args.lat <= 90.0):
        raise SystemExit("Latitude must be within [-90, 90] degrees for compact mode.")
    if args.lon is not None and not (-180.0 <= args.lon <= 180.0):
        raise SystemExit("Longitude must be within [-180, 180] degrees for compact mode.")


def _warn_compact_daily_summary(args: argparse.Namespace):
    if args.mode == 'compact' and getattr(args, 'daily_summary', False):
        logging.warning(
            "Compact mode optimizes for concise aspect lines; daily summaries are not recommended. "
            "Proceeding because --daily-summary was provided."
        )
