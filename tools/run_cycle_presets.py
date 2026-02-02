#!/usr/bin/env python3
from __future__ import annotations

"""
Run curated cycle presets to generate ICS files optimized for long/medium/short spans.

Presets focus on cycles-only generation (no aspects), tuned for 100-year windows by default.
You can choose which presets to run via --presets or run all.

Examples:
  python tools/run_cycle_presets.py --start 2026-01-01 --end 2125-12-31 --output-root output/presets --presets synodic_long,ingress_long --dry-run
  python tools/run_cycle_presets.py --start 2026-01-01 --end 2125-12-31 --output-root output/presets --presets all
"""

import argparse
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Sequence

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "DailyTransitAspectCalendarGenerator.py"


@dataclass
class CyclePreset:
    name: str
    description: str
    cycle_types: str
    phase_angles: str | None = None
    cycle_planets: str | None = None
    synodic_pairs: str | None = None
    synodic_step_scale: float | None = None
    synodic_mode: str | None = None
    synodic_max_delta_deg: float | None = None
    synodic_step_cap_minutes: int | None = None
    long_span_mode: bool = False
    ingress_signs: str | None = None
    output_name: str | None = None
    # Tuning knobs
    chunk_span_days: int | None = 360
    pos_cache_max: int | None = 300000
    sep_cache_max: int | None = 200000
    retro_padding_days: float = 15.0
    clamp_intervals: bool = True
    derive_spans: bool = True
    merge_window_hours: float | None = None
    coarse_step_mins: int | None = None
    refine_step_mins: int | None = None
    retro_probe_hours: float | None = None
    phase_override: bool = False  # If True, pass phase angles even if synodic not present.
    extra_args: List[str] = field(default_factory=list)
    default_span_years: int | None = None
    default_start: str | None = None

    def to_command(self, start: str, end: str, output_root: Path, base_args: Sequence[str]) -> List[str]:
        output_file = output_root / f"{self.output_name or self.name}.ics"
        cmd = [
            sys.executable,
            str(GENERATOR),
            "--start",
            start,
            "--end",
            end,
            "--output",
            str(output_file),
            "--cycle-engine",
            "helionext-cycles",
            "--cycle-types",
            self.cycle_types,
            "--skip-aspect-detection",
            "--no-aspects",
            "--cycle-chunk-span-days",
            str(self.chunk_span_days) if self.chunk_span_days is not None else "0",
        ]
        if self.cycle_planets:
            cmd.extend(["--cycle-planets", self.cycle_planets])
        if self.phase_angles and ("synodic_phase" in self.cycle_types or self.phase_override):
            cmd.extend(["--cycle-phase-angles", self.phase_angles])
        if self.synodic_pairs:
            cmd.extend(["--cycle-synodic-pairs", self.synodic_pairs])
        if self.ingress_signs:
            cmd.extend(["--cycle-ingress-signs", self.ingress_signs])
        if self.synodic_step_scale is not None:
            cmd.extend(["--cycle-synodic-step-scale", str(self.synodic_step_scale)])
        if self.synodic_mode:
            cmd.extend(["--cycle-synodic-mode", self.synodic_mode])
        if self.synodic_max_delta_deg is not None:
            cmd.extend(["--cycle-synodic-max-delta-deg", str(self.synodic_max_delta_deg)])
        if self.synodic_step_cap_minutes is not None:
            cmd.extend(["--cycle-synodic-step-cap-minutes", str(self.synodic_step_cap_minutes)])
        if self.long_span_mode:
            cmd.append("--cycle-long-span-mode")
        if self.pos_cache_max is not None:
            cmd.extend(["--cycle-pos-cache-max", str(self.pos_cache_max)])
        if self.sep_cache_max is not None:
            cmd.extend(["--cycle-sep-cache-max", str(self.sep_cache_max)])
        if self.retro_padding_days:
            cmd.extend(["--cycle-retro-padding-days", str(self.retro_padding_days)])
        if self.clamp_intervals:
            cmd.append("--cycle-clamp-intervals")
        if self.merge_window_hours is not None:
            cmd.extend(["--cycle-merge-window-hours", str(self.merge_window_hours)])
        if self.retro_probe_hours is not None:
            cmd.extend(["--cycle-retro-probe-hours", str(self.retro_probe_hours)])
        if self.coarse_step_mins is not None:
            cmd.extend(["--coarse-step-mins", str(self.coarse_step_mins)])
        if self.refine_step_mins is not None:
            cmd.extend(["--refine-step-mins", str(self.refine_step_mins)])
        if self.derive_spans:
            cmd.append("--cycle-derive-spans")
        if self.merge_window_hours is None:
            # allow defaults, but prefer small merge to cut dupes on long spans
            cmd.extend(["--cycle-merge-window-hours", "8"])
        cmd.extend(base_args)
        cmd.extend(self.extra_args)
        return cmd


PRESETS: Dict[str, CyclePreset] = {
    # Synodic: prioritize valuable long arcs (Sun + outers) to avoid inner-pair explosion.
    "synodic_long": CyclePreset(
        name="synodic_long",
        description="Synodic phases (outer-focused) for long spans",
        cycle_types="synodic_phase",
        phase_angles="0",
        cycle_planets="Sun,Jupiter,Saturn,Uranus,Neptune,Pluto",
        synodic_pairs=(
            "Sun|Jupiter,Sun|Saturn,Sun|Uranus,Sun|Neptune,Sun|Pluto,"
            "Jupiter|Saturn,Jupiter|Uranus,Jupiter|Neptune,Jupiter|Pluto,"
            "Saturn|Uranus,Saturn|Neptune,Saturn|Pluto,"
            "Uranus|Neptune,Uranus|Pluto,Neptune|Pluto"
        ),
        synodic_step_scale=2.0,
        synodic_mode="conjunction_only",
        synodic_max_delta_deg=0.3,
        synodic_step_cap_minutes=120,
        long_span_mode=True,
        chunk_span_days=540,
        pos_cache_max=500000,
        sep_cache_max=300000,
        default_span_years=100,
        default_start="2026-01-01",
    ),
    "synodic_medium": CyclePreset(
        name="synodic_medium",
        description="Synodic phases medium set (adds Mars)",
        cycle_types="synodic_phase",
        phase_angles="0",
        cycle_planets="Sun,Mars,Jupiter,Saturn,Uranus,Neptune,Pluto",
        synodic_pairs=(
            "Sun|Mars,Sun|Jupiter,Sun|Saturn,Sun|Uranus,Sun|Neptune,Sun|Pluto,"
            "Mars|Jupiter,Mars|Saturn,Mars|Uranus,Mars|Neptune,Mars|Pluto,"
            "Jupiter|Saturn,Jupiter|Uranus,Jupiter|Neptune,Jupiter|Pluto,"
            "Saturn|Uranus,Saturn|Neptune,Saturn|Pluto,"
            "Uranus|Neptune,Uranus|Pluto,Neptune|Pluto"
        ),
        synodic_step_scale=1.5,
        synodic_mode="conjunction_only",
        synodic_max_delta_deg=0.35,
        synodic_step_cap_minutes=90,
        long_span_mode=True,
        chunk_span_days=420,
        pos_cache_max=450000,
        sep_cache_max=260000,
        default_span_years=10,
        default_start="2026-01-01",
    ),
    "synodic_short": CyclePreset(
        name="synodic_short",
        description="Synodic phases with inners for short spans",
        cycle_types="synodic_phase",
        phase_angles="0",
        cycle_planets="Sun,Mercury,Venus,Mars,Jupiter,Saturn",
        synodic_pairs=(
            "Sun|Mercury,Sun|Venus,Sun|Mars,Sun|Jupiter,Sun|Saturn,"
            "Mercury|Venus,Mercury|Mars,Mercury|Jupiter,Mercury|Saturn,"
            "Venus|Mars,Venus|Jupiter,Venus|Saturn,"
            "Mars|Jupiter,Mars|Saturn,Jupiter|Saturn"
        ),
        synodic_mode="conjunction_only",
        synodic_max_delta_deg=0.35,
        synodic_step_cap_minutes=60,
        chunk_span_days=300,
        pos_cache_max=300000,
        sep_cache_max=180000,
        default_span_years=1,
        default_start="2026-01-01",
    ),
    # Ingress spans: outer-focused for long-term occupancy; spans derived on.
    "ingress_long": CyclePreset(
        name="ingress_long",
        description="Ingress spans for outers only",
        cycle_types="ingress",
        cycle_planets="Jupiter,Saturn,Uranus,Neptune,Pluto",
        chunk_span_days=540,
        pos_cache_max=400000,
        sep_cache_max=0,  # unused here
        retro_padding_days=0.0,
        default_span_years=100,
        default_start="2026-01-01",
    ),
    "ingress_medium": CyclePreset(
        name="ingress_medium",
        description="Ingress spans adds Mars/Jupiter",
        cycle_types="ingress",
        cycle_planets="Sun,Mars,Jupiter",
        chunk_span_days=420,
        pos_cache_max=350000,
        sep_cache_max=0,
        retro_padding_days=0.0,
        default_span_years=10,
        default_start="2026-01-01",
    ),
    "ingress_short": CyclePreset(
        name="ingress_short",
        description="Ingress spans inners + Sun (1y)",
        cycle_types="ingress",
        cycle_planets="Sun,Moon,Mercury,Venus,Mars",
        chunk_span_days=300,
        pos_cache_max=250000,
        sep_cache_max=0,
        retro_padding_days=0.0,
        default_span_years=1,
        default_start="2026-01-01",
    ),
    "ingress_lunar": CyclePreset(
        name="ingress_lunar",
        description="Ingress spans Moon-only (1y)",
        cycle_types="ingress",
        cycle_planets="Moon",
        chunk_span_days=120,
        pos_cache_max=150000,
        sep_cache_max=0,
        retro_padding_days=0.0,
        default_span_years=1,
        default_start="2026-01-01",
    ),
    # Retro/stations: long intervals on outers; clamp and pad a bit for continuity.
    "retro_long": CyclePreset(
        name="retro_long",
        description="Retro intervals + stations for outers",
        cycle_types="retro_interval,station",
        cycle_planets="Jupiter,Saturn,Uranus,Neptune,Pluto",
        long_span_mode=True,
        chunk_span_days=540,
        pos_cache_max=400000,
        sep_cache_max=0,
        retro_padding_days=45.0,
        clamp_intervals=True,
    ),
    "retro_medium": CyclePreset(
        name="retro_medium",
        description="Retro intervals + stations adds Mars",
        cycle_types="retro_interval,station",
        cycle_planets="Mars,Jupiter,Saturn,Uranus,Neptune,Pluto",
        long_span_mode=True,
        chunk_span_days=420,
        pos_cache_max=350000,
        sep_cache_max=0,
        retro_padding_days=30.0,
        clamp_intervals=True,
    ),
    "retro_short": CyclePreset(
        name="retro_short",
        description="Retro intervals + stations including inners",
        cycle_types="retro_interval,station",
        cycle_planets="Mercury,Venus,Mars,Jupiter,Saturn",
        chunk_span_days=240,
        pos_cache_max=250000,
        sep_cache_max=0,
        retro_padding_days=15.0,
        clamp_intervals=True,
    ),
    # Distance extrema (perihelion/aphelion) on outers only to limit churn.
    "perihelion_long": CyclePreset(
        name="perihelion_long",
        description="Perihelion/aphelion for outers",
        cycle_types="perihelion_aphelion",
        cycle_planets="Jupiter,Saturn,Uranus,Neptune,Pluto",
        chunk_span_days=540,
        pos_cache_max=200000,
        sep_cache_max=0,
        retro_padding_days=0.0,
        clamp_intervals=False,
        derive_spans=False,
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run curated cycle presets for ICS generation")
    parser.add_argument("--start", help="Start date YYYY-MM-DD (default depends on preset; e.g. synodic_short 2026-01-01)")
    parser.add_argument("--end", help="End date YYYY-MM-DD (default depends on preset span; e.g. synodic_short 2026-12-31)")
    parser.add_argument("--output-root", default="output/presets", help="Root output directory for generated ICS files")
    parser.add_argument("--presets", default="all", help="Comma-separated preset names to run, or 'all'")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    parser.add_argument("--log-level", default="INFO", help="Logging level for this runner")
    parser.add_argument("--timezone", default="UTC", help="Timezone for ICS output (default UTC)")
    parser.add_argument("--product-id", default="-//HelioNext Cycle Presets//EN", help="PRODID to embed")
    parser.add_argument("--ayanamsa", default="tropical", choices=["tropical", "lahiri", "galactic_core"], help="Ayanamsa mode")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate even if the output ICS already exists",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(asctime)s - %(levelname)s - %(message)s")

    requested = [p.strip() for p in args.presets.split(",") if p.strip()] if args.presets else []
    if not requested or "all" in requested:
        selected = list(PRESETS.values())
    else:
        missing = [p for p in requested if p not in PRESETS]
        if missing:
            raise SystemExit(f"Unknown preset(s): {', '.join(missing)}")
        selected = [PRESETS[p] for p in requested]

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    base_args = [
        "--timezone",
        args.timezone,
        "--product-id",
        args.product_id,
        "--ayanamsa",
        args.ayanamsa,
    ]

    def parse_date(d: str) -> date:
        return date.fromisoformat(d)

    def add_years(d: date, years: int) -> date:
        try:
            return d.replace(year=d.year + years)
        except ValueError:
            # Handle Feb 29 -> Feb 28 on non-leap replacement years.
            return d.replace(month=2, day=28, year=d.year + years)

    for preset in selected:
        # Resolve start/end per preset. If user supplies --start/--end, honor them; otherwise use preset defaults.
        preset_start_str = args.start or preset.default_start or "2026-01-01"
        start_date = parse_date(preset_start_str)
        if args.end:
            end_date = parse_date(args.end)
        elif preset.default_span_years:
            end_date = add_years(start_date, preset.default_span_years) - timedelta(days=1)
        else:
            end_date = add_years(start_date, 100) - timedelta(days=1)

        start_str = start_date.isoformat()
        end_str = end_date.isoformat()

        cmd = preset.to_command(start_str, end_str, output_root, base_args)
        if args.dry_run:
            logging.info("DRY RUN: %s", " ".join(cmd))
            continue
        out_idx = cmd.index("--output") + 1
        out_path = Path(cmd[out_idx])
        logging.info("Running preset %s -> %s", preset.name, out_path)
        if out_path.exists() and not args.force:
            logging.info("Skipping %s (exists); use --force to regenerate", preset.name)
            continue
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
