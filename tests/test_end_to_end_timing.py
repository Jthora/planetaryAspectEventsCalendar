"""Regression tests comparing detection output to timing reference fixtures."""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from DailyTransitAspectCalendarGenerator import load_ephemeris
from daily_transit.aspect_detection import detect_aspects

FIXTURE_FILE = Path(__file__).resolve().parent / "fixtures" / "timing_accuracy" / "reference_major_20240201_48h.json"


@pytest.mark.slow
@pytest.mark.require_ephemeris
@pytest.mark.skipif(not FIXTURE_FILE.exists(), reason="timing reference fixture missing")
def test_detect_aspects_matches_reference():
    reference = json.loads(FIXTURE_FILE.read_text(encoding="utf-8"))

    start = datetime.fromisoformat(reference["metadata"]["start"])
    end = datetime.fromisoformat(reference["metadata"]["end"])

    orb = reference["metadata"]["orb"]
    coarse_step = reference["metadata"]["coarse_step_minutes"]
    refine_step = reference["metadata"]["refine_step_minutes"]
    merge_window_hours = reference["metadata"]["merge_window_hours"]
    retrograde_probe_hours = reference["metadata"]["retrograde_probe_hours"]
    aspects = {name: float(deg) for name, deg in reference["metadata"]["aspects"].items()}
    planets = [tuple(p) for p in reference["metadata"]["planets"]]

    eph = load_ephemeris("de440s.bsp")

    from skyfield.api import load as skyfield_load

    ts = skyfield_load.timescale()

    detection_end = end + timedelta(days=1)
    events = detect_aspects(
        eph,
        ts,
        start,
        detection_end,
        orb,
        aspects,
        planets,
        coarse_step,
        refine_step,
        merge_window_hours,
        retrograde_probe_hours,
    )

    window_start = start
    inclusive_cutoff = detection_end - timedelta(seconds=1)
    filtered = [ev for ev in events if window_start <= ev.time <= inclusive_cutoff]

    expected = reference["events"]
    assert len(filtered) == len(expected)

    tolerance_seconds = 1

    for idx, (event, exp) in enumerate(zip(filtered, expected)):
        assert event.planet1 == exp["planet1"], idx
        assert event.planet2 == exp["planet2"], idx
        assert event.aspect == exp["aspect"], idx
        assert event.delta == pytest.approx(exp["delta"], abs=1e-6), idx
        exp_time = datetime.fromisoformat(exp["time"])
        assert abs((event.time - exp_time).total_seconds()) <= tolerance_seconds, idx
        assert bool(event.planet1_retrograde) == exp["planet1_retrograde"], idx
        assert bool(event.planet2_retrograde) == exp["planet2_retrograde"], idx
