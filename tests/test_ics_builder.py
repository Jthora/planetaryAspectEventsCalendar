from datetime import datetime
import hashlib
from typing import Dict

import pytz
from pytest import MonkeyPatch

from daily_transit import ics_builder
from daily_transit.aspect_detection import AspectEvent
from daily_transit.ics_builder import (
    build_aspect_event,
    build_daily_summary,
    build_lunar_phase_event,
)
from daily_transit.zodiac_metadata import PlanetZodiacInfo, SignMetadata
from daily_transit.lunar_phases import LunarPhaseEvent


UTC = pytz.timezone("UTC")
PLANETS = [
    ("Sun", "\u2609"),
    ("Moon", "\u263D"),
    ("Mercury", "\u263F"),
]
MEANINGS = {"Conjunction": "Fusion"}


def _sample_aspect_event() -> AspectEvent:
    return AspectEvent(
        time=datetime(2025, 1, 1, 4, 15),
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )


def _sign_metadata(sign: str) -> SignMetadata:
    return SignMetadata(
        name=sign,
        emoji="",
        element_name="Fire",
        element_glyph="",
        element_color_emoji="",
        element_color_name="Red",
        modality_name="Cardinal",
        modality_symbol="▲",
        left_framing="<",
        right_framing=">",
    )


def _zodiac_context() -> Dict[str, PlanetZodiacInfo]:
    meta = _sign_metadata("Aries")
    return {
        "Sun": PlanetZodiacInfo("Sun", 0.0, "Aries", meta),
        "Moon": PlanetZodiacInfo("Moon", 12.0, "Aries", meta),
    }


def md5_uid(planet1: str, planet2: str, aspect: str, dt: datetime) -> str:
    payload = f"{planet1}-{planet2}-{aspect}-{dt.strftime('%Y%m%d%H%M')}"
    return hashlib.md5(payload.encode()).hexdigest() + "@transit-aspect"


def test_build_aspect_event_produces_deterministic_uid():
    event_time = datetime(2024, 1, 2, 3, 4)
    aspect = AspectEvent(
        time=event_time,
        planet1="Sun",
        planet2="Mercury",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    first = build_aspect_event(aspect, UTC, "CONFIRMED", False, PLANETS, MEANINGS, False)
    second = build_aspect_event(aspect, UTC, "CONFIRMED", True, PLANETS, MEANINGS, False)

    expected_uid = md5_uid("Sun", "Mercury", "Conjunction", event_time)
    assert first.uid == expected_uid
    assert second.uid == expected_uid


def test_build_daily_summary_sets_uid_by_date(monkeypatch: MonkeyPatch):
    when = datetime(2024, 1, 1)

    monkeypatch.setattr(ics_builder, "compute_body_longitudes", lambda *args, **kwargs: {})

    event = build_daily_summary(
        when,
        UTC,
        eph=None,
        ts=None,
        aspects_today=[],
        status="CONFIRMED",
        thunderbird=False,
        planets=PLANETS,
        aspect_meanings=MEANINGS,
        ascii_only=True,
    )

    assert event.uid.endswith("@transit-daily")
    assert event.name == "Daily Transit Chart 2024-01-01"


def test_spaceforce_aspect_event_embeds_spaceforce_copy():
    aspect = _sample_aspect_event()
    event = build_aspect_event(
        aspect,
        UTC,
        "CONFIRMED",
        False,
        PLANETS,
        MEANINGS,
        interpretation_mode="space_force",
        ascii_only=True,
        zodiac_context={},
    )

    description = event.description
    assert "[Opportunity]" in description
    assert "Command vectors align" in description
    assert "Interaction Insight" in description


def test_spaceforce_daily_summary_lists_spaceforce_summary(monkeypatch: MonkeyPatch):
    aspect = _sample_aspect_event()
    when = aspect.time

    monkeypatch.setattr(ics_builder, "compute_body_longitudes", lambda *args, **kwargs: {})

    event = build_daily_summary(
        when,
        UTC,
        eph=None,
        ts=None,
        aspects_today=[aspect],
        status="CONFIRMED",
        thunderbird=False,
        planets=PLANETS,
        aspect_meanings=MEANINGS,
        interpretation_mode="space_force",
        ascii_only=True,
    )

    assert "Opportunity — command unity boosts throughput" in event.description


def test_spaceforce_planet_profiles_use_spaceforce_themes():
    aspect = _sample_aspect_event()
    context = _zodiac_context()

    event = build_aspect_event(
        aspect,
        UTC,
        "CONFIRMED",
        False,
        PLANETS,
        MEANINGS,
        interpretation_mode="space_force",
        ascii_only=True,
        zodiac_context=context,
    )

    description = event.description
    assert "Planet Profiles:" in description
    assert "command authority" in description
    assert "crew morale telemetry" in description


def test_build_lunar_phase_event_uid():
    phase = LunarPhaseEvent(
        time=datetime(2024, 1, 4, 3, 30),
        phase_code=3,
        phase_name="Last Quarter",
        phase_symbol="\U0001F317",
        zodiac_name="Libra",
        zodiac_symbol="\u264E",
        longitude=192.5,
        cultural_name=None,
    )

    event = build_lunar_phase_event(phase, UTC, "CONFIRMED", False, False)
    assert event.uid.endswith("@transit-lunar-phase")
    assert "Last Quarter" in event.name
