#!/usr/bin/env python3
"""Schema and completeness checks for the Space Force interpretation dictionaries.

Blueprint reference: docs/spaceforceupgrade/dictionary-blueprint.md.
QA reference: docs/spaceforceupgrade/qa-checklist.md.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ALLOWED_SEVERITIES = {"Opportunity", "Watch", "High Risk", "Info"}
REQUIRED_FIELDS = ("severity", "headline", "impact", "action", "summary")
OPTIONAL_FIELDS = ("watch",)


def _load_aspects() -> Sequence[str]:
    from astrological_dictionaries import astrological_aspects

    aspect_degrees = astrological_aspects.get("aspect_degrees", {})
    return sorted(aspect_degrees.keys())


def _load_spaceforce_module():
    from astrological_spaceforce_dictionaries import (
        SPACEFORCE_PLANET_THEMES,
        all_spaceforce_planets,
        spaceforce_aspect_guidance,
    )

    return SPACEFORCE_PLANET_THEMES, all_spaceforce_planets(), spaceforce_aspect_guidance


def _lookup_entry(mapping: Dict[str, Dict[str, Dict[str, str]]], aspect: str) -> Dict[str, str] | None:
    for bucket in ("major_aspects", "minor_aspects"):
        entry = mapping.get(bucket, {}).get(aspect)
        if entry is not None:
            return entry
    return None


def _validate_aspects(strict: bool) -> List[str]:
    errors: List[str] = []
    warnings: List[str] = []
    aspects = _load_aspects()
    planet_themes, expected_planets, guidance = _load_spaceforce_module()

    for aspect in aspects:
        entry = _lookup_entry(guidance, aspect)
        if entry is None:
            errors.append(f"[Aspect:{aspect}] Missing dictionary entry.")
            continue

        for field in REQUIRED_FIELDS:
            value = entry.get(field, "")
            if not isinstance(value, str):
                errors.append(f"[Aspect:{aspect}] Field '{field}' must be a string.")
                continue
            if not value.strip():
                message = f"[Aspect:{aspect}] Field '{field}' is blank."
                (errors if strict else warnings).append(message)
        for field in OPTIONAL_FIELDS:
            value = entry.get(field, "")
            if value is None:
                message = f"[Aspect:{aspect}] Optional field '{field}' missing."
                (errors if strict else warnings).append(message)

        severity = entry.get("severity", "").strip()
        if severity and severity not in ALLOWED_SEVERITIES:
            errors.append(f"[Aspect:{aspect}] Invalid severity '{severity}'.")

        summary = entry.get("summary", "").strip()
        if summary and len(summary) > 120:
            message = f"[Aspect:{aspect}] Summary exceeds 120 characters ({len(summary)})."
            (errors if strict else warnings).append(message)

    expected_planet_set = set(expected_planets)
    missing_planets = [p for p in expected_planet_set if not planet_themes.get(p, "").strip()]
    if missing_planets:
        errors.append(
            "[Planet Themes] Missing entries for: " + ", ".join(sorted(missing_planets))
        )

    extras = [p for p in planet_themes if p not in expected_planet_set]
    if extras:
        warnings.append("[Planet Themes] Extra entries detected: " + ", ".join(sorted(extras)))

    required_major = {"Conjunction", "Opposition", "Trine", "Square", "Sextile"}
    available_major = set(guidance.get("major_aspects", {}).keys())
    missing_major = sorted(required_major - available_major)
    if missing_major:
        message = "[Buckets] major_aspects missing required entries: " + ", ".join(missing_major)
        (errors if strict else warnings).append(message)

    for warning in warnings:
        print(f"WARNING: {warning}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Space Force interpretation data.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on blank fields and other warnings (default: warnings only).",
    )
    args = parser.parse_args()

    errors = _validate_aspects(args.strict)
    if errors:
        print("\nValidation failed:")
        for issue in errors:
            print(f" - {issue}")
        return 1

    mode = "STRICT" if args.strict else "LENIENT"
    print(f"Space Force dictionaries validated successfully ({mode} mode).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
