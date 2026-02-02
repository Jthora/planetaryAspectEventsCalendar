from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

WARN_PCT = 10.0
FAIL_PCT = 20.0
REFINE_WARN_RATE = 0.1  # percent of events
REFINE_FAIL_RATE = 0.5  # percent of events
CACHE_EVICT_WARN_RATE = 5.0  # percent of cap

MetricMap = Dict[str, Union[int, float]]


@dataclass
class MetricResult:
    scenario: str
    metric: str
    baseline: float
    candidate: float
    delta_pct: float
    status: str
    detail: str
    waiver_id: Optional[str] = None


@dataclass
class Waiver:
    id: str
    scenario: str
    metric: str
    expires: Optional[date]
    baseline_report: Optional[str]
    new_report: Optional[str]

    @classmethod
    def from_mapping(cls, data: Dict) -> "Waiver":
        waiver = data.get("waiver", data)
        expires = waiver.get("expires")
        expires_date = None
        if expires:
            try:
                expires_date = date.fromisoformat(expires)
            except ValueError as exc:
                raise ValueError(f"Invalid waiver expires date: {expires}") from exc
        return cls(
            id=str(waiver.get("id", "")),
            scenario=str(waiver.get("scenario", "")),
            metric=str(waiver.get("metric", "")),
            expires=expires_date,
            baseline_report=waiver.get("baseline_report"),
            new_report=waiver.get("new_report"),
        )

    def is_active(self, today: Optional[date] = None) -> bool:
        today = today or date.today()
        if self.expires and self.expires < today:
            return False
        return True

    def matches(self, scenario: str, metric: str, baseline_path: Path, candidate_path: Path) -> bool:
        if not self.is_active():
            return False
        if self.scenario and self.scenario != scenario:
            return False
        if self.metric and self.metric != metric:
            return False
        if self.baseline_report and Path(self.baseline_report).name != baseline_path.name:
            return False
        if self.new_report and Path(self.new_report).name != candidate_path.name:
            return False
        return True


def _load_yaml(text: str) -> Dict:
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - exercised only when missing dependency
        raise RuntimeError("pyyaml is required to load YAML waivers") from exc
    return yaml.safe_load(text)


def load_waivers(paths: Sequence[Path]) -> List[Waiver]:
    waivers: List[Waiver] = []
    for path in paths:
        if path.is_dir():
            for child in sorted(path.iterdir()):
                if child.suffix.lower() in {".json", ".yaml", ".yml"}:
                    waivers.extend(load_waivers([child]))
            continue
        text = path.read_text()
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = _load_yaml(text)
        else:
            data = json.loads(text)
        if isinstance(data, list):
            waivers.extend(Waiver.from_mapping(item) for item in data)
        else:
            waivers.append(Waiver.from_mapping(data))
    return waivers


def _scenario_name(path: Path) -> str:
    stem = path.stem
    if stem.startswith("metrics-"):
        return stem[len("metrics-"):]
    return stem


def _load_report(path: Path) -> Dict:
    return json.loads(path.read_text())


def _delta_pct(baseline: float, candidate: float) -> float:
    if baseline == 0:
        return 0.0 if candidate == 0 else math.inf
    return ((candidate - baseline) / baseline) * 100.0


def _collect_reports(directory: Path, scenarios: Optional[Iterable[str]] = None) -> Dict[str, Path]:
    reports: Dict[str, Path] = {}
    for path in directory.glob("*.json"):
        name = _scenario_name(path)
        reports[name] = path
    if scenarios:
        missing = [s for s in scenarios if s not in reports]
        if missing:
            raise FileNotFoundError(f"Missing reports in {directory}: {', '.join(missing)}")
        return {s: reports[s] for s in scenarios}
    return reports


def _evaluate_delta_metric(
    scenario: str,
    metric: str,
    baseline_value: float,
    candidate_value: float,
    warn_pct: float,
    fail_pct: float,
    baseline_path: Path,
    candidate_path: Path,
    waivers: Sequence[Waiver],
) -> MetricResult:
    delta = _delta_pct(baseline_value, candidate_value)
    status = "ok"
    detail = f"{baseline_value} -> {candidate_value} ({delta:+.2f}%)"

    if math.isinf(delta):
        status = "fail"
        detail = f"baseline 0; candidate {candidate_value}"
    elif delta > fail_pct:
        status = "fail"
    elif delta > warn_pct:
        status = "warn"

    waiver_id: Optional[str] = None
    if status == "fail":
        for waiver in waivers:
            if waiver.matches(scenario, metric, baseline_path, candidate_path):
                status = "waived"
                waiver_id = waiver.id
                break

    return MetricResult(
        scenario=scenario,
        metric=metric,
        baseline=baseline_value,
        candidate=candidate_value,
        delta_pct=delta,
        status=status,
        detail=detail,
        waiver_id=waiver_id,
    )


def _evaluate_refine_failures(
    scenario: str,
    baseline_value: float,
    candidate_value: float,
    total_events: int,
    baseline_path: Path,
    candidate_path: Path,
    waivers: Sequence[Waiver],
) -> MetricResult:
    delta = _delta_pct(baseline_value, candidate_value)
    rate = (candidate_value / total_events * 100.0) if total_events else 0.0
    status = "ok"
    detail = f"{candidate_value} failures over {total_events} events ({rate:.3f}%); delta {delta:+.2f}%"

    if rate > REFINE_FAIL_RATE:
        status = "fail"
    elif rate > REFINE_WARN_RATE:
        status = "warn"

    waiver_id: Optional[str] = None
    if status == "fail":
        for waiver in waivers:
            if waiver.matches(scenario, "refine_failures", baseline_path, candidate_path):
                status = "waived"
                waiver_id = waiver.id
                break

    return MetricResult(
        scenario=scenario,
        metric="refine_failures",
        baseline=baseline_value,
        candidate=candidate_value,
        delta_pct=delta,
        status=status,
        detail=detail,
        waiver_id=waiver_id,
    )


def _evaluate_cache_evictions(
    scenario: str,
    baseline_value: float,
    candidate_value: float,
    baseline_path: Path,
    candidate_path: Path,
    waivers: Sequence[Waiver],
    pos_cache_cap: Optional[int],
    sep_cache_cap: Optional[int],
) -> MetricResult:
    delta = _delta_pct(baseline_value, candidate_value)
    status = "ok"
    detail_parts = [f"{baseline_value} -> {candidate_value} ({delta:+.2f}%)"]

    caps = [cap for cap in (pos_cache_cap, sep_cache_cap) if cap]
    if caps:
        total_cap = sum(caps)
        rate = (candidate_value / total_cap * 100.0) if total_cap else 0.0
        detail_parts.append(f"cap_util={rate:.2f}%")
        if rate > CACHE_EVICT_WARN_RATE:
            status = "warn"
    elif delta > FAIL_PCT:
        status = "fail"
    elif delta > WARN_PCT:
        status = "warn"

    detail = "; ".join(detail_parts)
    waiver_id: Optional[str] = None
    if status == "fail":
        for waiver in waivers:
            if waiver.matches(scenario, "cache_evictions", baseline_path, candidate_path):
                status = "waived"
                waiver_id = waiver.id
                break

    return MetricResult(
        scenario=scenario,
        metric="cache_evictions",
        baseline=baseline_value,
        candidate=candidate_value,
        delta_pct=delta,
        status=status,
        detail=detail,
        waiver_id=waiver_id,
    )


def compare_reports(
    baseline_dir: Path,
    candidate_dir: Path,
    scenarios: Optional[Iterable[str]] = None,
    waivers: Optional[Sequence[Waiver]] = None,
    warn_pct: float = WARN_PCT,
    fail_pct: float = FAIL_PCT,
    pos_cache_cap: Optional[int] = None,
    sep_cache_cap: Optional[int] = None,
) -> List[MetricResult]:
    waivers = waivers or []
    baseline_reports = _collect_reports(baseline_dir, scenarios)
    candidate_reports = _collect_reports(candidate_dir, baseline_reports.keys())

    results: List[MetricResult] = []
    for scenario, baseline_path in baseline_reports.items():
        candidate_path = candidate_reports[scenario]
        baseline = _load_report(baseline_path)
        candidate = _load_report(candidate_path)

        total_events = int(sum(candidate.get("cycle_counts", {}).values()))
        metrics: MetricMap = {
            "runtime_seconds": float(baseline.get("runtime_seconds", 0.0)),
            "ephem_calls": float(baseline.get("ephem_calls", 0)),
            "refine_failures": float(baseline.get("refine_failures", 0)),
            "cache_evictions": float(baseline.get("pos_cache_evictions", 0))
            + float(baseline.get("sep_cache_evictions", 0)),
            "chunk_count": float(baseline.get("chunk_count", 0)),
        }

        candidate_values: MetricMap = {
            "runtime_seconds": float(candidate.get("runtime_seconds", 0.0)),
            "ephem_calls": float(candidate.get("ephem_calls", 0)),
            "refine_failures": float(candidate.get("refine_failures", 0)),
            "cache_evictions": float(candidate.get("pos_cache_evictions", 0))
            + float(candidate.get("sep_cache_evictions", 0)),
            "chunk_count": float(candidate.get("chunk_count", 0)),
        }

        results.append(
            _evaluate_delta_metric(
                scenario,
                "runtime_seconds",
                metrics["runtime_seconds"],
                candidate_values["runtime_seconds"],
                warn_pct,
                fail_pct,
                baseline_path,
                candidate_path,
                waivers,
            )
        )
        results.append(
            _evaluate_delta_metric(
                scenario,
                "ephem_calls",
                metrics["ephem_calls"],
                candidate_values["ephem_calls"],
                warn_pct,
                fail_pct,
                baseline_path,
                candidate_path,
                waivers,
            )
        )
        results.append(
            _evaluate_refine_failures(
                scenario,
                metrics["refine_failures"],
                candidate_values["refine_failures"],
                total_events,
                baseline_path,
                candidate_path,
                waivers,
            )
        )
        results.append(
            _evaluate_cache_evictions(
                scenario,
                metrics["cache_evictions"],
                candidate_values["cache_evictions"],
                baseline_path,
                candidate_path,
                waivers,
                pos_cache_cap,
                sep_cache_cap,
            )
        )
        results.append(
            _evaluate_delta_metric(
                scenario,
                "chunk_count",
                metrics["chunk_count"],
                candidate_values["chunk_count"],
                warn_pct,
                fail_pct,
                baseline_path,
                candidate_path,
                waivers,
            )
        )
    return results


def _format_result(result: MetricResult) -> str:
    status = result.status.upper()
    waiver_note = f" waiver={result.waiver_id}" if result.waiver_id else ""
    return f"  - {result.metric}: {status} ({result.detail}){waiver_note}"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compare cycle perf metrics against baseline")
    parser.add_argument("baseline_dir", type=Path, help="Directory containing baseline JSON reports")
    parser.add_argument("candidate_dir", type=Path, help="Directory containing new JSON reports")
    parser.add_argument(
        "--scenarios",
        nargs="*",
        help="Scenario names to compare (default: infer from baseline dir)",
    )
    parser.add_argument(
        "--waivers",
        nargs="*",
        type=Path,
        default=[],
        help="Waiver files or directories (YAML or JSON)",
    )
    parser.add_argument("--warn-pct", type=float, default=WARN_PCT, help="Warn threshold percent (default 10)")
    parser.add_argument("--fail-pct", type=float, default=FAIL_PCT, help="Fail threshold percent (default 20)")
    parser.add_argument("--pos-cache-cap", type=int, help="Position cache capacity for eviction rate calc")
    parser.add_argument("--sep-cache-cap", type=int, help="Separation cache capacity for eviction rate calc")
    args = parser.parse_args(argv)

    if not args.baseline_dir.is_dir():
        parser.error(f"Baseline dir not found: {args.baseline_dir}")
    if not args.candidate_dir.is_dir():
        parser.error(f"Candidate dir not found: {args.candidate_dir}")

    loaded_waivers = load_waivers([Path(p) for p in args.waivers]) if args.waivers else []

    results = compare_reports(
        args.baseline_dir,
        args.candidate_dir,
        scenarios=args.scenarios,
        waivers=loaded_waivers,
        warn_pct=args.warn_pct,
        fail_pct=args.fail_pct,
        pos_cache_cap=args.pos_cache_cap,
        sep_cache_cap=args.sep_cache_cap,
    )

    scenario_order = []
    for r in results:
        if r.scenario not in scenario_order:
            scenario_order.append(r.scenario)

    exit_code = 0
    for scenario in scenario_order:
        print(f"Scenario {scenario}")
        for res in [r for r in results if r.scenario == scenario]:
            print(_format_result(res))
            if res.status == "fail":
                exit_code = 1

    failed = [r for r in results if r.status == "fail"]
    if failed:
        print("\nFailures detected above fail threshold; consider adding a waiver if justified.")

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
