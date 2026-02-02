import json
from pathlib import Path

from daily_transit.cycles.engine import _write_cycle_metrics


def test_cycle_metrics_writer(tmp_path):
    metrics = {
        "ephem_calls": 2,
        "pos_cache_hits": 1,
        "sep_cache_hits": 3,
        "skipped_bodies": ["Ephemeris missing body Foo"],
        "boundary_drops": 0,
        "config_snapshot": {"planets": ["Sun", "Moon"], "ayanamsa": "tropical"},
    }
    out_path = tmp_path / "metrics.json"

    _write_cycle_metrics(str(out_path), metrics)

    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert data["ephem_calls"] == 2
    assert data["sep_cache_hits"] == 3
    # ensure keys are serialized as strings
    assert set(data.keys()) >= {"ephem_calls", "pos_cache_hits", "sep_cache_hits", "skipped_bodies", "config_snapshot"}
    assert data["skipped_bodies"] == ["Ephemeris missing body Foo"]
    assert data["config_snapshot"]["planets"] == ["Sun", "Moon"]
