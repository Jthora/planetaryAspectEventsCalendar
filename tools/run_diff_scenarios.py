from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from skyfield.api import load

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from astrological_dictionaries import astrological_aspects
from daily_transit.config import GeneratorConfig
from daily_transit.constants import DEFAULT_PLANETS
from daily_transit.helionext import diff_harness

MAJOR_ASPECTS = {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}

SCENARIOS: Dict[str, Dict] = {
    "short": {
        "start": datetime(2025, 1, 1, 0, 0, 0),
        "end": datetime(2025, 1, 3, 23, 59, 59),
        "aspect_scope": "complete",
        "ayanamsa": "tropical",
    },
    "week": {
        "start": datetime(2025, 1, 1, 0, 0, 0),
        "end": datetime(2025, 1, 8, 23, 59, 59),
        "aspect_scope": "major",
        "ayanamsa": "tropical",
    },
    "medium": {
        "start": datetime(2025, 1, 1, 0, 0, 0),
        "end": datetime(2025, 1, 31, 23, 59, 59),
        "aspect_scope": "major",
        "ayanamsa": "tropical",
    },
    "long": {
        "start": datetime(2025, 1, 1, 0, 0, 0),
        "end": datetime(2025, 12, 31, 23, 59, 59),
        "aspect_scope": "complete",
        "ayanamsa": "tropical",
    },
    "stress": {
        "start": datetime(2025, 1, 1, 0, 0, 0),
        "end": datetime(2025, 1, 8, 23, 59, 59),
        "aspect_scope": "complete",
        "ayanamsa": "galactic_core",
    },
}


def aspect_degrees_for_scope(scope: str) -> Dict[str, float]:
    all_aspects: Dict[str, float] = astrological_aspects["aspect_degrees"]
    if scope == "major":
        return {name: deg for name, deg in all_aspects.items() if name in MAJOR_ASPECTS}
    return dict(all_aspects)


def build_config(start: datetime, end: datetime, aspects: Dict[str, float], ayanamsa: str) -> GeneratorConfig:
    return GeneratorConfig(
        start_date=start,
        end_date=end,
        timezone=None,
        orb=1.0,
        aspect_degrees=aspects,
        planets=DEFAULT_PLANETS,
        coarse_step_mins=30,
        refine_step_mins=5,
        merge_window_hours=4.0,
        inclusive_end=False,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//HelioNext//DiffHarness//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=6.0,
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="standard",
        engine="helionext",
        mode="standard",
        ayanamsa=ayanamsa,
        latitude=None,
        longitude=None,
        elevation_m=0.0,
        precision_deg="decimal",
        precision_time="seconds",
    )


def run_scenario(name: str, ephem_path: Path, out_dir: Path, time_tol: float, delta_tol: float) -> Path:
    if name not in SCENARIOS:
        raise ValueError(f"Unknown scenario '{name}'")
    scenario = SCENARIOS[name]
    aspects = aspect_degrees_for_scope(scenario["aspect_scope"])
    config = build_config(scenario["start"], scenario["end"], aspects, scenario["ayanamsa"])

    eph = load(str(ephem_path))
    ts = load.timescale()

    report = diff_harness.run_dual(
        config=config,
        eph=eph,
        ts=ts,
        detection_end=config.end_date,
        time_tolerance_s=time_tol,
        delta_tolerance_deg=delta_tol,
    )
    base = out_dir / f"diff_{name}_{scenario['ayanamsa']}"
    os.makedirs(out_dir, exist_ok=True)
    diff_harness.write_reports(report, str(base))
    return base.with_name(base.name + "_report.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run dual-run diff scenarios for HelioNext vs legacy")
    parser.add_argument("scenario", choices=sorted(SCENARIOS.keys()), help="Scenario to run")
    parser.add_argument("--ephem", default=str(Path(__file__).resolve().parents[1] / "de440s.bsp"), help="Path to ephemeris bsp file")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "output" / "diff_reports"), help="Directory to write reports")
    parser.add_argument("--time-tol", type=float, default=2.0, help="Time tolerance in seconds")
    parser.add_argument("--delta-tol", type=float, default=0.005, help="Delta tolerance in degrees")
    return parser.parse_args()


def main():
    args = parse_args()
    report_path = run_scenario(
        name=args.scenario,
        ephem_path=Path(args.ephem),
        out_dir=Path(args.out),
        time_tol=args.time_tol,
        delta_tol=args.delta_tol,
    )
    print(f"Wrote diff report to {report_path}")


if __name__ == "__main__":
    main()
