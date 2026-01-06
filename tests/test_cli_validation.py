import logging
from types import SimpleNamespace

import pytest

from DailyTransitAspectCalendarGenerator import (
    _validate_location_args,
    _warn_compact_daily_summary,
    parse_args,
)


def test_compact_requires_lat_lon():
    args = SimpleNamespace(mode="compact", lat=None, lon=None)
    with pytest.raises(SystemExit):
        _validate_location_args(args)


def test_compact_rejects_out_of_range():
    args = SimpleNamespace(mode="compact", lat=100.0, lon=0.0)
    with pytest.raises(SystemExit):
        _validate_location_args(args)
    args = SimpleNamespace(mode="compact", lat=0.0, lon=200.0)
    with pytest.raises(SystemExit):
        _validate_location_args(args)


def test_standard_mode_allows_missing_location():
    args = SimpleNamespace(mode="standard", lat=None, lon=None)
    _validate_location_args(args)  # should not raise


def test_compact_daily_summary_emits_warning(caplog):
    args = SimpleNamespace(mode="compact", daily_summary=True)
    with caplog.at_level(logging.WARNING):
        _warn_compact_daily_summary(args)
    assert "compact mode" in caplog.text.lower()


def test_compact_daily_summary_no_warning_when_disabled(caplog):
    args = SimpleNamespace(mode="compact", daily_summary=False)
    with caplog.at_level(logging.WARNING):
        _warn_compact_daily_summary(args)
    assert "compact mode" not in caplog.text.lower()


def test_compact_daily_summary_default_off():
    args = parse_args([
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-02",
        "--mode",
        "compact",
        "--lat",
        "0",
        "--lon",
        "0",
    ])
    assert args.daily_summary is False


def test_compact_mode_missing_lat_lon_via_parse_args():
    args = parse_args([
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-02",
        "--mode",
        "compact",
    ])

    with pytest.raises(SystemExit) as excinfo:
        _validate_location_args(args)

    assert "--lat --lon" in str(excinfo.value)


def test_unknown_ayanamsa_choice_rejected():
    with pytest.raises(SystemExit):
        parse_args([
            "--start",
            "2025-01-01",
            "--end",
            "2025-01-02",
            "--ayanamsa",
            "unknown",
        ])
