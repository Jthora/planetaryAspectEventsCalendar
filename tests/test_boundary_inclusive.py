from datetime import datetime, timedelta

from daily_transit.aspect_detection import AspectEvent


def filter_for_output(events, start, end, inclusive_end):
    exclusive_cutoff = end + timedelta(days=1)
    inclusive_cutoff = exclusive_cutoff - timedelta(seconds=1)
    results = []
    for ev in events:
        if ev.time < start:
            continue
        if inclusive_end:
            if ev.time > inclusive_cutoff:
                continue
        else:
            if ev.time >= exclusive_cutoff:
                continue
        results.append(ev)
    return results


def make_event(event_time):
    return AspectEvent(
        time=event_time,
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )


def test_inclusive_end_keeps_boundary_event():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    boundary_event = make_event(datetime(2024, 1, 2, 23, 59, 59))
    beyond_event = make_event(datetime(2024, 1, 3, 0, 0, 0))

    events = [boundary_event, beyond_event]
    filtered = filter_for_output(events, start, end, inclusive_end=True)

    assert boundary_event in filtered
    assert beyond_event not in filtered


def test_exclusive_end_drops_boundary_event():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)
    boundary_event = make_event(datetime(2024, 1, 3, 0, 0, 0))

    filtered = filter_for_output([boundary_event], start, end, inclusive_end=False)

    assert boundary_event not in filtered
