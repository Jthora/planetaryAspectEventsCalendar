from __future__ import annotations

from daily_transit import interpretations
from astrological_dictionaries import astrological_aspects


WAVE4_ASPECTS = [
    "Undecile",
    "Tridecile",
    "Quadraundecile",
]
MODES = ["standard", "business", "space_force", "raves"]


def _assert_non_empty(result):
    assert result.summary.strip(), "Summary should not be empty"
    joined = " ".join(result.detail_lines)
    assert joined.strip(), "Detail lines should not be empty"


def test_wave4_guidance_non_empty_across_modes():
    for mode in MODES:
        for aspect in WAVE4_ASPECTS:
            res = interpretations.get_interpretation(
                mode=mode,
                aspect_name=aspect,
                planet1="Sun",
                planet2="Saturn",
                aspect_meanings=astrological_aspects.get("aspect_meanings", {}),
            )
            _assert_non_empty(res)
            first = res.detail_lines[0]
            assert first.startswith("[") and "]" in first, f"Missing severity badge for {mode} {aspect}: {first}"
