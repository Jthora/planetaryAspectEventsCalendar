from datetime import datetime

import pytz

from daily_transit.aspect_detection import AspectEvent
from daily_transit.ics_builder import build_aspect_event
from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.ics_builder import build_cycle_event


def test_cycle_and_aspect_uid_namespaces_differ():
    ts = datetime(2026, 1, 1, 0, 0)
    aspect_ev = AspectEvent(
        time=ts,
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )
    aspect_ics = build_aspect_event(
        aspect_ev,
        tz=pytz.UTC,
        status="CONFIRMED",
        thunderbird=False,
        planets=[("Sun", "Su"), ("Moon", "Mo")],
        aspect_meanings={},
        interpretation_mode="standard",
        ascii_only=True,
    )

    cycle_ev = CycleEvent(
        event_type="ingress",
        body="Sun",
        sign="Aries",
        start_time_utc=ts,
        end_time_utc=ts,
        source_engine="helionext-cycles",
    )
    cycle_ics = build_cycle_event(cycle_ev, pytz.UTC, status="CONFIRMED", thunderbird=False, ascii_only=True)

    assert aspect_ics.uid != cycle_ics.uid
    assert aspect_ics.uid.endswith("@transit-aspect")
    assert cycle_ics.uid.endswith("@helionext-cycles")
    assert cycle_ics.uid.startswith("cycles-")
