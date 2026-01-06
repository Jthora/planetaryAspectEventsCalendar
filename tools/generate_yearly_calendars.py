#!/usr/bin/env python3
"""Batch generate transit/aspect calendars for whole-year ranges.

This helper wraps ``DailyTransitAspectCalendarGenerator.py`` so we can
quickly render one ICS file per year without crafting individual CLI
invocations.

Example:
    python tools/generate_yearly_calendars.py \
        --start-year 2025 --end-year 2026 \
        --output-prefix business_calendar --interpretation-mode business \
        --daily-summary

The script will emit ``output/business_calendar_2025.ics`` and
``output/business_calendar_2026.ics`` by default.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def build_generator_command(
    year: int,
    output_path: Path,
    *,
    interpretation_mode: str,
    daily_summary: bool,
    orb: float,
    aspects: str,
    timezone: str,
    planets: str | None,
    ascii_only: bool,
    include_lunar_phases: bool,
    thunderbird_friendly: bool,
    retrograde_probe_hours: float,
    coarse_step_mins: int,
    refine_step_mins: int,
    merge_window_hours: float,
    status: str,
    product_id: str,
    verbose: bool,
    mode: str,
    ayanamsa: str,
    latitude: Optional[float],
    longitude: Optional[float],
    elevation_m: float,
    precision_deg: str,
    precision_time: str,
) -> List[str]:
    cmd: List[str] = [
        sys.executable,
        "DailyTransitAspectCalendarGenerator.py",
        "--start",
        f"{year}-01-01",
        "--end",
        f"{year}-12-31",
        "--output",
        str(output_path),
        "--interpretation-mode",
        interpretation_mode,
        "--orb",
        f"{orb:.4f}",
        "--aspects",
        aspects,
        "--timezone",
        timezone,
        "--mode",
        mode,
        "--ayanamsa",
        ayanamsa,
        "--precision-deg",
        precision_deg,
        "--precision-time",
        precision_time,
        "--retrograde-probe-hours",
        f"{retrograde_probe_hours:.4f}",
        "--coarse-step-mins",
        str(coarse_step_mins),
        "--refine-step-mins",
        str(refine_step_mins),
        "--merge-window-hours",
        f"{merge_window_hours:.4f}",
        "--status",
        status,
        "--product-id",
        product_id,
    ]

    if daily_summary:
        cmd.append("--daily-summary")
    if include_lunar_phases:
        cmd.append("--lunar-phases")
    if ascii_only:
        cmd.append("--ascii-only")
    if thunderbird_friendly:
        cmd.append("--thunderbird-friendly")
    if planets:
        cmd.extend(["--planets", planets])
    if verbose:
        cmd.append("--verbose")
    if latitude is not None:
        cmd.extend(["--lat", f"{latitude:.6f}"])
    if longitude is not None:
        cmd.extend(["--lon", f"{longitude:.6f}"])
    if elevation_m is not None:
        cmd.extend(["--elev", f"{elevation_m:.2f}"])

    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch-generate yearly ICS calendars using DailyTransitAspectCalendarGenerator",
    )
    parser.add_argument("--start-year", type=int, required=True, help="First year to render (inclusive)")
    parser.add_argument("--end-year", type=int, required=True, help="Last year to render (inclusive)")
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to store generated ICS files (default: output)",
    )
    parser.add_argument(
        "--output-prefix",
        default="transit_aspects",
        help="Filename prefix (default: transit_aspects)",
    )
    parser.add_argument(
        "--interpretation-mode",
        choices=["standard", "business", "space_force", "raves"],
        default="standard",
        help="Interpretation tone to render (default: standard)",
    )
    parser.add_argument(
        "--daily-summary",
        action="store_true",
        help="Include daily summary events (optional)",
    )
    parser.add_argument(
        "--no-daily-summary",
        dest="daily_summary",
        action="store_false",
        help="Disable daily summary events",
    )
    parser.set_defaults(daily_summary=False)
    parser.add_argument("--orb", type=float, default=1.5, help="Orb in degrees (default: 1.5)")
    parser.add_argument(
        "--aspects",
        choices=["major", "all", "complete"],
        default="major",
        help="Aspect scope to include (default: major)",
    )
    parser.add_argument("--timezone", default="UTC", help="Timezone for event timestamps (default: UTC)")
    parser.add_argument(
        "--mode",
        choices=["standard", "compact"],
        default="standard",
        help="Output mode (compact requires lat/lon)",
    )
    parser.add_argument(
        "--ayanamsa",
        choices=["tropical", "lahiri", "galactic_core"],
        default="tropical",
        help="Ayanamsa offset to apply (default: tropical)",
    )
    parser.add_argument("--lat", type=float, help="Latitude in decimal degrees (required for compact mode)")
    parser.add_argument("--lon", type=float, help="Longitude in decimal degrees (required for compact mode)")
    parser.add_argument("--elev", type=float, default=0.0, help="Elevation in meters (default: 0)")
    parser.add_argument(
        "--precision-deg",
        choices=["decimal", "dms"],
        default="decimal",
        help="Angle precision format (default: decimal)",
    )
    parser.add_argument(
        "--precision-time",
        choices=["seconds", "minutes"],
        default="seconds",
        help="Time precision format (default: seconds)",
    )
    parser.add_argument(
        "--planets",
        help="Optional comma-separated planet filter passed to generator",
    )
    parser.add_argument(
        "--ascii-only",
        action="store_true",
        help="Use ASCII labels instead of glyphs",
    )
    parser.add_argument(
        "--include-lunar-phases",
        action="store_true",
        help="Include lunar phase events in output",
    )
    parser.add_argument(
        "--thunderbird-friendly",
        action="store_true",
        help="Add UID/CREATED fields for Thunderbird sync",
    )
    parser.add_argument(
        "--retrograde-probe-hours",
        type=float,
        default=6.0,
        help="Hours ahead to probe for retrograde detection (default: 6)",
    )
    parser.add_argument(
        "--coarse-step-mins",
        type=int,
        default=60,
        help="Minutes between coarse scan samples (default: 60)",
    )
    parser.add_argument(
        "--refine-step-mins",
        type=int,
        default=5,
        help="Minutes between refinement samples (default: 5)",
    )
    parser.add_argument(
        "--merge-window-hours",
        type=float,
        default=4.0,
        help="Merge duplicate aspect hits within this hour window (default: 4)",
    )
    parser.add_argument(
        "--status",
        default="CONFIRMED",
        help="ICS STATUS field value (default: CONFIRMED)",
    )
    parser.add_argument(
        "--product-id",
        default="-//Daily Transit Aspect Generator//EN",
        help="VCALENDAR PRODID string",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Regenerate files even if they already exist",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Pass --verbose to each generator invocation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.end_year < args.start_year:
        raise SystemExit("end-year must be greater than or equal to start-year")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    for year in range(args.start_year, args.end_year + 1):
        output_path = output_dir / f"{args.output_prefix}_{year}.ics"
        if output_path.exists() and not args.overwrite:
            print(f"[skip] {year}: {output_path} already exists")
            continue

        cmd = build_generator_command(
            year,
            output_path,
            interpretation_mode=args.interpretation_mode,
            daily_summary=args.daily_summary,
            orb=args.orb,
            aspects=args.aspects,
            timezone=args.timezone,
            planets=args.planets,
            ascii_only=args.ascii_only,
            include_lunar_phases=args.include_lunar_phases,
            thunderbird_friendly=args.thunderbird_friendly,
            retrograde_probe_hours=args.retrograde_probe_hours,
            coarse_step_mins=args.coarse_step_mins,
            refine_step_mins=args.refine_step_mins,
            merge_window_hours=args.merge_window_hours,
            status=args.status,
            product_id=args.product_id,
            verbose=args.verbose,
            mode=args.mode,
            ayanamsa=args.ayanamsa,
            latitude=args.lat,
            longitude=args.lon,
            elevation_m=args.elev,
            precision_deg=args.precision_deg,
            precision_time=args.precision_time,
        )

        print(f"[run] {year}: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"[error] Year {year} generation failed with exit code {exc.returncode}")
            raise


if __name__ == "__main__":
    main()
