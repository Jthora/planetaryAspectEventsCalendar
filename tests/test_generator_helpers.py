from datetime import datetime

from ics import Event

from DailyTransitAspectCalendarGenerator import (
    _event_priority,
    _event_sort_key,
    select_aspects,
)


MAJOR_ASPECTS = {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}


def make_event(categories, begin=None, name="Test", uid="uid"):
    event = Event()
    event.categories = categories
    event.begin = begin
    event.name = name
    event.uid = uid
    return event


def test_select_aspects_major_scope_returns_only_major_angles():
    selected = select_aspects("major")
    assert set(selected.keys()) == MAJOR_ASPECTS


def test_select_aspects_all_scope_includes_minor_angles():
    selected = select_aspects("all")
    assert MAJOR_ASPECTS.issubset(selected.keys())
    assert "Quincunx" in selected


def test_select_aspects_complete_scope_uses_catalog():
    selected = select_aspects("complete")
    assert "Trebiquintile" in selected
    assert "Semi-Septile" in selected


def test_select_aspects_all_matches_legacy_dictionary():
    selected = select_aspects("all")
    # Legacy dictionary includes many more aspects than the curated complete set.
    assert len(selected) > len(MAJOR_ASPECTS)
    assert selected.get("Septile") is not None


def test_event_priority_daily_transit_wins():
    daily = make_event(["Daily Transit"])
    lunar = make_event(["Lunar Phase"])
    aspect = make_event(["Conjunction"])

    assert _event_priority(daily) == 0
    assert _event_priority(lunar) == 1
    assert _event_priority(aspect) == 2


def test_event_sort_key_handles_missing_begin_timestamp():
    event = make_event(["Daily Transit"], begin=None, name="Alpha", uid="123")
    priority, timestamp, _, _ = _event_sort_key(event)
    assert priority == 0
    assert timestamp == float("inf")


def test_event_sort_key_orders_by_begin_then_name_then_uid():
    first_begin = datetime(2024, 1, 1, 0, 0)
    second_begin = datetime(2024, 1, 1, 12, 0)

    first_event = make_event(["Conjunction"], begin=first_begin, name="Aspect A", uid="1")
    second_event = make_event(["Conjunction"], begin=second_begin, name="Aspect B", uid="0")

    ordered = sorted([second_event, first_event], key=_event_sort_key)
    assert ordered[0] is first_event

    # When begin is equal, ensure secondary sorting kicks in
    tie_event_a = make_event(["Conjunction"], begin=first_begin, name="Aspect A", uid="2")
    tie_event_b = make_event(["Conjunction"], begin=first_begin, name="Aspect A", uid="1")

    ordered_ties = sorted([tie_event_a, tie_event_b], key=_event_sort_key)
    assert ordered_ties[0].uid == "1"
