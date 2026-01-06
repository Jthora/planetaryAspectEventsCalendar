from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from daily_transit import aspect_detection as ad

BASE_TIME = datetime(2024, 1, 1, 0, 0, 0)


class FakeAngle:
    def __init__(self, degrees: float):
        self.degrees = degrees


class LinearBody:
    def __init__(self, base_degrees: float, degrees_per_hour: float):
        self.base_degrees = base_degrees
        self.degrees_per_hour = degrees_per_hour

    def longitude_at(self, dt: datetime) -> float:
        delta_hours = (dt - BASE_TIME).total_seconds() / 3600.0
        return ad.wrap360(self.base_degrees + self.degrees_per_hour * delta_hours)


class FakeObservation:
    def __init__(self, dt: datetime, body: LinearBody):
        self.dt = dt
        self.body = body

    def apparent(self):
        return self

    def ecliptic_latlon(self):
        return (None, FakeAngle(self.body.longitude_at(self.dt)))


class FakeEarthAt:
    def __init__(self, dt: datetime):
        self.dt = dt

    def observe(self, body: LinearBody):
        return FakeObservation(self.dt, body)


class FakeEarth:
    def at(self, dt: datetime):
        return FakeEarthAt(dt)


class FakeTimescale:
    def utc(self, year: int, month: int, day: int, hour: int, minute: int, second: int):
        return datetime(year, month, day, hour, minute, second)


@pytest.fixture
def fake_ephemeris():
    return {
        "earth": FakeEarth(),
        "sun": LinearBody(0.0, 0.0),
        "moon": LinearBody(-2.0, 15.0),
    }


@pytest.fixture
def fake_timescale():
    return FakeTimescale()


def test_refine_exact_time_reaches_second_precision(monkeypatch):
    target_time = datetime(2024, 1, 1, 12, 30, 45)
    velocity = 0.02  # degrees per second

    def fake_raw(_eph, _earth, _ts, _p1, _p2, dt):
        delta_seconds = (dt - target_time).total_seconds()
        return ad.wrap360(velocity * delta_seconds)

    monkeypatch.setattr(ad, "raw_separation_at", fake_raw)

    refined_time, _raw, delta = ad.refine_exact_time(
        {"earth": object()},
        None,
        "Sun",
        "Moon",
        0.0,
        target_time - timedelta(minutes=5),
        target_time + timedelta(minutes=5),
        refine_step_mins=5,
    )

    assert abs((refined_time - target_time).total_seconds()) <= 1
    assert delta == pytest.approx(0.0, abs=1e-6)


def test_detect_aspects_produces_precise_event(fake_ephemeris, fake_timescale):
    aspects = ad.detect_aspects(
        fake_ephemeris,
        fake_timescale,
        BASE_TIME,
        BASE_TIME + timedelta(hours=1),
        orb=1.0,
        aspect_degrees={"Conjunction": 0.0},
        planets=[("Sun", ""), ("Moon", "")],
        coarse_step_mins=60,
        refine_step_mins=5,
        merge_window_hours=0.5,
        retrograde_probe_hours=3.0,
    )

    assert len(aspects) == 1
    event = aspects[0]
    expected_time = BASE_TIME + timedelta(minutes=8)
    assert abs((event.time - expected_time).total_seconds()) <= 1
    assert event.delta <= 1.0 + 1e-6

    debug_aspects = ad.detect_aspects(
        fake_ephemeris,
        fake_timescale,
        BASE_TIME,
        BASE_TIME + timedelta(hours=1),
        orb=1.0,
        aspect_degrees={"Conjunction": 0.0},
        planets=[("Sun", ""), ("Moon", "")],
        coarse_step_mins=60,
        refine_step_mins=5,
        merge_window_hours=0.5,
        retrograde_probe_hours=3.0,
        timing_debug=True,
    )

    assert len(debug_aspects) == 1
    assert abs((debug_aspects[0].time - expected_time).total_seconds()) <= 1


def test_detect_aspects_skips_candidate_when_refined_delta_beyond_orb(monkeypatch, fake_ephemeris, fake_timescale, caplog):
    def fake_refine(_eph, _ts, _p1, _p2, _target, t1, t2, _refine, *args, **kwargs):
        midpoint = t1 + (t2 - t1) / 2
        return midpoint, 0.0, 1.5

    monkeypatch.setattr(ad, "refine_exact_time", fake_refine)

    with caplog.at_level("WARNING"):
        aspects = ad.detect_aspects(
            fake_ephemeris,
            fake_timescale,
            BASE_TIME,
            BASE_TIME + timedelta(hours=1),
            orb=1.0,
            aspect_degrees={"Conjunction": 0.0},
            planets=[("Sun", ""), ("Moon", "")],
            coarse_step_mins=60,
            refine_step_mins=5,
            merge_window_hours=0.5,
            retrograde_probe_hours=3.0,
        )

    assert not aspects
    assert any("Discarding" in record.message for record in caplog.records)


def test_detect_aspects_uses_custom_aspect_map(fake_timescale):
    eph = {
        "earth": FakeEarth(),
        "sun": LinearBody(0.0, 0.0),
        "moon": LinearBody(0.0, 90.0),  # moves fast enough to hit 45° within an hour
    }

    aspects = ad.detect_aspects(
        eph,
        fake_timescale,
        BASE_TIME,
        BASE_TIME + timedelta(hours=1),
        orb=1.0,
        aspect_degrees={"SemiSquare": 45.0},
        planets=[("Sun", ""), ("Moon", "")],
        coarse_step_mins=30,
        refine_step_mins=5,
        merge_window_hours=0.5,
        retrograde_probe_hours=3.0,
    )

    assert len(aspects) == 1
    event = aspects[0]
    assert event.aspect == "SemiSquare"
    expected_time = BASE_TIME + timedelta(minutes=30)
    assert abs((event.time - expected_time).total_seconds()) <= 60


def test_is_retrograde_detects_negative_motion():
    retro_body = LinearBody(120.0, -2.0)
    eph = {"earth": FakeEarth(), "moon": retro_body}
    ts = FakeTimescale()
    dt = BASE_TIME

    assert ad.is_retrograde(
        eph,
        eph["earth"],
        ts,
        "Moon",
        dt,
        probe_hours=3.0,
        approx_speed=2.0,
    )

    direct_body = LinearBody(45.0, 2.0)
    eph_direct = {"earth": FakeEarth(), "moon": direct_body}
    assert not ad.is_retrograde(
        eph_direct,
        eph_direct["earth"],
        ts,
        "Moon",
        dt,
        probe_hours=3.0,
        approx_speed=2.0,
    )
