from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import List

PR_SUITE: List[str] = [
    "tests/test_cycle_synthetic_linear.py",
    "tests/test_cycle_ingress_double_cross.py",
    "tests/test_cycle_synodic_wrap_angles.py",
    "tests/test_cycle_retro_heuristics.py",
    "tests/test_cycle_cache.py",
    "tests/test_cycle_chunking.py",
    "tests/test_cycle_dto_uncertainty.py",
    "tests/test_cycle_real_moon_window.py",
]

NIGHTLY_ONLY: List[str] = [
    "tests/test_cycle_real_mercury_retro.py",
    "tests/test_cycle_real_outer_jup_ura.py",
    "tests/test_cycle_distance_extrema.py",
    "tests/test_cycle_ingress_fallback.py",
    "tests/test_cycle_station_ingress_coincident.py",
    "tests/test_cycle_synodic_sep_cache.py",
    "tests/test_cycle_metrics_output.py",
]

ALL_EXTRA: List[str] = [
    "tests/test_end_to_end_timing.py",
]


def _run_pytest(files: List[str], extra_pytest_args: str, quiet: bool) -> int:
    args = ["pytest"]
    if quiet:
        args.append("-q")
    if extra_pytest_args:
        args.extend(shlex.split(extra_pytest_args))
    args.extend(files)

    print("Running:", " ".join(args))
    result = subprocess.run(args)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run HelioNext cycle validation suites")
    parser.add_argument(
        "--suite",
        choices=["pr", "nightly", "all"],
        default="pr",
        help="Suite to run (default pr)",
    )
    parser.add_argument(
        "--extra-pytest-args",
        default="",
        help="Additional args passed through to pytest (quoted string)",
    )
    parser.add_argument(
        "--no-quiet",
        action="store_true",
        help="Do not pass -q to pytest (default is quiet)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: current working directory)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    quiet = not args.no_quiet

    if args.suite == "pr":
        files = PR_SUITE
    elif args.suite == "nightly":
        files = PR_SUITE + NIGHTLY_ONLY
    else:
        files = PR_SUITE + NIGHTLY_ONLY + ALL_EXTRA

    missing = [f for f in files if not (root / f).exists()]
    if missing:
        parser.error(f"Missing test files relative to {root}: {', '.join(missing)}")

    return _run_pytest(files, args.extra_pytest_args, quiet)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
