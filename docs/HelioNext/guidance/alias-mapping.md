# Aspect Alias Mapping

Purpose: ensure catalogs and guidance resolve to a single canonical key per aspect.

Canonical → Aliases (keep canonical names aligned to daily_transit.aspect_catalog COMPLETE_ASPECTS):
- Semisextile → Semi-Sextile, Duodecile
- Semisquare → SemiSquare
- Sesquiquadrate → (none; keep as-is)
- Decile → Semiquintile
- Tredecile → Trebiquintile
- Quattuordecile → Semi-Septile, Septuagenary
- Biquintile → Sesquiquintile
- Quadranovile → (none; keep as-is)
- Semi-Octile → (none; keep as-is)
- Sesqui-Octile → (none; keep as-is)
- Undecile → (none; keep as-is)
- Tridecile → (none; keep as-is)
- Quadraundecile → (none; keep as-is)
- Vigintile → (none; keep as-is)
- Quinvigintile → (none; keep as-is)
- Septdecile → (none; keep as-is)
- Semiduodecile → (none; keep as-is)
- Septile family → keep numeric qualifiers (Septile, Biseptile, Triseptile)

Usage:
- Detection/catalogs should emit canonical names.
- Interpretations should normalize incoming names to canonical before lookup.
- Keep this list in sync with aspect_catalog COMPLETE_ASPECTS and astrological_dictionaries angles.
