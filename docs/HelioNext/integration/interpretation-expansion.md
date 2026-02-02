# Interpretation Expansion for Minor/Tertiary Aspects

## Goals
- Ensure HelioNext-emitted minor/tertiary aspects have meaningful interpretations across modes (standard, business, space_force, raves).
- Provide safe fallbacks so ICS output never goes blank when a new aspect is present.

## Aspect coverage to support
- Minor/tertiary angles (union of legacy dictionary and HelioNext catalog): Semi-Sextile/Semisextile, SemiSquare/Semisquare, Semiquintile/Decile, Quintile, Biquintile, Trebiquintile/Tredecile, Quincunx, Septile family (Septile, Biseptile, Triseptile, Semi-Septile/Quattuordecile/Septuagenary), Novile/Binovile/Quadranovile, Semi-Octile/Sesqui-Octile, Undecile/Tridecile/Quadraundecile, Vigintile/Quinvigintile, Sesquiquadrate, Semiduodecile, Sesquiquintile.

## Work items
- Add a tertiary bucket (or expanded minor bucket) to structured interpretation routing so non-major aspects are looked up instead of dropped.
- Add fallback text for unmapped aspects using `astrological_aspects['aspect_meanings']` when structured guidance is missing.
- Populate guidance entries per mode for the minor/tertiary set (can iterate: start with standard, then business/space_force/raves).
- Add alias mapping so synonymous names resolve to the same guidance (e.g., Semi-Sextile ↔ Semisextile, SemiSquare ↔ Semisquare, Semiquintile ↔ Decile, Trebiquintile ↔ Tredecile, Semi-Septile ↔ Quattuordecile/Septuagenary).
- Update tests to cover a sample of minor/tertiary aspects through the interpretation pipeline (headline/impact/action non-empty, fallback present).

## Acceptance
- Any aspect emitted by HelioNext or legacy (major/minor/tertiary) yields a non-empty summary in ICS outputs across modes.
- Alias names resolve consistently; no blank descriptions for recognized angles.
- Tests cover at least one minor, one septile-family angle, and one quincunx/quintile path per mode.
