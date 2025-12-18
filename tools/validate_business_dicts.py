#!/usr/bin/env python3
"""Validate executive-focused business interpretation dictionaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from astrological_business_dictionaries import (  # type: ignore import-not-found
    all_business_planets,
    business_aspect_guidance,
    business_pair_overrides,
)
from astrological_dictionaries import astrological_aspects

_REQUIRED_KEYS = ("severity", "headline", "impact", "action", "summary")
_ALLOWED_SEVERITIES = {"Opportunity", "Watch", "High Risk", "Info"}
_SUMMARY_MAX = 120


def _all_aspects() -> Iterable[str]:
    return sorted(astrological_aspects.get("aspect_degrees", {}).keys())


def _bucket(aspect: str) -> str:
    return "major_aspects" if aspect in business_aspect_guidance.get("major_aspects", {}) else "minor_aspects"


def _is_blank(value: str) -> bool:
    return not value or not value.strip()


def _validate_aspect_entries() -> List[str]:
    issues: List[str] = []
    guidance = business_aspect_guidance
    for aspect in _all_aspects():
        bucket = _bucket(aspect)
        entry: Dict[str, str] = guidance.get(bucket, {}).get(aspect, {})
        for key in _REQUIRED_KEYS:
            if _is_blank(entry.get(key, "")):
                issues.append(f"Aspect `{aspect}` missing `{key}`")
        severity = entry.get("severity", "").strip()
        if severity and severity not in _ALLOWED_SEVERITIES:
            issues.append(f"Aspect `{aspect}` has unknown severity `{severity}`")
        summary = entry.get("summary", "").strip()
        if summary and len(summary) > _SUMMARY_MAX:
            issues.append(f"Aspect `{aspect}` summary exceeds {_SUMMARY_MAX} characters")
    return issues


def _validate_pairs() -> Tuple[List[str], List[str]]:
    issues: List[str] = []
    notes: List[str] = []
    seen: set[Tuple[str, str]] = set()
    for pair_key, message in business_pair_overrides.items():
        if len(pair_key) != 2:
            issues.append(f"Pair key `{pair_key}` is malformed")
            continue
        normalised = tuple(sorted(pair_key))
        if normalised in seen:
            issues.append(f"Duplicate pair override `{pair_key}`")
        seen.add(normalised)
        if _is_blank(message):
            issues.append(f"Pair `{normalised[0]} - {normalised[1]}` has empty message")
    covered_planets = {planet for pair in seen for planet in pair}
    missing_planets = sorted(set(all_business_planets()) - covered_planets)
    if missing_planets:
        notes.append(
            "Pair coverage note: using default theme balance for "
            + ", ".join(missing_planets)
            + "."
        )
    return issues, notes


def _print_report(aspect_issues: List[str], pair_issues: List[str], pair_notes: List[str]) -> None:
    print("Business Interpretation Dictionary Audit")
    print("=========================================")
    print(f"Aspects checked: {len(list(_all_aspects()))}")
    print(f"Aspect issues: {len(aspect_issues)}")
    print(f"Pair overrides: {len(business_pair_overrides)} entries")
    print(f"Pair issues: {len(pair_issues)}")

    if aspect_issues:
        print("\nAspect Guidance Issues:")
        for issue in aspect_issues:
            print(f"  - {issue}")

    if pair_issues:
        print("\nPair Override Issues:")
        for issue in pair_issues:
            print(f"  - {issue}")

    if pair_notes:
        print("\nPair Override Notes:")
        for note in pair_notes:
            print(f"  - {note}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate business interpretation dictionaries.")
    parser.add_argument("--strict", action="store_true", help="Exit with status 1 when issues are detected.")
    args = parser.parse_args()

    aspect_issues = _validate_aspect_entries()
    pair_issues, pair_notes = _validate_pairs()

    _print_report(aspect_issues, pair_issues, pair_notes)

    if args.strict and (aspect_issues or pair_issues):
        sys.exit(1)


if __name__ == "__main__":
    main()
