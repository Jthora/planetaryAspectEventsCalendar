from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

# Normalize alternate aspect names to canonical keys used in dictionaries/catalogs.
_ASPECT_ALIASES: Dict[str, str] = {
    "Semi-Sextile": "Semisextile",
    "SemiSquare": "Semisquare",
    "Semiquintile": "Decile",  # alias to legacy naming
    "Decile": "Decile",
    "Trebiquintile": "Tredecile",
    "Sesquiquintile": "Biquintile",  # documented as equivalent
    "Semi-Septile": "Quattuordecile",
    "Septuagenary": "Quattuordecile",
    "Semi-Octile": "Semi-Octile",
    "Sesqui-Octile": "Sesqui-Octile",
}

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
    from daily_transit.standard_guidance import standard_aspect_guidance
except ImportError:  # pragma: no cover - default to empty standard dictionaries
    standard_aspect_guidance = {"major_aspects": {}, "minor_aspects": {}, "tertiary_aspects": {}}

try:
    from astrological_business_dictionaries import (
        PLANET_THEMES,
        business_aspect_guidance,
        business_pair_overrides,
        default_pair_message as business_default_pair_message,
    )
except ImportError:  # pragma: no cover - default to empty business dictionaries
    PLANET_THEMES = {}
    business_aspect_guidance = {"major_aspects": {}, "minor_aspects": {}}
    business_pair_overrides: Dict[Tuple[str, str], str] = {}

    def business_default_pair_message(planet_a: str, planet_b: str) -> str:  # type: ignore[no-redef]
        return ""

try:
    from astrological_spaceforce_dictionaries import (
        SPACEFORCE_PLANET_THEMES,
        default_pair_message as spaceforce_default_pair_message,
        spaceforce_aspect_guidance,
        spaceforce_pair_overrides,
    )
except ImportError:  # pragma: no cover - default to empty spaceforce dictionaries
    SPACEFORCE_PLANET_THEMES = {}
    spaceforce_aspect_guidance = {"major_aspects": {}, "minor_aspects": {}}
    spaceforce_pair_overrides: Dict[Tuple[str, str], str] = {}

    def spaceforce_default_pair_message(planet_a: str, planet_b: str) -> str:  # type: ignore[no-redef]
        return ""

try:
    from astrological_raves_dictionaries import (
        RAVES_PLANET_THEMES,
        default_pair_message as raves_default_pair_message,
        raves_aspect_guidance,
        raves_pair_overrides,
    )
except ImportError:  # pragma: no cover - default to empty raves dictionaries
    RAVES_PLANET_THEMES = {}
    raves_aspect_guidance = {"major_aspects": {}, "minor_aspects": {}}
    raves_pair_overrides: Dict[Tuple[str, str], str] = {}

    def raves_default_pair_message(planet_a: str, planet_b: str) -> str:  # type: ignore[no-redef]
        return ""


@dataclass
class InterpretationResult:
    summary: str
    detail_lines: List[str]
    extras: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class StructuredModeResources:
    name: str
    aspect_guidance: Dict[str, Dict[str, Dict[str, str]]]
    planet_themes: Dict[str, str]
    pair_overrides: Dict[Tuple[str, str], str]
    default_pair_message: Callable[[str, str], str]
    major_aspects: Tuple[str, ...]
    minor_aspects: Tuple[str, ...]
    tertiary_aspects: Tuple[str, ...]


_ALLOWED_SEVERITIES = {"Opportunity", "Watch", "High Risk", "Info"}
_OPTIONAL_EXTRA_FIELDS = (
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


def _build_structured_resources(
    name: str,
    aspect_guidance: Dict[str, Dict[str, Dict[str, str]]],
    planet_themes: Dict[str, str],
    pair_overrides: Dict[Tuple[str, str], str],
    default_pair_message: Callable[[str, str], str],
) -> StructuredModeResources:
    major = tuple(sorted(aspect_guidance.get("major_aspects", {}).keys())) or tuple(sorted(_MAJOR_FALLBACK))
    minor = tuple(sorted(aspect_guidance.get("minor_aspects", {}).keys()))
    tertiary = tuple(sorted(aspect_guidance.get("tertiary_aspects", {}).keys()))
    return StructuredModeResources(
        name=name,
        aspect_guidance=aspect_guidance,
        planet_themes=planet_themes,
        pair_overrides=pair_overrides,
        default_pair_message=default_pair_message,
        major_aspects=major,
        minor_aspects=minor,
        tertiary_aspects=tertiary,
    )


_STRUCTURED_MODE_RESOURCES: Dict[str, StructuredModeResources] = {}

_STRUCTURED_MODE_RESOURCES["standard"] = _build_structured_resources(
    "standard",
    standard_aspect_guidance,
    PLANET_THEMES,
    {},
    business_default_pair_message,
)

_STRUCTURED_MODE_RESOURCES["business"] = _build_structured_resources(
    "business",
    business_aspect_guidance,
    PLANET_THEMES,
    business_pair_overrides,
    business_default_pair_message,
)

_STRUCTURED_MODE_RESOURCES["space_force"] = _build_structured_resources(
    "space_force",
    spaceforce_aspect_guidance,
    SPACEFORCE_PLANET_THEMES,
    spaceforce_pair_overrides,
    spaceforce_default_pair_message,
)

_STRUCTURED_MODE_RESOURCES["raves"] = _build_structured_resources(
    "raves",
    raves_aspect_guidance,
    RAVES_PLANET_THEMES,
    raves_pair_overrides,
    raves_default_pair_message,
)

_PLANET_THEME_MAP: Dict[str, Dict[str, str]] = {
    "standard": PLANET_THEMES,
    "business": PLANET_THEMES,
    "space_force": SPACEFORCE_PLANET_THEMES,
    "raves": RAVES_PLANET_THEMES,
}


def planet_themes_for_mode(mode: str) -> Dict[str, str]:
    return _PLANET_THEME_MAP.get(mode) or PLANET_THEMES


def _format_summary(text: str) -> str:
    trimmed = text.strip()
    if len(trimmed) > 120:
        return trimmed[:117].rstrip() + "..."
    return trimmed


def _normalize_aspect_name(aspect_name: str) -> str:
    return _ASPECT_ALIASES.get(aspect_name, aspect_name)


def _structured_bucket_name(resources: StructuredModeResources, aspect_name: str) -> Optional[str]:
    if aspect_name in resources.major_aspects:
        return "major_aspects"
    if aspect_name in resources.minor_aspects:
        return "minor_aspects"
    if aspect_name in getattr(resources, "tertiary_aspects", ()):  # safety for older resources
        return "tertiary_aspects"
    return None


def _structured_guidance_entry(resources: StructuredModeResources, aspect_name: str) -> Optional[Dict[str, str]]:
    normalized = _normalize_aspect_name(aspect_name)
    bucket = _structured_bucket_name(resources, normalized)
    if not bucket:
        return None
    entry = resources.aspect_guidance.get(bucket, {}).get(normalized)
    if not entry:
        return None
    if not any(entry.get(field, "").strip() for field in ("headline", "impact", "action")):
        return None
    return entry


def _pair_insight(resources: StructuredModeResources, planet1: str, planet2: str) -> str:
    key = tuple(sorted((planet1, planet2)))
    direct = resources.pair_overrides.get(key)
    if direct:
        return direct
    fallback = resources.default_pair_message(planet1, planet2)
    if fallback:
        return fallback
    theme1 = resources.planet_themes.get(planet1, planet1.lower())
    theme2 = resources.planet_themes.get(planet2, planet2.lower())
    return f"Balance {theme1} with {theme2} to keep the strategic posture coherent."


def _generate_structured_interpretation(
    resources: StructuredModeResources,
    aspect_name: str,
    planet1: str,
    planet2: str,
) -> InterpretationResult:
    normalized_name = _normalize_aspect_name(aspect_name)
    guidance = _structured_guidance_entry(resources, normalized_name)
    extras: Dict[str, str] = {}

    if not guidance:
        meaning_map = astrological_aspects.get("aspect_meanings", {})
        meaning = meaning_map.get(normalized_name) or meaning_map.get(aspect_name)
        headline = meaning or f"{aspect_name} aspect active — guidance pending."
        summary = _format_summary(meaning or f"Info — {aspect_name} influence tracked; default guidance applied.")
        lines = [f"[Info] {headline}"]
        if meaning:
            lines.append(f"Why it matters: {meaning}")
        else:
            lines.append("Why it matters: Monitor this transit using standard frameworks until guidance is authored.")
    else:
        severity = guidance.get("severity", "Watch").strip() or "Watch"
        if severity not in _ALLOWED_SEVERITIES:
            severity = "Watch"
        badge = f"[{severity}]"
        headline_text = guidance.get("headline", "").strip()
        impact_text = guidance.get("impact", "").strip()
        action_text = guidance.get("action", "").strip()
        watch_text = guidance.get("watch", "").strip()

        lines = [f"{badge} {headline_text}".strip() if headline_text else badge]
        if impact_text:
            lines.append(f"Why it matters: {impact_text}")
        if action_text:
            lines.append(f"Action: {action_text}")
        if watch_text:
            lines.append(f"Watch: {watch_text}")

        computed_summary = guidance.get("summary", "").strip() or headline_text or impact_text or action_text
        summary = _format_summary(computed_summary or f"{aspect_name} impact in focus.")

        extras = {
            key: guidance.get(key, "").strip()
            for key in _OPTIONAL_EXTRA_FIELDS
            if guidance.get(key, "").strip()
        }

    pair_text = _pair_insight(resources, planet1, planet2)
    if pair_text:
        lines.extend(["", f"Interaction Insight: {pair_text}"])

    if len(lines) == 1:
        lines.append("Why it matters: Guidance pending development.")

    return InterpretationResult(summary=summary, detail_lines=lines, extras=extras)


def generate_business_interpretation(aspect_name: str, planet1: str, planet2: str) -> InterpretationResult:
    resources = _STRUCTURED_MODE_RESOURCES.get("business")
    if not resources:
        return generate_standard_interpretation(aspect_name, astrological_aspects.get("aspect_meanings", {}))
    return _generate_structured_interpretation(resources, aspect_name, planet1, planet2)


def generate_spaceforce_interpretation(aspect_name: str, planet1: str, planet2: str) -> InterpretationResult:
    resources = _STRUCTURED_MODE_RESOURCES.get("space_force")
    if not resources:
        return generate_standard_interpretation(aspect_name, astrological_aspects.get("aspect_meanings", {}))
    return _generate_structured_interpretation(resources, aspect_name, planet1, planet2)


def generate_raves_interpretation(aspect_name: str, planet1: str, planet2: str) -> InterpretationResult:
    resources = _STRUCTURED_MODE_RESOURCES.get("raves")
    if not resources:
        return generate_standard_interpretation(aspect_name, astrological_aspects.get("aspect_meanings", {}))
    return _generate_structured_interpretation(resources, aspect_name, planet1, planet2)


def generate_standard_interpretation(
    aspect_name: str,
    aspect_meanings: Dict[str, str],
) -> InterpretationResult:
    meaning = aspect_meanings.get(aspect_name, "").strip()
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
    resources = _STRUCTURED_MODE_RESOURCES.get(mode)
    if resources:
        return _generate_structured_interpretation(resources, aspect_name, planet1, planet2)
    return generate_standard_interpretation(aspect_name, aspect_meanings)
