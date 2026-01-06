from datetime import datetime
from types import SimpleNamespace
import sys

import pytest

import DailyTransitAspectCalendarGenerator as cli
from daily_transit.aspect_detection import AspectEvent


class FakeEph:
    def __contains__(self, _key):
        return True

    def __getitem__(self, _key):  # pragma: no cover - should not be used in stubbed path
        return self


@pytest.mark.parametrize("ayanamsa", ["tropical", "galactic_core", "lahiri"])
def test_compact_cli_slice_generates_houses(monkeypatch, tmp_path, ayanamsa):
    output_path = tmp_path / f"slice_{ayanamsa}.ics"
    log_path = tmp_path / "run.log"

    def fake_detect_aspects(*_args, **_kwargs):
        return [
            AspectEvent(
                planet1="Sun",
                planet2="Moon",
                aspect="Conjunction",
                time=datetime(2025, 1, 1, 12, 0, 0),
                delta=0.05,
                exact_degrees=0.0,
                raw_separation=0.05,
                planet1_retrograde=False,
                planet2_retrograde=False,
            )
        ]

    def fake_longitudes(*_args, **_kwargs):
        return {"Sun": 0.0, "Moon": 180.0}

    def fake_assign_houses(*_args, **_kwargs):
        return SimpleNamespace(houses={"Sun": 1, "Moon": 7}, fallback=False, reason=None)

    monkeypatch.setattr(cli, "load_ephemeris", lambda _path: FakeEph())
    monkeypatch.setattr(cli, "load", SimpleNamespace(timescale=lambda: None))
    monkeypatch.setattr(cli, "detect_aspects", fake_detect_aspects)
    monkeypatch.setattr(cli, "compute_body_longitudes", fake_longitudes)
    monkeypatch.setattr(cli, "assign_houses", fake_assign_houses)

    argv = [
        "prog",
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-03",
        "--mode",
        "compact",
        "--lat",
        "0",
        "--lon",
        "0",
        "--ayanamsa",
        ayanamsa,
        "--aspect-scope",
        "complete",
        "--output",
        str(output_path),
        "--log",
        str(log_path),
    ]

    monkeypatch.setattr(sys, "argv", argv)

    cli.main()

    ics_text = output_path.read_text()
    assert "H:1" in ics_text and "H:7" in ics_text
    assert "Conjunction" in ics_text
    assert ayanamsa in ics_text or "VCALENDAR" in ics_text  # basic sanity: file written
