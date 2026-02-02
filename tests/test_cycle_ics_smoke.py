from datetime import datetime

import pytz
from ics import Calendar

from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.ics_builder import build_cycle_event
from daily_transit.ics_writer import fold_ical_lines, serialize_calendar


def test_cycle_ics_serializes_and_parses():
    ts = datetime(2026, 1, 1, 0, 0)
    ev = CycleEvent(
        event_type="ingress",
        body="Sun",
        sign="Aries",
        start_time_utc=ts,
        end_time_utc=ts,
        source_engine="helionext-cycles",
    )
    ics_event = build_cycle_event(ev, pytz.UTC, status="CONFIRMED", thunderbird=False, ascii_only=True)
    raw_calendar = serialize_calendar([ics_event], "-//HelioNext Cycles//EN")
    folded = fold_ical_lines(raw_calendar)

    # Parse to ensure ICS is readable by the ics library (smoke test)
    cal = Calendar(folded)
    events = list(cal.events)
    assert len(events) == 1
    parsed = events[0]
    assert "Sun" in parsed.name
    assert parsed.begin is not None
