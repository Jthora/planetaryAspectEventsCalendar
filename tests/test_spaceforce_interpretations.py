from daily_transit import interpretations


def test_spaceforce_interpretation_uses_structured_copy():
    result = interpretations.get_interpretation(
        mode="space_force",
        aspect_name="Conjunction",
        planet1="Sun",
        planet2="Moon",
        aspect_meanings={"Conjunction": "Fusion"},
    )

    assert result.summary.startswith("Opportunity")
    assert any("Why it matters" in line for line in result.detail_lines)
    assert any("Interaction Insight" in line for line in result.detail_lines)


def test_spaceforce_interpretation_handles_missing_aspect():
    result = interpretations.get_interpretation(
        mode="space_force",
        aspect_name="NonexistentAspect",
        planet1="Sun",
        planet2="Mars",
        aspect_meanings={},
    )

    assert "[Info]" in result.detail_lines[0]
    assert "Monitor this transit" in " ".join(result.detail_lines)


def test_planet_themes_switch_based_on_mode():
    themes = interpretations.planet_themes_for_mode("space_force")
    assert themes.get("Mars") == "tactical thrust"

    fallback = interpretations.planet_themes_for_mode("unknown_mode")
    assert fallback is interpretations.PLANET_THEMES
