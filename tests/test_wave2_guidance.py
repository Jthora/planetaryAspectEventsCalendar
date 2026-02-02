from __future__ import annotations

from daily_transit import interpretations
from astrological_dictionaries import astrological_aspects


WAVE2_ASPECTS = ["Quintile", "Biquintile", "Decile", "Tredecile"]
ALIASES = ["Semiquintile", "Sesquiquintile", "Trebiquintile"]
MODES = ["standard", "business", "space_force", "raves"]


def _assert_non_empty(result):
    assert result.summary.strip(), "Summary should not be empty"
    joined = " ".join(result.detail_lines)
    assert joined.strip(), "Detail lines should not be empty"


def test_wave2_guidance_non_empty_across_modes():
    for mode in MODES:
        for aspect in WAVE2_ASPECTS:
            res = interpretations.get_interpretation(
                mode=mode,
                aspect_name=aspect,
                planet1="Sun",
                planet2="Venus",
                aspect_meanings=astrological_aspects.get("aspect_meanings", {}),
            )
            _assert_non_empty(res)
            first = res.detail_lines[0]
            assert first.startswith("[") and "]" in first, f"Missing severity badge for {mode} {aspect}: {first}"


def test_wave2_aliases_resolve_to_guidance():
    for alias in ALIASES:
        res = interpretations.get_interpretation(
            mode="standard",
            aspect_name=alias,
            planet1="Sun",
            planet2="Mercury",
            aspect_meanings=astrological_aspects.get("aspect_meanings", {}),
        )
        _assert_non_empty(res)
        first = res.detail_lines[0]
        assert first.startswith("[") and "]" in first, f"Missing severity badge for alias {alias}: {first}"
