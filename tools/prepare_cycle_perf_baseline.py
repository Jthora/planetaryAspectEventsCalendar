from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import List, Tuple

DEFAULT_SOURCE = Path("output/perf")
DEFAULT_BASELINE = Path("output/perf/baseline")
DEFAULT_LATEST = Path("output/perf/latest")


def _collect_metrics(source_dir: Path) -> List[Tuple[Path, str]]:
    results: List[Tuple[Path, str]] = []
    for path in sorted(source_dir.glob("*.json")):
        stem = path.stem
        scenario = stem[len("metrics-") :] if stem.startswith("metrics-") else stem
        results.append((path, f"{scenario}.json"))
    if not results:
        raise FileNotFoundError(f"No metrics json files found in {source_dir}")
    return results


def _copy_metrics(pairs: List[Tuple[Path, str]], dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src, name in pairs:
        dest = dest_dir / name
        shutil.copyfile(src, dest)
        print(f"Copied {src} -> {dest}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare cycle perf baselines or latest reports")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Directory containing metrics JSON files")
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=DEFAULT_BASELINE,
        help="Destination for baseline reports (default output/perf/baseline)",
    )
    parser.add_argument(
        "--latest-dir",
        type=Path,
        default=DEFAULT_LATEST,
        help="Destination for latest run reports (default output/perf/latest)",
    )
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Copy into baseline dir (default is skip)",
    )
    parser.add_argument(
        "--update-latest",
        action="store_true",
        help="Copy into latest dir (default is skip)",
    )
    args = parser.parse_args()

    pairs = _collect_metrics(args.source)
    if not args.update_baseline and not args.update_latest:
        parser.error("Specify at least one of --update-baseline or --update-latest")

    if args.update_baseline:
        _copy_metrics(pairs, args.baseline_dir)
    if args.update_latest:
        _copy_metrics(pairs, args.latest_dir)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
