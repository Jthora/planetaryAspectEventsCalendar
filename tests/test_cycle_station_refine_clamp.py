from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.retro import _refine_station, MAX_FRACTIONAL_BACKOFF


def test_refine_station_clamps_secant_step(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(hours=10)
    probe_hours = 1.0

    rates = {
        start: 1.0,
        end: -1.0,
    }

    def fake_velocity_sign(eph, ts, earth, body, dt, probe_hours_arg, pos_cache, metrics):
        return rates.get(dt, 0.0)

    monkeypatch.setattr("daily_transit.cycles.retro._velocity_sign", fake_velocity_sign)

    # Position cache and metrics placeholders
    pos_cache = {}
    metrics = {}

    station_time, _ = _refine_station(
        eph=None,
        ts=None,
        earth=None,
        body="Mercury",
        probe_hours=probe_hours,
        left=start,
        right=end,
        pos_cache=pos_cache,
        metrics=metrics,
    )

    # Ensure chosen time stays within clamped span bounds
    span_seconds = (end - start).total_seconds()
    max_jump = span_seconds * MAX_FRACTIONAL_BACKOFF
    earliest_allowed = end - timedelta(seconds=max_jump)
    latest_allowed = start + timedelta(seconds=max_jump)

    assert earliest_allowed <= station_time <= latest_allowed
