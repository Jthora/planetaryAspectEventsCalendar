from datetime import datetime
from typing import Dict

import pytz

from daily_transit import ics_builder, interpretations
from daily_transit.aspect_detection import AspectEvent
from daily_transit.zodiac_metadata import PlanetZodiacInfo, SignMetadata

UTC = pytz.timezone("UTC")
PLANETS = [
    ("Sun", "\u2609"),
    ("Moon", "\u263D"),
]
MEANINGS = {"Conjunction": "Fusion"}


def _sample_aspect_event() -> AspectEvent:
    return AspectEvent(
        time=datetime(2025, 2, 2, 2, 0),
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


def _configure_raves(monkeypatch, guidance, themes=None, pair_overrides=None, default_pair=None):
    themes = themes or {}
    pair_overrides = pair_overrides or {}
    default_pair = default_pair or (lambda a, b: "Sync the vibe together.")
    resources = interpretations._build_structured_resources(  # type: ignore[attr-defined]
        "raves",
        guidance,
        themes,
        pair_overrides,
        default_pair,
    )
    monkeypatch.setitem(interpretations._STRUCTURED_MODE_RESOURCES, "raves", resources)
    monkeypatch.setitem(interpretations._PLANET_THEME_MAP, "raves", themes)


def test_raves_aspect_event_includes_extras_block(monkeypatch):
    guidance = {
        "major_aspects": {
            "Conjunction": {
                "severity": "Opportunity",
                "headline": "Peak alignment",
                "impact": "Shared build toward the same drop.",
                "action": "Anchor a shared meetup spot before the rush.",
                "watch": "Keep pacing steady so the night lasts.",
                "summary": "Crew cohesion with upbeat momentum.",
                "music_genre": "House",
                "music_vibe": "Playful and bright",
                "outfit_cue": "Comfortable layers with reflective accents",
                "social_mode": "Invite new friends into the circle",
            }
        },
        "minor_aspects": {},
    }
    _configure_raves(
        monkeypatch,
        guidance,
        themes={"Sun": "spotlight", "Moon": "intuition"},
        pair_overrides={("Moon", "Sun"): "Blend spotlight and intuition without losing grounding."},
    )

    aspect = _sample_aspect_event()
    context = _zodiac_context()
    event = ics_builder.build_aspect_event(
        aspect,
        UTC,
        status="CONFIRMED",
        thunderbird=False,
        planets=PLANETS,
        aspect_meanings=MEANINGS,
        interpretation_mode="raves",
        ascii_only=True,
        zodiac_context=context,
    )

    description = event.description
    assert "Rave Extras:" in description
    assert "Music genre: House" in description
    assert "Outfit: Comfortable layers" in description
    assert "Interaction Insight" in description
    assert "Element focus: high-octane hype" in description
    assert "Modality focus: kickoff energy" in description


def test_raves_extras_block_omitted_when_empty(monkeypatch):
    guidance = {
        "major_aspects": {
            "Conjunction": {
                "severity": "Watch",
                "headline": "Quiet alignment",
                "impact": "Subtle sync without the extras.",
                "action": "Keep plans simple.",
                "watch": "Notice mood shifts.",
                "summary": "Low-key connection without decoration.",
            }
        },
        "minor_aspects": {},
    }
    _configure_raves(monkeypatch, guidance, themes={"Sun": "spotlight"})

    aspect = _sample_aspect_event()
    event = ics_builder.build_aspect_event(
        aspect,
        UTC,
        status="CONFIRMED",
        thunderbird=False,
        planets=PLANETS,
        aspect_meanings=MEANINGS,
        interpretation_mode="raves",
        ascii_only=True,
        zodiac_context=_zodiac_context(),
    )

    description = event.description
    assert "Rave Extras:" not in description
    assert "Interaction Insight" in description
