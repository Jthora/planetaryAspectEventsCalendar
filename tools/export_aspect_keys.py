#!/usr/bin/env python3
"""Utility script to list aspect and planet keys required for interpretation content."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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

def _collect_aspects() -> Dict[str, List[str]]:
    all_aspects = sorted(astrological_aspects.get("aspect_degrees", {}).keys())
    majors = sorted([aspect for aspect in all_aspects if aspect in _MAJOR_ASPECTS])
    minors = sorted([aspect for aspect in all_aspects if aspect not in _MAJOR_ASPECTS])
    return {"major": majors, "minor": minors}


def _collect_planets() -> List[str]:
    names = {name for name, _glyph in DEFAULT_PLANETS}
    names.update(_EXTRA_ENTITIES)
    return sorted(names)


def _collect_pairs(planets: List[str]) -> List[str]:
    return [f"{p1} - {p2}" for p1, p2 in combinations(planets, 2)]


def _build_payload() -> Dict[str, List[str]]:
    planets = _collect_planets()
    aspects = _collect_aspects()
    return {
        "major_aspects": aspects["major"],
        "minor_aspects": aspects["minor"],
        "planets": planets,
        "planet_pairs": _collect_pairs(planets),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Export aspect and planet keys for interpretation authoring.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    payload = _build_payload()

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    print("Major Aspects ({}):".format(len(payload["major_aspects"])))
    for aspect in payload["major_aspects"]:
        print(f"  - {aspect}")

    print("\nMinor Aspects ({}):".format(len(payload["minor_aspects"])))
    for aspect in payload["minor_aspects"]:
        print(f"  - {aspect}")

    print("\nPlanets / Entities ({}):".format(len(payload["planets"])))
    for planet in payload["planets"]:
        print(f"  - {planet}")

    print("\nPlanet Pairs ({} combinations):".format(len(payload["planet_pairs"])))
    for pair in payload["planet_pairs"]:
        print(f"  - {pair}")


if __name__ == "__main__":
    main()
