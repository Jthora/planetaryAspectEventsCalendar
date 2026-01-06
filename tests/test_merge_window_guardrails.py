from datetime import datetime, timedelta

from daily_transit import aspect_detection as ad
from daily_transit.aspect_detection import AspectEvent

BASE_TIME = datetime(2024, 1, 1, 0, 0, 0)


def make_event(
    offset_minutes: int,
    delta: float,
    pair: tuple[str, str],
    aspect: str = "Conjunction",
) -> AspectEvent:
    return AspectEvent(
        time=BASE_TIME + timedelta(minutes=offset_minutes),
        planet1=pair[0],
        planet2=pair[1],
        aspect=aspect,
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=delta,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )


def test_moon_pairs_merge_cluster():
    cluster = [
        make_event(0, 0.5, ("Sun", "Moon")),
        make_event(10, 0.3, ("Sun", "Moon")),
        make_event(20, 0.7, ("Sun", "Moon")),
    ]

    merged = ad.merge_aspect_events(cluster, merge_window_hours=4.0)

    assert len(merged) == 1
    assert merged[0].delta == 0.3


def test_slow_pairs_preserve_distinct_events():
    events = [
        make_event(0, 0.4, ("Sun", "Mercury")),
        make_event(90, 0.2, ("Sun", "Mercury")),
        make_event(200, 0.6, ("Sun", "Mercury")),
    ]

    merged = ad.merge_aspect_events(events, merge_window_hours=4.0)

    assert len(merged) == 3
    times = [event.time for event in merged]
    assert times == sorted(times)


def test_merge_aspect_events_empty_input_returns_empty():
    merged = ad.merge_aspect_events([], merge_window_hours=4.0)
    assert merged == []


def test_merge_aspect_events_respects_aspect_names():
    events = [
        make_event(0, 0.4, ("Sun", "Moon"), aspect="Conjunction"),
        make_event(5, 0.3, ("Sun", "Moon"), aspect="Trine"),
    ]

    merged = ad.merge_aspect_events(events, merge_window_hours=4.0)

    assert len(merged) == 2
    aspects = {event.aspect for event in merged}
    assert aspects == {"Conjunction", "Trine"}


def test_merge_aspect_events_prefers_earliest_when_delta_equal():
    events = [
        make_event(10, 0.25, ("Sun", "Moon")),
        make_event(5, 0.25, ("Sun", "Moon")),
    ]

    merged = ad.merge_aspect_events(events, merge_window_hours=4.0)

    assert len(merged) == 1
    assert merged[0].time == BASE_TIME + timedelta(minutes=5)


def test_mercury_pairs_merge_when_within_window():
    events = [
        make_event(0, 0.4, ("Sun", "Mercury")),
        make_event(30, 0.3, ("Sun", "Mercury")),
    ]

    merged = ad.merge_aspect_events(events, merge_window_hours=4.0)

    assert len(merged) == 1
    assert merged[0].delta == 0.3


def test_non_major_aspect_merges_same_as_major():
    events = [
        make_event(0, 0.4, ("Sun", "Moon"), aspect="SemiSquare"),
        make_event(20, 0.2, ("Sun", "Moon"), aspect="SemiSquare"),
    ]

    merged = ad.merge_aspect_events(events, merge_window_hours=4.0)

    assert len(merged) == 1
    assert merged[0].aspect == "SemiSquare"
    assert merged[0].delta == 0.2