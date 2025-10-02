#!/usr/bin/env python3
"""Validate business interpretation dictionaries for coverage and placeholders."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from astrological_business_dictionaries import (
    business_aspect_action,
    business_aspect_behavior,
    business_aspect_context,
    business_planet_action,
    business_planet_behavior,
    business_planet_context,
    business_planet_interactions,
)
from astrological_dictionaries import astrological_aspects
from daily_transit.constants import DEFAULT_PLANETS


_MAJOR_ASPECTS = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

_EXTRA_ENTITIES = ["North Node", "South Node", "Chiron"]


def _is_missing(value: str) -> bool:
    if value is None:
        return True
    stripped = value.strip()
    if not stripped:
        return True
    return stripped.upper().startswith("TODO")


def _all_aspects() -> Iterable[str]:
    return astrological_aspects.get("aspect_degrees", {}).keys()


def _aspect_bucket(aspect: str) -> str:
    return "major_aspects" if aspect in _MAJOR_ASPECTS else "minor_aspects"


def _collect_planets() -> List[str]:
    names = {name for name, _glyph in DEFAULT_PLANETS}
    names.update(_EXTRA_ENTITIES)
    return sorted(names)


def _check_aspect_dict(
    label: str,
    dictionary: Dict[str, Dict[str, str]],
) -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    for aspect in _all_aspects():
        bucket = _aspect_bucket(aspect)
        entry = dictionary.get(bucket, {}).get(aspect)
        if _is_missing(entry):
            missing.append((label, aspect))
    return missing


def _check_planet_dict(label: str, dictionary: Dict[str, str]) -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    for planet in _collect_planets():
        entry = dictionary.get(planet)
        if _is_missing(entry):
            missing.append((label, planet))
    return missing


def _check_pairs(dictionary: Dict[str, Dict[str, str]]) -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    planets = _collect_planets()
    for i, primary in enumerate(planets):
        for secondary in planets[i + 1 :]:
            entry = dictionary.get(primary, {}).get(secondary)
            if _is_missing(entry):
                missing.append((primary, secondary))
    return missing


def _print_section(title: str, items: List[str]) -> None:
    print(f"\n{title} ({len(items)}):")
    for item in items:
        print(f"  - {item}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate business interpretation dictionaries.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 when missing entries are detected.",
    )
    args = parser.parse_args()

    issues: List[str] = []

    aspect_context_missing = _check_aspect_dict("Context", business_aspect_context)
    aspect_behavior_missing = _check_aspect_dict("Behavior", business_aspect_behavior)
    aspect_action_missing = _check_aspect_dict("Action", business_aspect_action)

    planet_context_missing = _check_planet_dict("Planetary Context", business_planet_context)
    planet_behavior_missing = _check_planet_dict("Planetary Behavior", business_planet_behavior)
    planet_action_missing = _check_planet_dict("Planetary Action", business_planet_action)

    pair_missing = _check_pairs(business_planet_interactions)

    if aspect_context_missing:
        issues.extend([f"Aspect Context :: {aspect}" for _, aspect in aspect_context_missing])
    if aspect_behavior_missing:
        issues.extend([f"Aspect Behavior :: {aspect}" for _, aspect in aspect_behavior_missing])
    if aspect_action_missing:
        issues.extend([f"Aspect Action :: {aspect}" for _, aspect in aspect_action_missing])

    if planet_context_missing:
        issues.extend([f"Planet Context :: {planet}" for _, planet in planet_context_missing])
    if planet_behavior_missing:
        issues.extend([f"Planet Behavior :: {planet}" for _, planet in planet_behavior_missing])
    if planet_action_missing:
        issues.extend([f"Planet Action :: {planet}" for _, planet in planet_action_missing])

    if pair_missing:
        issues.extend([f"Planet Pair :: {pair[0]} - {pair[1]}" for pair in pair_missing])

    print("Business Interpretation Dictionary Audit")
    print("=========================================")
    print(f"Aspect Context missing: {len(aspect_context_missing)}")
    print(f"Aspect Behavior missing: {len(aspect_behavior_missing)}")
    print(f"Aspect Action missing: {len(aspect_action_missing)}")
    print(f"Planet Context missing: {len(planet_context_missing)}")
    print(f"Planet Behavior missing: {len(planet_behavior_missing)}")
    print(f"Planet Action missing: {len(planet_action_missing)}")
    print(f"Planet Pair interactions missing: {len(pair_missing)}")

    if issues:
        _print_section("Detailed Missing Entries", issues)

    if args.strict and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
