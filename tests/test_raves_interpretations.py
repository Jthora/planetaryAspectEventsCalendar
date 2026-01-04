import pytest

from daily_transit import interpretations


@pytest.fixture
def set_raves(monkeypatch):
    def _apply(guidance, themes=None, pair_overrides=None, default_pair=None):
        themes = themes or {}
        pair_overrides = pair_overrides or {}
        default_pair = default_pair or (lambda a, b: f"Balance {a} and {b} for the night.")
        resources = interpretations._build_structured_resources(  # type: ignore[attr-defined]
            "raves",
            guidance,
            themes,
            pair_overrides,
            default_pair,
        )
        monkeypatch.setitem(interpretations._STRUCTURED_MODE_RESOURCES, "raves", resources)
        monkeypatch.setitem(interpretations._PLANET_THEME_MAP, "raves", themes)
        return resources

    return _apply


def test_raves_interpretation_uses_structured_copy(set_raves):
    guidance = {
        "major_aspects": {
            "Conjunction": {
                "severity": "Opportunity",
                "headline": "Mainstage alignment",
                "impact": "Energy stacks with friends and shared vision.",
                "action": "Plan a peak set together; keep hydration handy.",
                "watch": "Balance group hype with pacing to avoid burnout.",
                "summary": "Optimistic, connected, ready to move together.",
                "music_genre": "House",
                "social_mode": "Pull your crew closer and welcome new faces.",
            }
        },
        "minor_aspects": {},
    }
    set_raves(
        guidance,
        themes={"Sun": "solar spotlight", "Moon": "mood tides"},
        pair_overrides={("Moon", "Sun"): "Blend spotlight warmth with emotional safety."},
    )

    result = interpretations.get_interpretation(
        mode="raves",
        aspect_name="Conjunction",
        planet1="Sun",
        planet2="Moon",
        aspect_meanings={},
    )

    joined = " ".join(result.detail_lines)
    assert result.summary == "Optimistic, connected, ready to move together."
    assert "[Opportunity] Mainstage alignment" in joined
    assert "Why it matters: Energy stacks" in joined
    assert "Action: Plan a peak set together" in joined
    assert "Watch: Balance group hype" in joined
    assert "Interaction Insight: Blend spotlight warmth with emotional safety." in joined
    assert result.extras["music_genre"] == "House"
    assert "social_mode" in result.extras


def test_raves_interpretation_falls_back_when_missing_guidance(set_raves):
    guidance = {"major_aspects": {}, "minor_aspects": {}}
    set_raves(
        guidance,
        themes={"Sun": "solar spotlight", "Mars": "engine"},
        pair_overrides={},
        default_pair=lambda a, b: f"Default: balance {a} with {b} for cohesion.",
    )

    result = interpretations.get_interpretation(
        mode="raves",
        aspect_name="UnknownAspect",
        planet1="Sun",
        planet2="Mars",
        aspect_meanings={},
    )

    joined = " ".join(result.detail_lines)
    assert result.summary.startswith("Info — UnknownAspect influence tracked")
    assert result.detail_lines[0].startswith("[Info] UnknownAspect aspect active")
    assert "Interaction Insight: Default: balance Sun with Mars for cohesion." in joined
    assert result.extras == {}


def test_planet_themes_switch_based_on_raves_mode(set_raves):
    guidance = {"major_aspects": {}, "minor_aspects": {}}
    themes = {"Mars": "afterburn"}
    set_raves(guidance, themes=themes)

    mapped = interpretations.planet_themes_for_mode("raves")
    assert mapped.get("Mars") == "afterburn"

    fallback = interpretations.planet_themes_for_mode("unknown_mode")
    assert fallback is interpretations.PLANET_THEMES
