from datetime import datetime

from daily_transit.cycles.dto import CycleEvent, cycle_sort_key


def test_ingress_precedes_station_when_same_time():
    ts = datetime(2026, 1, 1, 12, 0)
    ingress = CycleEvent(event_type="ingress", body="Mars", sign="Aries", start_time_utc=ts)
    station = CycleEvent(event_type="station", body="Mars", station_direction="forward_to_retro", start_time_utc=ts)

    ordered = sorted([station, ingress], key=cycle_sort_key)
    assert ordered[0].event_type == "ingress"
    assert ordered[1].event_type == "station"


def test_station_after_retro_interval_when_same_time():
    ts = datetime(2026, 1, 2, 12, 0)
    retro_interval = CycleEvent(
        event_type="retro_interval",
        body="Mercury",
        start_time_utc=ts,
        end_time_utc=ts,
        retrograde=True,
    )
    station = CycleEvent(event_type="station", body="Mercury", station_direction="retro_to_forward", start_time_utc=ts)

    ordered = sorted([station, retro_interval], key=cycle_sort_key)
    assert ordered[0].event_type == "retro_interval"
    assert ordered[1].event_type == "station"
