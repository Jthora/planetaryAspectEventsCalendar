from datetime import datetime

import pytest
from ics import Event

from DailyTransitAspectCalendarGenerator import (
    _event_sort_key,
    fold_ical_lines,
    serialize_calendar,
)


def make_event(name: str, category: str, begin: datetime, uid_suffix: str) -> Event:
    event = Event()
    event.name = name
    event.categories = [category]
    event.begin = begin
    event.uid = f"{name}-{uid_suffix}"
    return event


def test_event_sorting_prioritizes_daily_then_lunar_then_aspects():
    base = datetime(2024, 1, 1)
    daily = make_event("daily", "Daily Transit", base, "1")
    lunar = make_event("lunar", "Lunar Phase", base, "2")
    aspect = make_event("aspect", "Conjunction", base, "3")

    later_daily = make_event("daily-late", "Daily Transit", base.replace(day=2), "4")

    events = [aspect, later_daily, lunar, daily]
    events.sort(key=_event_sort_key)

    names = [event.name for event in events]
    assert names == ["daily", "daily-late", "lunar", "aspect"]


def test_fold_ical_lines_wraps_and_prefixes_continuations():
    long_line = "DESCRIPTION:" + "A" * 150
    folded = fold_ical_lines(long_line)
    lines = folded.strip().split("\r\n")

    assert all(len(line.encode("utf-8")) <= 75 for line in lines)
    assert lines[0].startswith("DESCRIPTION:")
    for continuation in lines[1:]:
        assert continuation.startswith(" ")


def test_fold_ical_lines_handles_multibyte_glyphs():
    long_line = "SUMMARY:" + "♃" * 60
    folded = fold_ical_lines(long_line)
    lines = folded.strip().split("\r\n")

    assert all(len(line.encode("utf-8")) <= 75 for line in lines)
    assert lines[0].startswith("SUMMARY:")
    for continuation in lines[1:]:
        assert continuation.startswith(" ")


def test_serialize_calendar_injects_prodid_and_events():
    event = make_event("test", "Daily Transit", datetime(2024, 1, 1), "uid")
    ics_text = serialize_calendar([event], "Acme Transit//v0.4.0")

    assert "BEGIN:VCALENDAR" in ics_text
    assert "END:VCALENDAR" in ics_text
    assert "PRODID:-//Acme Transit//v0.4.0" in ics_text
    assert "BEGIN:VEVENT" in ics_text
    assert ics_text.endswith("\r\n")


def test_serialize_calendar_defaults_prodid_when_missing():
    event = make_event("test", "Daily Transit", datetime(2024, 1, 1), "uid")
    ics_text = serialize_calendar([event], "")
    assert "PRODID:-//Daily Transit Aspect Generator//EN" in ics_text
