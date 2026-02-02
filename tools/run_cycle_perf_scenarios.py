import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List

DEFAULT_SPAN = 180

SCENARIOS = [
    {
        "name": "moon_week",
        "start": "2025-01-01",
        "end": "2025-01-08",
        "bodies": "Sun,Moon",
    },
    {
        "name": "inner_month",
        "start": "2025-05-01",
        "end": "2025-06-15",
        "bodies": "Sun,Moon,Mercury,Venus",
    },
    {
        "name": "outer_year",
        "start": "2025-01-01",
        "end": "2026-01-01",
        "bodies": "Sun,Moon,Mars,Jupiter,Saturn,Uranus,Neptune,Pluto",
    },
]


def run_scenario(cli: List[str], scenario: dict, output_dir: Path, chunk_span: int, include_aspects: bool):
    out_path = output_dir / f"metrics-{scenario['name']}.json"
    args = list(cli) + [
        "--cycle-engine",
        "helionext-cycles",
        "--cycle-types",
        "ingress,synodic_phase",
        "--cycle-phase-angles",
        "0,90,180,270",
        "--cycle-metrics-path",
        str(out_path),
        "--cycle-chunk-span-days",
        str(chunk_span),
        "--start",
        scenario["start"],
        "--end",
        scenario["end"],
        "--planets",
        scenario["bodies"],
        "--ayanamsa",
        "tropical",
        "--engine",
        "helionext",
    ]
    if not include_aspects:
        args.append("--skip-aspect-detection")
    print(f"Running {scenario['name']} -> {out_path}")
    subprocess.check_call(args)


def main():
    parser = argparse.ArgumentParser(description="Run cycle perf scenarios with metrics output")
    parser.add_argument(
        "--cli",
        required=True,
        help="CLI invocation to run (e.g., 'python DailyTransitAspectCalendarGenerator.py')",
    )
    parser.add_argument(
        "--output-dir",
        default="output/perf",
        help="Directory to write metrics JSON files (default output/perf)",
    )
    parser.add_argument(
        "--chunk-span",
        type=int,
        default=DEFAULT_SPAN,
        help="Chunk span days (default 180; set 0 to disable chunking)",
    )
    parser.add_argument(
        "--include-aspects",
        action="store_true",
        help="Run aspect detection too (default skips for faster cycle perf runs)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cli_parts = shlex.split(args.cli)
    results: List[Path] = []
    for scenario in SCENARIOS:
        run_scenario(cli_parts, scenario, output_dir, args.chunk_span, args.include_aspects)
        results.append(output_dir / f"metrics-{scenario['name']}.json")

    summary_path = output_dir / "metrics-summary.txt"
    try:
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from tools.analyze_cycle_metrics import summarize_metrics

        report, merged = summarize_metrics(results)
        summary_path.write_text(report)
        print(f"Wrote summary to {summary_path}")
    except Exception as exc:
        print(f"Skipping summary generation: {exc}")


if __name__ == "__main__":
    main()
