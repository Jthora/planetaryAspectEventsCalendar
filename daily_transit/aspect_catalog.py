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
    # Major
    "Conjunction": 0.0,
    "Opposition": 180.0,
    "Trine": 120.0,
    "Square": 90.0,
    "Sextile": 60.0,
    # Minor / tertiary (aligned to astrological_dictionaries names/angles)
    "Semisextile": 30.0,  # alias Semi-Sextile
    "Quincunx": 150.0,
    "Semisquare": 45.0,  # alias SemiSquare
    "Sesquiquadrate": 135.0,
    "Quintile": 72.0,
    "Biquintile": 144.0,  # alias Sesquiquintile
    "Septile": 51.42857142857143,
    "Biseptile": 102.85714285714286,
    "Triseptile": 154.28571428571428,
    "Novile": 40.0,
    "Binovile": 80.0,
    "Quadranovile": 160.0,
    "Decile": 36.0,  # alias Semiquintile
    "Tredecile": 108.0,  # alias Trebiquintile
    "Undecile": 32.72727272727273,
    "Tridecile": 65.45454545454545,
    "Quadraundecile": 130.9090909090909,
    "Quattuordecile": 25.714285714285715,  # alias Semi-Septile / Septuagenary
    "Vigintile": 18.0,
    "Quinvigintile": 14.4,
    "Semi-Octile": 22.5,
    "Sesqui-Octile": 67.5,
    "Septdecile": 21.176470588235293,
    "Semiduodecile": 15.0,
    "Sesquiquintile": 144.0,  # synonym of Biquintile
}


def select_scope(scope: str):
    key = (scope or "major").lower()
    if key == "major":
        return MAJOR_ASPECTS
    if key == "complete":
        return COMPLETE_ASPECTS
    return None
