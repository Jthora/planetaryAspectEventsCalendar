from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.dto import CycleEvent, cycle_sort_key


def test_station_and_ingress_ordering_coincident():
    ts = datetime(2025, 1, 1, 0, 0)
    station = CycleEvent(
        event_type="station",
        body="Mercury",
        station_direction="forward_to_retro",
        start_time_utc=ts,
        end_time_utc=ts,
    )
    ingress = CycleEvent(
        event_type="ingress",
        body="Mercury",
        sign="Aries",
        start_time_utc=ts,
        end_time_utc=ts,
    )

    ordered = sorted([ingress, station], key=cycle_sort_key)
    # Expect ingress before station at identical timestamp per ordering policy (ingress rank=1, station rank=4)
    assert ordered[0].event_type == "ingress"
    assert ordered[1].event_type == "station"
