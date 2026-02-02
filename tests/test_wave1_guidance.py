from __future__ import annotations

from daily_transit import interpretations
from astrological_dictionaries import astrological_aspects


WAVE1_ASPECTS = ["Quincunx", "Semisextile", "Semisquare"]
MODES = ["standard", "business", "space_force", "raves"]


def _assert_non_empty(result):
    assert result.summary.strip(), "Summary should not be empty"
    joined = " ".join(result.detail_lines)
    assert joined.strip(), "Detail lines should not be empty"


def test_wave1_guidance_non_empty_across_modes():
    for mode in MODES:
        for aspect in WAVE1_ASPECTS:
            res = interpretations.get_interpretation(
                mode=mode,
                aspect_name=aspect,
                planet1="Sun",
                planet2="Mars",
                aspect_meanings=astrological_aspects.get("aspect_meanings", {}),
            )
            _assert_non_empty(res)
            # Ensure severity badge appears for structured modes
            if mode in {"standard", "business", "space_force", "raves"}:
                first = res.detail_lines[0]
                assert first.startswith("[") and "]" in first, f"Missing severity badge for {mode} {aspect}: {first}"


def test_wave1_aliases_resolve_to_guidance():
    alias_samples = ["Semi-Sextile", "SemiSquare"]
    for alias in alias_samples:
        res = interpretations.get_interpretation(
            mode="standard",
            aspect_name=alias,
            planet1="Sun",
            planet2="Venus",
            aspect_meanings=astrological_aspects.get("aspect_meanings", {}),
        )
        _assert_non_empty(res)
        assert "Watch" in res.detail_lines[0], f"Expected Watch severity for alias {alias}"
