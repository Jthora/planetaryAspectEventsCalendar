#!/usr/bin/env python3
"""Generate timing accuracy reference data using the current algorithm."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from DailyTransitAspectCalendarGenerator import load_ephemeris, select_aspects
from daily_transit.aspect_detection import detect_aspects
from daily_transit.constants import DEFAULT_PLANETS

FIXTURE_PATH = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "timing_accuracy" / "reference_major_20240201_48h.json"


def generate_fixture():
    start = datetime(2024, 2, 1)
    end = datetime(2024, 2, 2)

    orb = 1.5
    coarse_step = 30
    refine_step = 5
    merge_window_hours = 4.0
    retrograde_probe_hours = 6.0

    eph = load_ephemeris("de440s.bsp")

    from skyfield.api import load as skyfield_load

    ts = skyfield_load.timescale()

    aspect_degrees = select_aspects("major")

    detection_end = end + timedelta(days=1)

    events = detect_aspects(
        eph,
        ts,
        start,
        detection_end,
        orb,
        aspect_degrees,
        DEFAULT_PLANETS,
        coarse_step,
        refine_step,
        merge_window_hours,
        retrograde_probe_hours,
        timing_debug=False,
    )

    window_start = start
    exclusive_cutoff = end + timedelta(days=1)
    inclusive_cutoff = exclusive_cutoff - timedelta(seconds=1)

    filtered = []
    for ev in events:
        if ev.time < window_start:
            continue
        if ev.time > inclusive_cutoff:
            continue
        filtered.append(ev)

    payload = {
        "metadata": {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "orb": orb,
            "coarse_step_minutes": coarse_step,
            "refine_step_minutes": refine_step,
            "merge_window_hours": merge_window_hours,
            "retrograde_probe_hours": retrograde_probe_hours,
            "aspects": aspect_degrees,
            "planets": DEFAULT_PLANETS,
        },
        "events": [
            {
                "time": ev.time.isoformat(),
                "planet1": ev.planet1,
                "planet2": ev.planet2,
                "aspect": ev.aspect,
                "delta": ev.delta,
                "planet1_retrograde": bool(ev.planet1_retrograde),
                "planet2_retrograde": bool(ev.planet2_retrograde),
            }
            for ev in filtered
        ],
    }

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(filtered)} events to {FIXTURE_PATH}")


if __name__ == "__main__":
    generate_fixture()
