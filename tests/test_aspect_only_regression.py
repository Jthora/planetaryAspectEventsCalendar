from datetime import datetime

import pytz

from DailyTransitAspectCalendarGenerator import build_config_from_args, parse_args
from daily_transit.aspect_detection import AspectEvent
from daily_transit.ics_builder import build_aspect_event


PLANETS = [("Sun", "Su"), ("Moon", "Mo")]
MEANINGS = {"Conjunction": "Fusion"}


def _snapshot(extra_args):
    args = [
        "--start",
        "2026-01-01",
        "--end",
        "2026-01-02",
    ] + list(extra_args)
    parsed = parse_args(args)
    cfg = build_config_from_args(
        parsed,
        aspect_degrees={"Conjunction": 0.0},
        planets=PLANETS,
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )

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

    event = build_aspect_event(
        aspect,
        pytz.UTC,
        cfg.status,
        cfg.thunderbird_friendly,
        PLANETS,
        MEANINGS,
        interpretation_mode="noop",
        ascii_only=True,
        zodiac_context={},
    )

    return {
        "cycle_config": cfg.cycle_config,
        "name": event.name,
        "uid": event.uid,
        "categories": event.categories,
        "desc_head": event.description.splitlines()[:7],
    }


def test_aspect_only_snapshot_stable_when_cycles_disabled():
    baseline = _snapshot([])
    explicit_off = _snapshot(["--cycle-engine", "off"])

    expected_desc_head = [
        "Aspect: Conjunction",
        "Planets: Sun Su / Moon Mo",
        "Exact Time (UTC): 2026-01-01 12:00",
            "Separation Δ: 0.10° (Target 0.0°)",
            "Raw Separation: 0.10°",
        "",
        "Meaning: Fusion",
    ]

    for snapshot in (baseline, explicit_off):
        assert snapshot["cycle_config"] is None
        assert snapshot["name"] == "Su [CONJ] Mo"
        assert snapshot["categories"] == ["Conjunction"]
        assert snapshot["uid"].endswith("@transit-aspect")
        assert snapshot["desc_head"] == expected_desc_head

    assert baseline == explicit_off
