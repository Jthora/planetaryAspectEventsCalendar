import json
from datetime import date, timedelta
from pathlib import Path

from tools.compare_cycle_perf import Waiver, compare_reports


def _write_report(directory: Path, name: str, payload: dict) -> Path:
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload))
    return path


def test_warn_and_fail_statuses(tmp_path):
    baseline_dir = tmp_path / "baseline"
    candidate_dir = tmp_path / "candidate"
    baseline_dir.mkdir()
    candidate_dir.mkdir()

    baseline_payload = {
        "runtime_seconds": 100.0,
        "ephem_calls": 1000,
        "refine_failures": 0,
        "chunk_count": 1,
        "cycle_counts": {"ingress": 50, "synodic_phase": 50},
        "pos_cache_evictions": 0,
        "sep_cache_evictions": 0,
    }
    candidate_payload = {
        "runtime_seconds": 112.0,  # +12% warn
        "ephem_calls": 1300,  # +30% fail
        "refine_failures": 0,
        "chunk_count": 1,
        "cycle_counts": {"ingress": 50, "synodic_phase": 50},
        "pos_cache_evictions": 0,
        "sep_cache_evictions": 0,
    }

    _write_report(baseline_dir, "demo", baseline_payload)
    _write_report(candidate_dir, "demo", candidate_payload)

    results = {r.metric: r.status for r in compare_reports(baseline_dir, candidate_dir)}
    assert results["runtime_seconds"] == "warn"
    assert results["ephem_calls"] == "fail"
    assert results["refine_failures"] == "ok"
    assert results["cache_evictions"] == "ok"
    assert results["chunk_count"] == "ok"


def test_waiver_applied(tmp_path):
    baseline_dir = tmp_path / "baseline"
    candidate_dir = tmp_path / "candidate"
    baseline_dir.mkdir()
    candidate_dir.mkdir()

    baseline_payload = {
        "runtime_seconds": 50.0,
        "ephem_calls": 100,
        "refine_failures": 0,
        "chunk_count": 1,
        "cycle_counts": {"ingress": 10},
        "pos_cache_evictions": 0,
        "sep_cache_evictions": 0,
    }
    candidate_payload = {
        "runtime_seconds": 55.0,
        "ephem_calls": 130,  # +30% would fail without waiver
        "refine_failures": 0,
        "chunk_count": 1,
        "cycle_counts": {"ingress": 10},
        "pos_cache_evictions": 0,
        "sep_cache_evictions": 0,
    }

    _write_report(baseline_dir, "demo", baseline_payload)
    _write_report(candidate_dir, "demo", candidate_payload)

    waiver = Waiver(
        id="PERF-TEST-1",
        scenario="demo",
        metric="ephem_calls",
        expires=date.today() + timedelta(days=1),
        baseline_report=None,
        new_report=None,
    )

    results = {r.metric: r.status for r in compare_reports(baseline_dir, candidate_dir, waivers=[waiver])}
    assert results["ephem_calls"] == "waived"
