from datetime import datetime

import pytest

from daily_transit import lunar_phases
from daily_transit.lunar_phases import LunarPhaseEvent


class StubTimescale:
    def utc(self, *args):
        # The moon phase search window is opaque to our stub; returning raw tuples is sufficient
        return args


class StubAngle:
    def __init__(self, degrees: float):
        self.degrees = degrees


class StubObservation:
    def __init__(self, longitude: float):
        self._longitude = longitude

    def apparent(self):
        return self

    def ecliptic_latlon(self):
        return (None, StubAngle(self._longitude))


class StubAt:
    def __init__(self, longitude: float):
        self._longitude = longitude

    def observe(self, _moon):
        return StubObservation(self._longitude)


class StubEarth:
    def at(self, moment):
        return StubAt(moment.longitude)


class StubMoon:
    pass


class StubTime:
    def __init__(self, dt: datetime, longitude: float):
        self._dt = dt
        self.longitude = longitude

    def utc_datetime(self):
        return self._dt


@pytest.fixture
def stub_timescale():
    return StubTimescale()


def test_compute_lunar_phases_requires_earth_and_moon(stub_timescale):
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    result_missing_moon = lunar_phases.compute_lunar_phases({}, stub_timescale, start, end)
    assert result_missing_moon == []

    eph_without_moon = {"earth": StubEarth()}
    result_still_empty = lunar_phases.compute_lunar_phases(eph_without_moon, stub_timescale, start, end)
    assert result_still_empty == []


def test_compute_lunar_phases_builds_enriched_events(monkeypatch, stub_timescale):
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 3)

    event_time = datetime(2024, 1, 2, 5, 45)
    stub_time = StubTime(event_time, longitude=45.0)  # 45° → Taurus

    def fake_moon_phases(_eph):
        return "phase-function"

    def fake_find_discrete(_start, _end, _func):
        return [stub_time], [2]

    monkeypatch.setattr(lunar_phases.almanac, "moon_phases", fake_moon_phases)
    monkeypatch.setattr(lunar_phases.almanac, "find_discrete", fake_find_discrete)

    eph = {"earth": StubEarth(), "moon": StubMoon()}

    events = lunar_phases.compute_lunar_phases(eph, stub_timescale, start, end)
    assert len(events) == 1

    event = events[0]
    assert event.phase_name == "Full Moon"
    assert event.phase_symbol == "\U0001F315"
    assert pytest.approx(event.longitude) == 45.0
    assert event.zodiac_name == "Taurus"
    assert event.zodiac_symbol == "\u2649"
    assert event.cultural_name == "Wolf"


def test_format_phase_label_ascii_uses_lookup():
    event = LunarPhaseEvent(
        time=datetime(2024, 1, 1),
        phase_code=0,
        phase_name="New Moon",
        phase_symbol="\U0001F311",
        zodiac_name="Aries",
        zodiac_symbol="\u2648",
        longitude=10.0,
    )

    label = lunar_phases.format_phase_label(event, ascii_only=True)
    assert label == "New Moon"


def test_format_phase_label_unicode_includes_symbol():
    event = LunarPhaseEvent(
        time=datetime(2024, 1, 1),
        phase_code=1,
        phase_name="First Quarter",
        phase_symbol="\U0001F313",
        zodiac_name="Cancer",
        zodiac_symbol="\u264B",
        longitude=100.0,
    )

    label = lunar_phases.format_phase_label(event, ascii_only=False)
    assert label.startswith("\U0001F313")
    assert "First Quarter" in label


def test_format_phase_label_unicode_falls_back_without_symbol():
    event = LunarPhaseEvent(
        time=datetime(2024, 1, 1),
        phase_code=2,
        phase_name="Full Moon",
        phase_symbol="",
        zodiac_name="Leo",
        zodiac_symbol="\u264C",
        longitude=150.0,
    )

    label = lunar_phases.format_phase_label(event, ascii_only=False)
    assert label == "Full Moon"


def test_phase_meaning_known_code():
    event = LunarPhaseEvent(
        time=datetime(2024, 1, 1),
        phase_code=3,
        phase_name="Last Quarter",
        phase_symbol="\U0001F317",
        zodiac_name="Scorpio",
        zodiac_symbol="\u264F",
        longitude=220.0,
    )

    meaning = lunar_phases.phase_meaning(event)
    assert "Release" in meaning or "release" in meaning


def test_phase_meaning_unknown_code_uses_default():
    event = LunarPhaseEvent(
        time=datetime(2024, 1, 1),
        phase_code=99,
        phase_name="Mystery",
        phase_symbol="",
        zodiac_name="Aries",
        zodiac_symbol="\u2648",
        longitude=0.0,
    )

    meaning = lunar_phases.phase_meaning(event)
    assert meaning == "Key moment within the lunar cycle."
