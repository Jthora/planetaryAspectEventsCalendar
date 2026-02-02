# Aspect Coverage Cross-Reference

This document catalogs the aspect sets used by the Astrological Event Calendar Generator (legacy) and the HelioNext engine so they can be cross-referenced when expanding interpretation modes.

## Legacy Generator (astrological_dictionaries.aspect_degrees)
Major and non-major entries currently defined:
- Conjunction (0)
- Opposition (180)
- Trine (120)
- Square (90)
- Sextile (60)
- Semisextile (30)
- Quincunx (150)
- Semisquare (45)
- Sesquiquadrate (135)
- Quintile (72)
- Biquintile (144)
- Septile (≈51.42857)
- Biseptile (≈102.85714)
- Triseptile (≈154.28571)
- Novile (40)
- Binovile (80)
- Quadranovile (160)
- Decile (36)
- Tredecile (108)
- Undecile (≈32.72727)
- Tridecile (≈65.45455)
- Quadraundecile (≈130.90909)
- Duodecile (30)
- Quattuordecile (≈25.71429)
- Vigintile (18)
- Quinvigintile (14.4)
- Sesquiquintile (144)
- Semi-Octile (22.5)
- Sesqui-Octile (67.5)
- Septdecile (≈21.17647)
- Semiduodecile (15)
- Septuagenary (≈25.71429)

## HelioNext Catalog (daily_transit/aspect_catalog.py)
- Major set: Conjunction, Opposition, Trine, Square, Sextile
- Complete set (major + minor/tertiary): Conjunction; Semi-Septile; Semi-Sextile; Semiquintile (Decile); Novile; SemiSquare; Septile; Sextile; Quintile; Binovile; Square; Biseptile; Trebiquintile; Trine; Biquintile; Quincunx; Triseptile; Opposition

## Naming and coverage differences to reconcile
- Legacy-only (not in HelioNext catalog): Sesquiquadrate (135), Quadranovile (160), Tredecile (108 named differently?), Undecile (≈32.727), Tridecile (≈65.454), Quadraundecile (≈130.909), Vigintile (18), Quinvigintile (14.4), Semi-Octile (22.5), Sesqui-Octile (67.5), Septdecile (≈21.176), Semiduodecile (15), Septuagenary (≈25.714, overlaps Quattuordecile), Sesquiquintile (144 alias of Biquintile), Duodecile (30 alias of Semisextile).
- HelioNext-only naming variants: Semi-Sextile (legacy Semisextile), SemiSquare (legacy Semisquare), Semiquintile (legacy Decile), Trebiquintile (legacy Tredecile?), Semi-Septile (legacy Quattuordecile/Septuagenary angle 25.714).
- Missing in HelioNext catalog: Sesquiquadrate (135) and other legacy minors/tertiaries listed above.

## Action items for interpretation expansion
- Decide canonical names and aliases across engines (e.g., map Semiquintile ↔ Decile; SemiSquare ↔ Semisquare; Semi-Sextile ↔ Semisextile; Trebiquintile ↔ Tredecile if intended).
- Expand the HelioNext aspect catalog or add an alias layer so legacy minor/tertiary aspects are emitted/recognized consistently.
- Update interpretation modes to include guidance buckets for all minor/tertiary aspects that will be emitted; add fallbacks for unmapped aspects.
- Align CLI aspect scope options (major vs complete) with the unified catalog and ensure the ICS generator uses the same mapping.
- Add schema reference: see [aspect-event-schema.md](aspect-event-schema.md) for downstream consumer field contract.
