from datetime import datetime, timezone

import math

from pytest import MonkeyPatch

from daily_transit.houses import (
    assign_houses,
    fallback_count,
    placidus_cusps,
    reset_fallback_counter,
)


def test_whole_sign_fallback_increments_counter_and_assigns_houses(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", False)
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longitudes = {
        "Sun": 15.0,  # Aries -> house 1
        "Moon": 75.0,  # Gemini -> house 3
        "Mars": 359.9,  # Pisces wrap -> house 12
    }

    result = assign_houses(dt, longitudes, latitude=51.5, longitude=-0.1, elevation_m=0.0)

    assert result.fallback is True
    assert result.system_used == "whole_sign"
    assert result.houses["Sun"] == 1
    assert result.houses["Moon"] == 3
    assert result.houses["Mars"] == 12
    assert fallback_count() == 1


def test_fallback_counter_resets(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", False)
    reset_fallback_counter()
    assert fallback_count() == 0
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    assign_houses(dt, {"Sun": 0.0}, latitude=0.0, longitude=0.0)
    assert fallback_count() == 1
    reset_fallback_counter()
    assert fallback_count() == 0


def test_whole_sign_wrap_boundary():
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longitudes = {
        "Mercury": 29.9999,  # Aries, should stay in house 1
        "Venus": 30.0,       # Taurus, should move to house 2
    }

    result = assign_houses(dt, longitudes, latitude=0.0, longitude=0.0, prefer_system="whole_sign")

    assert result.houses["Mercury"] == 1
    assert result.houses["Venus"] == 2


def test_high_latitude_triggers_fallback_and_assigns_all(monkeypatch: MonkeyPatch):
    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", False)
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longs = {f"P{i}": i * 29.5 for i in range(1, 13)}

    result = assign_houses(dt, longs, latitude=75.0, longitude=0.0)

    assert result.fallback is True
    assert result.system_used == "whole_sign"
    assert len(result.houses) == len(longs)
    assert all(1 <= h <= 12 for h in result.houses.values())
    assert fallback_count() == 1


def test_fallback_warning_emitted_once(caplog, monkeypatch: MonkeyPatch):
    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", False)
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longs = {"Sun": 0.0}

    with caplog.at_level("WARNING"):
        assign_houses(dt, longs, latitude=0.0, longitude=0.0)

    warnings = [rec for rec in caplog.records if "Placidus houses unavailable" in rec.message]
    assert len(warnings) == 1


def test_assign_houses_does_not_mutate_inputs():
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longs = {"Sun": 10.0, "Moon": 45.5}
    original = longs.copy()

    assign_houses(dt, longs, latitude=0.0, longitude=0.0)

    assert longs == original


def test_adjusted_longitudes_flow_into_houses():
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    adjusted_longs = {
        "Sun": 45.0,   # Taurus -> house 2
        "Moon": 195.0, # Libra -> house 7
    }

    result = assign_houses(dt, adjusted_longs, latitude=0.0, longitude=0.0, prefer_system="whole_sign")

    assert result.houses["Sun"] == 2
    assert result.houses["Moon"] == 7


def test_placidus_cusps_return_valid_angles():
    dt = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    cusps = placidus_cusps(dt, latitude=37.7749, longitude=-122.4194)

    assert len(cusps) == 12
    assert all(not math.isnan(c) for c in cusps)
    assert all(0.0 <= c < 360.0 for c in cusps)

    asc = cusps[0]
    desc = cusps[6]
    mc = cusps[9]
    ic = cusps[3]

    def ang_diff(a, b):
        return abs(((a - b + 180.0) % 360.0) - 180.0)

    assert ang_diff(desc, asc + 180.0) < 1.0
    assert ang_diff(ic, mc + 180.0) < 1.0


def test_placidus_cusps_cache_hit(monkeypatch: MonkeyPatch):
    dt = datetime(2025, 1, 1, 12, 30, tzinfo=timezone.utc)
    calls = {"count": 0}

    def fake_core(*args, **kwargs):
        calls["count"] += 1
        return [i * 30.0 for i in range(12)]

    monkeypatch.setattr("daily_transit.placidus._compute_cusps_core", fake_core)
    # First call populates cache using hour-bucketed key
    first = placidus_cusps(dt, latitude=10.0, longitude=20.0)
    second = placidus_cusps(dt, latitude=10.0, longitude=20.0)

    assert calls["count"] == 1
    assert first == second


def test_placidus_midlat_reference_values():
    dt = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    cusps = placidus_cusps(dt, latitude=37.7749, longitude=-122.4194)

    expected = [
        247.27,
        278.49,
        309.71,
        340.93,
        9.71,
        38.49,
        67.27,
        98.49,
        129.71,
        160.93,
        189.71,
        218.49,
    ]

    assert len(cusps) == len(expected)
    for got, want in zip(cusps, expected):
        assert abs(got - want) < 0.5


def test_placidus_equatorial_reference_values():
    dt = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    cusps = placidus_cusps(dt, latitude=0.0, longitude=0.0)

    expected = [
        10.47,
        41.23,
        71.98,
        102.73,
        131.98,
        161.23,
        190.47,
        221.23,
        251.98,
        282.73,
        311.98,
        341.23,
    ]

    assert len(cusps) == len(expected)
    for got, want in zip(cusps, expected):
        assert abs(got - want) < 0.5


def test_placidus_high_latitude_reference_and_ordering():
    dt = datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc)
    cusps = placidus_cusps(dt, latitude=65.0, longitude=0.0)

    assert len(cusps) == 12
    assert all(not math.isnan(c) for c in cusps)

    asc = cusps[0]
    desc = cusps[6]
    mc = cusps[9]
    ic = cusps[3]

    def ang_diff(a, b):
        return abs(((a - b + 180.0) % 360.0) - 180.0)

    assert ang_diff(desc, asc + 180.0) < 2.0
    assert ang_diff(ic, mc + 180.0) < 2.0

    # Verify ordering wraps once from ASC
    unwrapped = [0.0]
    for cusp in cusps[1:]:
        delta = ((cusp - asc + 360.0) % 360.0)
        unwrapped.append(delta)
    assert all(unwrapped[i] <= unwrapped[i + 1] for i in range(len(unwrapped) - 1))


def test_placidus_assigns_when_enabled(monkeypatch: MonkeyPatch):
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longs = {
        "Sun": 5.0,
        "Moon": 95.0,
        "Mars": 185.0,
    }

    cusps = [0.0 + i * 30.0 for i in range(12)]

    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", True)
    monkeypatch.setattr("daily_transit.houses.placidus_cusps", lambda *args, **kwargs: cusps)

    result = assign_houses(dt, longs, latitude=40.0, longitude=-74.0)

    assert result.fallback is False
    assert result.system_used == "placidus"
    assert result.houses == {"Sun": 1, "Moon": 4, "Mars": 7}
    assert fallback_count() == 0


def test_placidus_nan_triggers_fallback(monkeypatch: MonkeyPatch):
    reset_fallback_counter()
    dt = datetime(2025, 1, 1, tzinfo=timezone.utc)
    longs = {"Sun": 10.0}

    monkeypatch.setattr("daily_transit.houses.ENABLE_PLACIDUS", True)
    monkeypatch.setattr("daily_transit.houses.placidus_cusps", lambda *args, **kwargs: [math.nan] * 12)

    result = assign_houses(dt, longs, latitude=10.0, longitude=10.0)

    assert result.fallback is True
    assert result.system_used == "whole_sign"
    assert result.houses["Sun"] == 1
    assert fallback_count() == 1
