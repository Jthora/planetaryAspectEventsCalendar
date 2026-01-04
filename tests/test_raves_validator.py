import sys

import pytest

from tools import validate_raves_dicts as validator


def _configure_validator(monkeypatch, guidance, pairs, default_pair="Fallback pair."):
    monkeypatch.setattr(validator, "_all_aspects", lambda: ["Conjunction"])
    monkeypatch.setattr(validator, "raves_aspect_guidance", guidance)
    monkeypatch.setattr(validator, "raves_pair_overrides", pairs)
    monkeypatch.setattr(validator, "default_pair_message", lambda a, b: default_pair)
    monkeypatch.setattr(validator, "all_raves_planets", lambda: ["Sun", "Moon"])


def test_validator_strict_fails_on_missing_fields(monkeypatch):
    guidance = {"major_aspects": {"Conjunction": {}}, "minor_aspects": {}}
    pairs = {("Sun", "Moon"): ""}
    _configure_validator(monkeypatch, guidance, pairs)

    monkeypatch.setattr(sys, "argv", ["prog", "--strict"])
    with pytest.raises(SystemExit) as excinfo:
        validator.main()

    assert excinfo.value.code == 1


def test_validator_strict_passes_on_complete_fixture(monkeypatch, capsys):
    guidance = {
        "major_aspects": {
            "Conjunction": {
                "severity": "Opportunity",
                "headline": "Test headline",
                "impact": "Clear impact statement.",
                "action": "Take a balanced step tonight.",
                "watch": "Stay hydrated and grounded.",
                "summary": "Concise, under limit.",
                "music_genre": "House",
            }
        },
        "minor_aspects": {},
    }
    pairs = {("Sun", "Moon"): "Pair insight present."}
    _configure_validator(monkeypatch, guidance, pairs, default_pair="Fallback pair used.")

    monkeypatch.setattr(sys, "argv", ["prog", "--strict"])
    validator.main()

    out = capsys.readouterr().out
    assert "Aspect issues: 0" in out
    assert "Pair issues: 0" in out