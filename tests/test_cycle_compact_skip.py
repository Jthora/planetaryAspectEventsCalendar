from datetime import datetime
from types import SimpleNamespace
import sys

import pytz

import DailyTransitAspectCalendarGenerator as cli
from DailyTransitAspectCalendarGenerator import parse_args, build_config_from_args
from daily_transit.aspect_detection import AspectEvent


def test_compact_mode_disables_cycles_even_if_requested():
    args = parse_args([
        "--start", "2026-01-01",
        "--end", "2026-01-02",
        "--mode", "compact",
        "--cycle-engine", "helionext-cycles",
    ])
    assert args.cycle_engine == "off"
    cfg = build_config_from_args(
        args,
        aspect_degrees={"Conjunction": 0.0},
        planets=[("Sun", "Su")],
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )
    assert cfg.cycle_config is None


def _run_compact_cli(monkeypatch, tmp_path, extra_args):
    aspect = AspectEvent(
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        time=datetime(2026, 1, 1, 12, 0, 0),
        delta=0.1,
        exact_degrees=0.0,
        raw_separation=0.1,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    def fake_detect(*_args, **_kwargs):
        return [aspect]

    def fake_longitudes(*_args, **_kwargs):
        return {"Sun": 0.0, "Moon": 180.0}

    def fake_assign_houses(*_args, **_kwargs):
        return SimpleNamespace(houses={"Sun": 1, "Moon": 7}, fallback=False, reason=None)

    class FakeEph:
        def __contains__(self, _key):
            return True

    class FakeEngine:
        name = "fake"

        def detect(self, *_args, **_kwargs):  # pragma: no cover - trivial stub
            return fake_detect()

    monkeypatch.setattr(cli, "load_ephemeris", lambda _path: FakeEph())
    monkeypatch.setattr(cli, "load", SimpleNamespace(timescale=lambda: None))
    monkeypatch.setattr(cli, "get_detection_engine", lambda _name: FakeEngine())
    monkeypatch.setattr(cli, "get_cycle_detection_engine", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("cycle engine should not be used in compact mode")))
    monkeypatch.setattr(cli, "compute_body_longitudes", fake_longitudes)
    monkeypatch.setattr(cli, "assign_houses", fake_assign_houses)

    output_path = tmp_path / ("compact_base.ics" if not extra_args else "compact_cycle_flag.ics")
    log_path = tmp_path / "compact.log"

    argv = [
        "prog",
        "--start",
        "2026-01-01",
        "--end",
        "2026-01-02",
        "--mode",
        "compact",
        "--lat",
        "0",
        "--lon",
        "0",
        "--output",
        str(output_path),
        "--log",
        str(log_path),
    ] + list(extra_args)

    monkeypatch.setattr(sys, "argv", argv)
    cli.main()

    return output_path.read_text()


def test_compact_output_unchanged_when_cycle_flag_present(monkeypatch, tmp_path):
    base = _run_compact_cli(monkeypatch, tmp_path, extra_args=[])
    with_cycle_flag = _run_compact_cli(
        monkeypatch,
        tmp_path,
        extra_args=["--cycle-engine", "helionext-cycles"],
    )

    assert base == with_cycle_flag
    assert "Conjunction" in base
    assert "BEGIN:VCALENDAR" in base
