"""Rave-focused narratives for the raves interpretation mode.

This module mirrors the structure of business/space_force dictionaries to deliver
rave-ready copy without touching core logic. It includes planet themes, aspect
guidance template, pair overrides, and a per-sign genre/theme map placeholder.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

from astrological_dictionaries import astrological_aspects
from daily_transit.constants import DEFAULT_PLANETS

_MAJOR_ASPECTS = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

_ADDITIONAL_ENTITIES = ["North Node", "South Node", "Chiron"]

# Optional extra fields (raves-only) are allowed in guidance entries:
# music_genre, music_subgenre, music_theme, music_style, music_speed,
# music_tone, music_vibe, outfit_cue, social_mode, friend_making_risk,
# chaos_order, safety_flag, conflict_risk, crowd_profile
_REQUIRED_GUIDANCE_KEYS = ("severity", "headline", "impact", "action", "watch", "summary")
_OPTIONAL_GUIDANCE_KEYS = (
    "music_genre",
    "music_subgenre",
    "music_theme",
    "music_style",
    "music_speed",
    "music_tone",
    "music_vibe",
    "outfit_cue",
    "social_mode",
    "friend_making_risk",
    "chaos_order",
    "safety_flag",
    "conflict_risk",
    "crowd_profile",
)

RAVES_PLANET_THEMES: Dict[str, str] = {
    "Sun": "headline energy",
    "Moon": "vibe and mood flux",
    "Mercury": "comms and meetups",
    "Venus": "aesthetic cohesion",
    "Mars": "mosh intensity and edge",
    "Jupiter": "scale and guest-list hype",
    "Saturn": "security and lines",
    "Uranus": "surprises and genre flips",
    "Neptune": "trance and dreamy flow",
    "Pluto": "deep intensity and bass weight",
    "North Node": "emerging scenes",
    "South Node": "nostalgia throwbacks",
    "Chiron": "safe healing spaces",
}


def all_raves_planets() -> Tuple[str, ...]:
    names = [name for name, _glyph in DEFAULT_PLANETS]
    for extra in _ADDITIONAL_ENTITIES:
        if extra not in names:
            names.append(extra)
    return tuple(names)


def _all_aspect_names() -> Iterable[str]:
    return sorted(astrological_aspects.get("aspect_degrees", {}).keys())


def _aspect_bucket(aspect: str) -> str:
    return "major_aspects" if aspect in _MAJOR_ASPECTS else "minor_aspects"


def _blank_entry() -> Dict[str, str]:
    return {key: "" for key in _REQUIRED_GUIDANCE_KEYS}


def _build_guidance_template() -> Dict[str, Dict[str, Dict[str, str]]]:
    mapping: Dict[str, Dict[str, Dict[str, str]]] = {"major_aspects": {}, "minor_aspects": {}}
    for aspect in _all_aspect_names():
        mapping[_aspect_bucket(aspect)][aspect] = _blank_entry()
    return mapping


raves_aspect_guidance: Dict[str, Dict[str, Dict[str, str]]] = _build_guidance_template()

# Seed major aspects with initial rave-focused copy; minors remain blank until Phase 7.2 is completed.
raves_aspect_guidance["major_aspects"]["Conjunction"] = {
    "severity": "Opportunity",
    "headline": "Peak alignment — one crew, one drop",
    "impact": "Energies fuse; shared focus amplifies the main moment and crew cohesion.",
    "action": "Lock a meetup point, set a pacing plan, and aim the crew at a headline set.",
    "watch": "Overheating or overcommitting; schedule water runs and quick breathers.",
    "summary": "Unified surge with high cohesion if you pace the hype.",
    "music_genre": "Progressive house",
    "music_vibe": "Soaring, unified, hands-up",
    "outfit_cue": "Light layers with reflective pops",
    "social_mode": "Crew-first; welcome friendly add-ons",
    "chaos_order": "Order the rush with checkpoints",
    "safety_flag": "Hydrate and ventilate",
}

raves_aspect_guidance["major_aspects"]["Opposition"] = {
    "severity": "Watch",
    "headline": "Tug-of-war energies",
    "impact": "Competing moods or agendas can split the crew between stages or styles.",
    "action": "Agree on rotation times and a midpoint meet; share pins before wandering.",
    "watch": "Mood swings and friction; avoid digging in on preferences.",
    "summary": "Balance the split so no one fragments the night.",
    "music_genre": "Breaks + techno blend",
    "music_vibe": "Edgy but playful",
    "outfit_cue": "Layered fits that move from chill to peak",
    "social_mode": "Tradeoffs and swaps; keep chat open",
    "chaos_order": "Hold a simple default plan",
    "conflict_risk": "Medium if tired or hungry",
}

raves_aspect_guidance["major_aspects"]["Trine"] = {
    "severity": "Opportunity",
    "headline": "Glide path and easy rapport",
    "impact": "Supportive flow; social openings feel natural and logistics stay smooth.",
    "action": "Float between floors, follow light serendipity, and log quick check-ins.",
    "watch": "Drift without direction; add gentle anchors (meet every hour).",
    "summary": "Light, social glide with low resistance.",
    "music_genre": "Melodic house",
    "music_vibe": "Breezy and open",
    "outfit_cue": "Breathable, easy layers",
    "social_mode": "Friendly mingling; low-pressure invites",
    "chaos_order": "Loose order with soft anchors",
}

raves_aspect_guidance["major_aspects"]["Square"] = {
    "severity": "Watch",
    "headline": "Frictive spark",
    "impact": "Tension can fuel movement or spill into agitation under crowd pressure.",
    "action": "Channel the edge into dancing; set cool-off spots and avoid bottlenecks.",
    "watch": "Short fuses and crowd squeezes; step out before it spikes.",
    "summary": "Use the heat for momentum, not conflict.",
    "music_genre": "Driving techno",
    "music_vibe": "Gritty and kinetic",
    "outfit_cue": "Sturdy shoes, sweat-ready",
    "social_mode": "Stay with trusted crew",
    "chaos_order": "Structured routes between stages",
    "safety_flag": "Identify exits and cool zones",
    "conflict_risk": "Elevated if cramped",
}

raves_aspect_guidance["major_aspects"]["Sextile"] = {
    "severity": "Opportunity",
    "headline": "Chance openings",
    "impact": "Small alignments invite quick wins—new friends, surprise sets, smooth pivots.",
    "action": "Say yes to low-cost invites; bookmark alternates so pivots stay easy.",
    "watch": "Keep an eye on time so wandering stays intentional.",
    "summary": "Light lift—easy connects and flexible choices.",
    "music_genre": "House/garage crossover",
    "music_vibe": "Buoyant and curious",
    "outfit_cue": "Comfort-first with a playful accent",
    "social_mode": "Open to quick circles",
    "chaos_order": "Loose but time-aware",
}


def _default_entry(aspect: str, bucket: str) -> Dict[str, str]:
    if bucket == "major_aspects":
        return {
            "severity": "Watch",
            "headline": f"{aspect} influence in play",
            "impact": "Energies need pacing and balance; keep the crew aligned.",
            "action": "Set checkpoints, hydrate, and stay flexible as plans shift.",
            "watch": "Overheating or drift; regroup before momentum drops.",
            "summary": f"{aspect}: steady the vibe and pace.",
        }
    return {
        "severity": "Watch",
        "headline": f"{aspect} adjustment window",
        "impact": "Subtle shifts add friction or tweaks; light steering keeps flow smooth.",
        "action": "Make small pivots, keep options open, and schedule short breathers.",
        "watch": "Notice energy dips and crowd squeeze; take breaks early.",
        "summary": "Small adjustment—flex plans and pace.",
    }


for _aspect in _all_aspect_names():
    _bucket = _aspect_bucket(_aspect)
    existing = raves_aspect_guidance.get(_bucket, {}).get(_aspect, {})
    needs_fill = not existing or any(not (existing.get(k, "").strip()) for k in _REQUIRED_GUIDANCE_KEYS)
    if needs_fill:
        raves_aspect_guidance[_bucket][_aspect] = _default_entry(_aspect, _bucket)


def _pair_key(planet_a: str, planet_b: str) -> Tuple[str, str]:
    return tuple(sorted((planet_a, planet_b)))


def _theme(planet: str) -> str:
    return RAVES_PLANET_THEMES.get(planet, planet.lower())


def default_pair_message(planet_a: str, planet_b: str) -> str:
    theme_a = _theme(planet_a)
    theme_b = _theme(planet_b)
    return f"Balance {theme_a} with {theme_b} to keep the night flowing."


raves_pair_overrides: Dict[Tuple[str, str], str] = {}
# Seed a few high-traffic pairs for future population
raves_pair_overrides[_pair_key("Sun", "Moon")] = "Sync headline energy with crowd mood; pace yourself between peaks."
raves_pair_overrides[_pair_key("Sun", "Mars")] = "Channel hype without tipping into chaos; hydrate and plan exits."
raves_pair_overrides[_pair_key("Moon", "Mars")] = "Emotions and edge run high; stay with your crew near the pit."
raves_pair_overrides[_pair_key("Sun", "Mercury")] = "Blend spotlight with comms; set clear meetup pins before splitting."
raves_pair_overrides[_pair_key("Sun", "Venus")] = "Match shine with aesthetic cohesion; avoid vanity delays when moving."
raves_pair_overrides[_pair_key("Moon", "Venus")] = "Comfort-first socializing; choose breathable spaces and kinder lighting."
raves_pair_overrides[_pair_key("Venus", "Mars")] = "Style meets edge—great for dancing; cool down before tempers spike."
raves_pair_overrides[_pair_key("Mercury", "Mars")] = "Fast chatter plus sharp energy; use simple signals to avoid snap arguments."
raves_pair_overrides[_pair_key("Venus", "Jupiter")] = "Social expansion and charm; don’t overcommit to every invite."


# Per-sign genre/theme hints (placeholder lists of ~7 entries each)
RAVES_SIGN_GENRE_MAP: Dict[str, Tuple[str, ...]] = {
    "Aries": (
        "peak-time techno",
        "hard dance",
        "drum and bass",
        "bass house",
        "industrial techno",
        "big-room",
        "trap/bass",
    ),
    "Taurus": (
        "deep house",
        "melodic techno",
        "nu-disco",
        "organic house",
        "downtempo",
        "chillhop",
        "lounge"
    ),
    "Gemini": (
        "tech house",
        "breaks",
        "garage",
        "multi-genre mashups",
        "bassline",
        "funky house",
        "electro"
    ),
    "Cancer": (
        "melodic house",
        "liquid drum and bass",
        "dreamy trance",
        "downtempo",
        "lofi",
        "ambient",
        "chillwave"
    ),
    "Leo": (
        "festival progressive house",
        "vocal trance",
        "electro house",
        "big-room",
        "disco/nu-disco",
        "future house",
        "mainstage pop-EDM"
    ),
    "Virgo": (
        "minimal techno",
        "microhouse",
        "progressive house",
        "deep tech",
        "uplifting trance",
        "breaks",
        "melodic techno"
    ),
    "Libra": (
        "classic house",
        "vocal house",
        "nu-disco",
        "melodic techno",
        "progressive house",
        "funk/disco",
        "soulful house"
    ),
    "Scorpio": (
        "dark techno",
        "industrial",
        "psytrance",
        "deep dubstep",
        "halftime",
        "dark drum and bass",
        "leftfield bass"
    ),
    "Sagittarius": (
        "psytrance",
        "goa",
        "progressive psy",
        "tribal house",
        "afro house",
        "world/bass fusion",
        "festival techno"
    ),
    "Capricorn": (
        "driving techno",
        "hardgroove",
        "classic progressive",
        "structured trance",
        "electro techno",
        "EBM",
        "warehouse house"
    ),
    "Aquarius": (
        "breakbeat",
        "leftfield bass",
        "future garage",
        "glitch hop",
        "experimental techno",
        "hyperpop",
        "idm-leaning sets"
    ),
    "Pisces": (
        "deep trance",
        "ambient",
        "liquid drum and bass",
        "downtempo",
        "organic house",
        "ethereal techno",
        "dreamy prog"
    ),
}


__all__ = [
    "RAVES_PLANET_THEMES",
    "all_raves_planets",
    "raves_aspect_guidance",
    "raves_pair_overrides",
    "default_pair_message",
    "RAVES_SIGN_GENRE_MAP",
]
