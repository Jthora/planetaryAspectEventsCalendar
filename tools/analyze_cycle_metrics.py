import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple


def _merge_metrics(files: List[Path]) -> Dict:
    merged: Dict = {
        "ephem_calls": 0,
        "pos_cache_hits": 0,
        "pos_cache_misses": 0,
        "sep_cache_hits": 0,
        "sep_cache_misses": 0,
        "refine_calls": 0,
        "refine_iterations": 0,
        "refine_failures": 0,
        "runtime_seconds": 0.0,
        "chunk_count": 0,
        "pos_cache_evictions": 0,
        "sep_cache_evictions": 0,
        "ephem_calls_by_body": {},
        "pos_cache_hits_by_body": {},
        "pos_cache_misses_by_body": {},
        "sep_cache_hits_by_pair": {},
        "sep_cache_misses_by_pair": {},
        "stage_runtime_seconds": {},
        "cycle_counts": {},
    }
    for path in files:
        data = json.loads(path.read_text())
        for key, value in data.items():
            if isinstance(value, dict):
                bucket = merged.setdefault(key, {})
                for k, v in value.items():
                    bucket[k] = bucket.get(k, 0) + v
            elif isinstance(value, (int, float)):
                merged[key] = merged.get(key, 0) + value
    return merged


def _ratio(numerator: int, denominator: int) -> float:
    return (numerator / denominator) if denominator else 0.0


def summarize_metrics(files: List[Path]) -> Tuple[str, Dict]:
    merged = _merge_metrics(files)

    lines: List[str] = []
    lines.append("=== Overall ===")
    lines.append(
        f"runtime_s={merged.get('runtime_seconds', 0.0):.2f} chunk_count={merged.get('chunk_count', 0)} "
        f"ephem_calls={merged.get('ephem_calls', 0)} pos_hits={merged.get('pos_cache_hits', 0)} "
        f"pos_miss={merged.get('pos_cache_misses', 0)} sep_hits={merged.get('sep_cache_hits', 0)} "
        f"sep_miss={merged.get('sep_cache_misses', 0)} evict_pos={merged.get('pos_cache_evictions', 0)} "
        f"evict_sep={merged.get('sep_cache_evictions', 0)}"
    )

    stage = merged.get("stage_runtime_seconds", {})
    if stage:
        lines.append("stage_runtime_s=" + ", ".join(f"{k}={v:.2f}" for k, v in sorted(stage.items())))

    lines.append("\n=== By body (pos/ephem) ===")
    for body, hits in sorted(merged.get("pos_cache_hits_by_body", {}).items()):
        misses = merged.get("pos_cache_misses_by_body", {}).get(body, 0)
        calls = merged.get("ephem_calls_by_body", {}).get(body, 0)
        lines.append(
            f"{body:8s} hits={hits:6d} miss={misses:6d} ephem={calls:6d} miss_rate={_ratio(misses, hits + misses):.3f}"
        )

    counts = merged.get("cycle_counts", {})
    if counts:
        lines.append("\n=== Cycle counts ===")
        for name, value in sorted(counts.items()):
            lines.append(f"{name:14s} count={value}")

    lines.append("\n=== By pair (sep cache) ===")
    for pair, hits in sorted(merged.get("sep_cache_hits_by_pair", {}).items()):
        misses = merged.get("sep_cache_misses_by_pair", {}).get(pair, 0)
        lines.append(f"{pair:12s} hits={hits:6d} miss={misses:6d} miss_rate={_ratio(misses, hits + misses):.3f}")

    return "\n".join(lines), merged


def main():
    parser = argparse.ArgumentParser(description="Summarize cycle metrics JSON files.")
    parser.add_argument("files", nargs="+", help="Metrics JSON files to merge")
    args = parser.parse_args()

    paths = [Path(p) for p in args.files]
    report, _ = summarize_metrics(paths)
    print(report)


if __name__ == "__main__":
    main()
