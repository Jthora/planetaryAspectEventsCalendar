from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

_MAJOR_FALLBACK = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

try:
    from astrological_dictionaries import astrological_aspects
except ImportError:  # pragma: no cover - fall back to minimal dictionaries
    astrological_aspects = {
        "aspect_meanings": {
            "Conjunction": "Fusion / concentrated focus of energies.",
            "Opposition": "Polarity seeking balance / awareness.",
            "Trine": "Ease, flow, supportive harmony.",
            "Square": "Dynamic tension prompting action.",
            "Sextile": "Opportunity requiring conscious activation.",
        }
    }

try:
    from astrological_business_dictionaries import (
        business_aspect_context,
        business_aspect_behavior,
        business_aspect_action,
        business_planet_context,
        business_planet_behavior,
        business_planet_action,
        business_planet_interactions,
    )
except ImportError:  # pragma: no cover - default to empty business dictionaries
    business_aspect_context = {"major_aspects": {}, "minor_aspects": {}}
    business_aspect_behavior = {"major_aspects": {}, "minor_aspects": {}}
    business_aspect_action = {"major_aspects": {}, "minor_aspects": {}}
    business_planet_context = {}
    business_planet_behavior = {}
    business_planet_action = {}
    business_planet_interactions = {}

try:
    from astrological_dictionaries import (
        astrological_aspects_market_analysis_context as legacy_aspect_context,
        astrological_aspects_market_analysis_behavior as legacy_aspect_behavior,
        astrological_aspects_market_analysis_action as legacy_aspect_action,
        planetary_context as legacy_planet_context,
        planetary_behavior as legacy_planet_behavior,
        planetary_action as legacy_planet_action,
        planetary_context_interactions as legacy_planet_interactions,
    )
except ImportError:  # pragma: no cover - keep legacy fallbacks empty
    legacy_aspect_context = {"major_aspects": {}, "minor_aspects": {}}
    legacy_aspect_behavior = {"major_aspects": {}, "minor_aspects": {}}
    legacy_aspect_action = {"major_aspects": {}, "minor_aspects": {}}
    legacy_planet_context = {}
    legacy_planet_behavior = {}
    legacy_planet_action = {}
    legacy_planet_interactions = {}


@dataclass
class InterpretationResult:
    summary: str
    detail_lines: List[str]


_ASPECT_CONTEXT_PRIMARY = business_aspect_context
_ASPECT_BEHAVIOR_PRIMARY = business_aspect_behavior
_ASPECT_ACTION_PRIMARY = business_aspect_action

_ASPECT_CONTEXT_FALLBACK = legacy_aspect_context
_ASPECT_BEHAVIOR_FALLBACK = legacy_aspect_behavior
_ASPECT_ACTION_FALLBACK = legacy_aspect_action

_PLANET_CONTEXT_PRIMARY = business_planet_context
_PLANET_BEHAVIOR_PRIMARY = business_planet_behavior
_PLANET_ACTION_PRIMARY = business_planet_action

_PLANET_CONTEXT_FALLBACK = legacy_planet_context
_PLANET_BEHAVIOR_FALLBACK = legacy_planet_behavior
_PLANET_ACTION_FALLBACK = legacy_planet_action

_PLANET_INTERACTIONS_PRIMARY = business_planet_interactions
_PLANET_INTERACTIONS_FALLBACK = legacy_planet_interactions

_BUSINESS_MAJOR = set(_ASPECT_CONTEXT_PRIMARY.get("major_aspects", {}).keys()) or set(
    _ASPECT_CONTEXT_FALLBACK.get("major_aspects", {}).keys()
) or _MAJOR_FALLBACK
_BUSINESS_MINOR = set(_ASPECT_CONTEXT_PRIMARY.get("minor_aspects", {}).keys()) or set(
    _ASPECT_CONTEXT_FALLBACK.get("minor_aspects", {}).keys()
)


def _aspect_tier(aspect_name: str) -> Optional[str]:
    if aspect_name in _BUSINESS_MAJOR:
        return "major"
    if aspect_name in _BUSINESS_MINOR:
        return "minor"
    return None


def _lookup_market(dictionary: Dict[str, Dict[str, str]], tier: Optional[str], aspect_name: str) -> str:
    if not dictionary or not tier:
        return ""
    tier_key = f"{tier}_aspects"
    tier_dict = dictionary.get(tier_key, {})
    return tier_dict.get(aspect_name, "")


def _resolve_market_text(
    primary: Dict[str, Dict[str, str]],
    fallback: Dict[str, Dict[str, str]],
    tier: Optional[str],
    aspect_name: str,
) -> str:
    text = _lookup_market(primary, tier, aspect_name)
    if text:
        return text
    return _lookup_market(fallback, tier, aspect_name)


def _clean(text: Optional[str]) -> str:
    return text.strip() if text else ""


def _lookup_combo(planet1: str, planet2: str) -> str:
    primary = _PLANET_INTERACTIONS_PRIMARY.get(planet1, {})
    combo = primary.get(planet2)
    if combo:
        return combo
    secondary = _PLANET_INTERACTIONS_PRIMARY.get(planet2, {})
    if secondary and planet1 in secondary:
        return secondary.get(planet1, "")
    fallback_primary = _PLANET_INTERACTIONS_FALLBACK.get(planet1, {})
    combo = fallback_primary.get(planet2)
    if combo:
        return combo
    fallback_secondary = _PLANET_INTERACTIONS_FALLBACK.get(planet2, {})
    return fallback_secondary.get(planet1, "")


def _planetary_section(
    title: str,
    planet1: str,
    planet2: str,
    primary: Dict[str, str],
    fallback: Dict[str, str],
) -> List[str]:
    lines: List[str] = []
    p1 = _clean(primary.get(planet1)) or _clean(fallback.get(planet1))
    p2 = _clean(primary.get(planet2)) or _clean(fallback.get(planet2))
    if p1 or p2:
        lines.append(title)
        if p1:
            lines.append(f"  {planet1}: {p1}")
        if p2:
            lines.append(f"  {planet2}: {p2}")
    return lines


def generate_business_interpretation(aspect_name: str, planet1: str, planet2: str) -> InterpretationResult:
    tier = _aspect_tier(aspect_name)
    context_text = _clean(
        _resolve_market_text(_ASPECT_CONTEXT_PRIMARY, _ASPECT_CONTEXT_FALLBACK, tier, aspect_name)
    )
    behavior_text = _clean(
        _resolve_market_text(_ASPECT_BEHAVIOR_PRIMARY, _ASPECT_BEHAVIOR_FALLBACK, tier, aspect_name)
    )
    action_text = _clean(
        _resolve_market_text(_ASPECT_ACTION_PRIMARY, _ASPECT_ACTION_FALLBACK, tier, aspect_name)
    )

    lines: List[str] = ["Market Interpretation:"]
    if context_text:
        lines.append(f"  Context: {context_text}")
    if behavior_text:
        lines.append(f"  Behavior: {behavior_text}")
    if action_text:
        lines.append(f"  Action: {action_text}")

    planet_lines: List[str] = []
    planet_lines.extend(
        _planetary_section(
            "Planetary Context:",
            planet1,
            planet2,
            _PLANET_CONTEXT_PRIMARY,
            _PLANET_CONTEXT_FALLBACK,
        )
    )
    planet_lines.extend(
        _planetary_section(
            "Planetary Behavior:",
            planet1,
            planet2,
            _PLANET_BEHAVIOR_PRIMARY,
            _PLANET_BEHAVIOR_FALLBACK,
        )
    )
    planet_lines.extend(
        _planetary_section(
            "Planetary Action:",
            planet1,
            planet2,
            _PLANET_ACTION_PRIMARY,
            _PLANET_ACTION_FALLBACK,
        )
    )

    combo_text = _clean(_lookup_combo(planet1, planet2))
    if combo_text:
        planet_lines.append("Interaction Dynamics:")
        planet_lines.append(f"  {planet1} & {planet2}: {combo_text}")

    if planet_lines:
        lines.extend(["", *planet_lines])

    summary_base = context_text or behavior_text or action_text
    if not summary_base:
        summary_base = f"{aspect_name} aspect influencing strategic market moves."

    if len(lines) == 1:  # Only header present, add fallback line
        lines.append("  Insight: No dedicated market interpretation available.")

    return InterpretationResult(summary=summary_base, detail_lines=lines)


def generate_standard_interpretation(
    aspect_name: str,
    aspect_meanings: Dict[str, str],
) -> InterpretationResult:
    meaning = _clean(aspect_meanings.get(aspect_name, ""))
    if not meaning:
        meaning = "No meaning available."
    detail_lines = [f"Meaning: {meaning}"]
    return InterpretationResult(summary=meaning, detail_lines=detail_lines)


def get_interpretation(
    mode: str,
    aspect_name: str,
    planet1: str,
    planet2: str,
    aspect_meanings: Dict[str, str],
) -> InterpretationResult:
    if mode == "business":
        return generate_business_interpretation(aspect_name, planet1, planet2)
    return generate_standard_interpretation(aspect_name, aspect_meanings)
