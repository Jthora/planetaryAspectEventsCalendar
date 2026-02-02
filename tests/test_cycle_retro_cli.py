import pytest

from DailyTransitAspectCalendarGenerator import parse_args


def test_negative_retro_probe_rejected():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-retro-probe-hours", "-1",
        ])


def test_excessive_retro_probe_rejected():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-retro-probe-hours", "100",
        ])
