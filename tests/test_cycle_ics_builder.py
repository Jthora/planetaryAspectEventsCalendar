from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.ics_builder import build_cycle_event, _uid_for_cycle, ALL_DAY_THRESHOLD_HOURS


def test_uid_uses_cycle_namespace_and_engine():
    ev = CycleEvent(
        event_type="ingress",
        body="Mars",
        sign="Aries",
        start_time_utc=datetime(2026, 1, 1, 0, 0),
        end_time_utc=datetime(2026, 1, 1, 0, 0),
        source_engine="helionext-cycles",
    )
    uid = _uid_for_cycle(ev)
    assert "helionext-cycles" in uid


def test_retro_interval_long_duration_becomes_all_day():
    start = datetime(2026, 1, 1, 0, 0)
    end = start + timedelta(hours=ALL_DAY_THRESHOLD_HOURS + 1)
    ev = CycleEvent(
        event_type="retro_interval",
        body="Mercury",
        start_time_utc=start,
        end_time_utc=end,
        retrograde=True,
    )
    event = build_cycle_event(ev, pytz.UTC, status="CONFIRMED", thunderbird=False, ascii_only=True)
    # All-day events are date-only and end is exclusive next day
    assert event.all_day
    assert event.begin.date() == start.date()
    # DTEND exclusive next day
    assert event.end.date() == end.date() + timedelta(days=1)
