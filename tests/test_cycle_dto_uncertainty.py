from datetime import datetime

from daily_transit.cycles.dto import CycleEvent, validate_cycle_event


def test_retro_interval_allows_uncertainty_and_convergence():
    ev = CycleEvent(
        event_type="retro_interval",
        body="Mars",
        start_time_utc=datetime(2026, 1, 1, 0, 0),
        end_time_utc=datetime(2026, 1, 2, 0, 0),
        retrograde=True,
        uncertainty_seconds=7200,
        convergence_status="fallback",
    )
    validate_cycle_event(ev)


def test_station_accepts_strength_and_uncertainty():
    ev = CycleEvent(
        event_type="station",
        body="Mercury",
        station_direction="forward_to_retro",
        start_time_utc=datetime(2026, 5, 1, 12, 0),
        end_time_utc=datetime(2026, 5, 1, 12, 0),
        station_strength=0.42,
        uncertainty_seconds=30.0,
        convergence_status="ok",
    )
    validate_cycle_event(ev)
