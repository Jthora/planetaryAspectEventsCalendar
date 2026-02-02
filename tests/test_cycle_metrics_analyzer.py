import json
from pathlib import Path

from tools.analyze_cycle_metrics import summarize_metrics


def test_metrics_analyzer_merges_and_rates(tmp_path):
    m1 = {
        "ephem_calls": 2,
        "pos_cache_hits": 3,
        "pos_cache_misses": 1,
        "sep_cache_hits": 4,
        "sep_cache_misses": 2,
        "ephem_calls_by_body": {"Moon": 2},
        "pos_cache_hits_by_body": {"Moon": 3},
        "pos_cache_misses_by_body": {"Moon": 1},
        "sep_cache_hits_by_pair": {"Moon|Sun": 4},
        "sep_cache_misses_by_pair": {"Moon|Sun": 2},
    }
    m2 = {
        "ephem_calls": 1,
        "pos_cache_hits": 1,
        "pos_cache_misses": 1,
        "sep_cache_hits": 1,
        "sep_cache_misses": 0,
        "ephem_calls_by_body": {"Sun": 1},
        "pos_cache_hits_by_body": {"Sun": 1},
        "pos_cache_misses_by_body": {"Sun": 1},
        "sep_cache_hits_by_pair": {"Moon|Sun": 1},
        "sep_cache_misses_by_pair": {"Moon|Sun": 0},
    }

    p1 = tmp_path / "m1.json"
    p2 = tmp_path / "m2.json"
    p1.write_text(json.dumps(m1))
    p2.write_text(json.dumps(m2))

    report, merged = summarize_metrics([p1, p2])

    assert merged["ephem_calls"] == 3
    assert merged["pos_cache_hits_by_body"]["Moon"] == 3
    assert merged["pos_cache_hits_by_body"]["Sun"] == 1
    assert merged["sep_cache_hits_by_pair"]["Moon|Sun"] == 5
    assert "Moon|Sun" in report
    assert "miss_rate" in report
