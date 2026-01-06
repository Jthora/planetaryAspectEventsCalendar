from __future__ import annotations

"""Aspect catalog presets for detection scopes."""

# Major set remains minimal; values are exact angles.
MAJOR_ASPECTS = {
    "Conjunction": 0.0,
    "Opposition": 180.0,
    "Trine": 120.0,
    "Square": 90.0,
    "Sextile": 60.0,
}


# Values match docs/galacticCore/aspect-catalog.md with sufficient precision; septile family keeps repeating decimals to avoid orb-edge misses.
COMPLETE_ASPECTS = {
    "Conjunction": 0.0,
    "Semi-Septile": 25.714285714285715,  # 180/7
    "Semi-Sextile": 30.0,
    "Semiquintile": 36.0,
    "Novile": 40.0,  # 360/9
    "SemiSquare": 45.0,
    "Septile": 51.42857142857143,  # 360/7 (keep extended precision)
    "Sextile": 60.0,
    "Quintile": 72.0,  # 360/5
    "Binovile": 80.0,  # 2/9
    "Square": 90.0,
    "Biseptile": 102.85714285714286,  # 2/7 (keep extended precision)
    "Trebiquintile": 108.0,  # 3/10
    "Trine": 120.0,
    "Biquintile": 144.0,  # 2/5
    "Quincunx": 150.0,
    "Triseptile": 154.28571428571428,  # 3/7 (keep extended precision)
    "Opposition": 180.0,
}


def select_scope(scope: str):
    key = (scope or "major").lower()
    if key == "major":
        return MAJOR_ASPECTS
    if key == "complete":
        return COMPLETE_ASPECTS
    return None
