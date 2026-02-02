from pathlib import Path

import pytest

from tools.prepare_cycle_perf_baseline import _collect_metrics, _copy_metrics


def test_collect_metrics_strips_prefix(tmp_path):
    (tmp_path / "metrics-moon_week.json").write_text("{}")
    (tmp_path / "outer_year.json").write_text("{}")

    pairs = _collect_metrics(tmp_path)
    assert pairs == [
        (tmp_path / "metrics-moon_week.json", "moon_week.json"),
        (tmp_path / "outer_year.json", "outer_year.json"),
    ]


def test_copy_metrics(tmp_path):
    src_dir = tmp_path / "src"
    dest_dir = tmp_path / "dest"
    src_dir.mkdir()
    (src_dir / "metrics-moon_week.json").write_text("{\"runtime_seconds\": 1}")

    pairs = _collect_metrics(src_dir)
    _copy_metrics(pairs, dest_dir)

    copied = dest_dir / "moon_week.json"
    assert copied.exists()
    assert copied.read_text() == "{\"runtime_seconds\": 1}"


def test_collect_metrics_raises_when_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        _collect_metrics(tmp_path)
