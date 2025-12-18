from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional

try:  # pragma: no cover - external dependency may not be present in tests
    from GalacticCenterAyanamsa import ZODIAC_SIGNS_EMOJI_AND_SYMBOLS
except ImportError:  # pragma: no cover
    ZODIAC_SIGNS_EMOJI_AND_SYMBOLS = {}

_ZODIAC_SEQUENCE: Iterable[str] = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

_LEFT_FRAMING: Mapping[str, str] = {
    "Aries": "<",
    "Taurus": "]|",
    "Gemini": "(|",
    "Cancer": ">",
    "Leo": "[",
    "Virgo": ")|",
    "Libra": "<|",
    "Scorpio": "]",
    "Sagittarius": "(",
    "Capricorn": ">|",
    "Aquarius": "[|",
    "Pisces": ")",
}

_RIGHT_FRAMING: Mapping[str, str] = {
    "Aries": ">",
    "Taurus": "|[",
    "Gemini": "|)",
    "Cancer": "<",
    "Leo": "]",
    "Virgo": "|(",
    "Libra": "|>",
    "Scorpio": "[",
    "Sagittarius": ")",
    "Capricorn": "|<",
    "Aquarius": "|]",
    "Pisces": "(",
}

_ELEMENT_COLOR_NAMES: Mapping[str, str] = {
    "Fire": "Red",
    "Earth": "Green",
    "Air": "Yellow",
    "Water": "Blue",
}

_ELEMENT_BUSINESS_TONES: Mapping[str, str] = {
    "Fire": "ignites urgency and spotlights initiatives that need bold advocacy.",
    "Earth": "demands measurable traction, compliance, and resource stewardship.",
    "Air": "accelerates communication, alignment, and multi-channel storytelling.",
    "Water": "deepens empathy, morale, and stakeholder trust across teams.",
}

_MODALITY_BUSINESS_TONES: Mapping[str, str] = {
    "Cardinal": "requires rapid kick-off, leadership alignment, and decisive prioritisation.",
    "Fixed": "stabilises commitments, enforces follow-through, and protects compounding value.",
    "Mutable": "keeps plans flexible, encourages iteration, and rewards adaptive playbooks.",
}

_SIGN_BUSINESS_TONES: Mapping[str, str] = {
    "Aries": "fuels first-mover instincts and rewards competitive courage.",
    "Taurus": "anchors the agenda in tangible results and patient capital deployment.",
    "Gemini": "opens new information channels and invites cross-functional dialogue.",
    "Cancer": "prioritises stakeholder care, retention, and protective risk buffers.",
    "Leo": "spotlights bold leadership, recognition cycles, and creative expression.",
    "Virgo": "sharpens precision, analytics, and process optimisation efforts.",
    "Libra": "increases partnership leverage and insists on consensus-oriented governance.",
    "Scorpio": "surfaces hidden leverage, reshapes power maps, and pushes for transformative deals.",
    "Sagittarius": "expands strategic horizons through exploration and visionary storytelling.",
    "Capricorn": "tightens executive control, fiscal discipline, and long-range planning.",
    "Aquarius": "champions innovation, network effects, and system-wide reinvention.",
    "Pisces": "amplifies empathy-driven strategy, intuition, and creative problem solving.",
}

_ASCII_MODALITY_SHAPES: Mapping[str, str] = {
    "Cardinal": "Triangle",
    "Fixed": "Square",
    "Mutable": "Circle",
}

@dataclass(frozen=True)
class SignMetadata:
    name: str
    emoji: str
    element_name: str
    element_glyph: str
    element_color_emoji: str
    element_color_name: str
    modality_name: str
    modality_symbol: str
    left_framing: str
    right_framing: str


@dataclass(frozen=True)
class PlanetZodiacInfo:
    planet: str
    longitude: float
    sign: str
    metadata: SignMetadata


def sign_from_longitude(angle: float) -> str:
    normalised = angle % 360.0
    index = int(normalised // 30)
    return list(_ZODIAC_SEQUENCE)[index]


def _raw_sign_metadata(sign: str) -> Dict[str, str]:
    fallback = {
        "symbol": "",
        "zodiac_element_glyph": "",
        "element_emoji": "",
        "modality_and_element": "Cardinal Fire",
        "modality_symbol": "▲",
    }
    return {**fallback, **ZODIAC_SIGNS_EMOJI_AND_SYMBOLS.get(sign, {})}


def get_sign_metadata(sign: str) -> SignMetadata:
    data = _raw_sign_metadata(sign)
    modality_element = data.get("modality_and_element", "Cardinal Fire").split()
    modality = modality_element[0]
    element = modality_element[-1]
    element_color_name = _ELEMENT_COLOR_NAMES.get(element, "")
    return SignMetadata(
        name=sign,
        emoji=data.get("symbol", ""),
        element_name=element,
        element_glyph=data.get("zodiac_element_glyph", ""),
        element_color_emoji=data.get("color_code", ""),
        element_color_name=element_color_name,
        modality_name=modality,
        modality_symbol=data.get("modality_symbol", ""),
        left_framing=_LEFT_FRAMING.get(sign, ""),
        right_framing=_RIGHT_FRAMING.get(sign, ""),
    )


def build_context_from_longitudes(longitudes: Mapping[str, float]) -> Dict[str, PlanetZodiacInfo]:
    context: Dict[str, PlanetZodiacInfo] = {}
    for planet, longitude in longitudes.items():
        sign = sign_from_longitude(longitude)
        context[planet] = PlanetZodiacInfo(
            planet=planet,
            longitude=longitude,
            sign=sign,
            metadata=get_sign_metadata(sign),
        )
    return context


def element_business_tone(element: str) -> str:
    return _ELEMENT_BUSINESS_TONES.get(element, "supports evolving priorities.")


def modality_business_tone(modality: str) -> str:
    return _MODALITY_BUSINESS_TONES.get(modality, "keeps work dynamic and situational.")


def sign_business_tone(sign: str) -> str:
    return _SIGN_BUSINESS_TONES.get(sign, "encourages adaptive leadership choices.")


def ascii_modality_shape(modality: str) -> str:
    return _ASCII_MODALITY_SHAPES.get(modality, modality)
