# Aspect Catalog (Complete Preset)

## Table
Name | Degrees | Notes
---- | ------- | -----
Conjunct | 0.0 | Standard conjunction
Semi-Septile | 25.714285714285715 | 1/14 of 360; prime aspect family
Semi-Sextile | 30.0 | Also semisextile
Semiquintile | 36.0 | 1/10 of 360
Novile | 40.0 | 1/9 of 360
SemiSquare | 45.0 | Also semisquare
Septile | 51.42857142857143 | 1/7 of 360; keep extra digits for orb edges
Sextile | 60.0 | Standard
Quintile | 72.0 | 1/5 of 360
Binovile | 80.0 | 2/9 of 360
Square | 90.0 | Standard
Biseptile | 102.85714285714286 | 2/7 of 360
Trebiquintile | 108.0 | Using 3/10 of 360; add 216 variant later under unique label
Trine | 120.0 | Standard
Biquintile | 144.0 | 2/5 of 360
Quincunx/Inconjunct | 150.0 | Also quincunx
Triseptile | 154.28571428571428 | 3/7 of 360
Opposition | 180.0 | Standard

## Scope presets
- major: Conjunction, Opposition, Trine, Square, Sextile
- complete: all rows above (becomes the compact-mode default when selected)

### Future preset ideas
- minor: semisextile, semisquare, quincunx, quintile, biquintile
- prime: septile, biseptile, triseptile

## Validation
- Use explicit float literals with enough precision to avoid orb-boundary misses; septile family keeps repeating decimals.
- Maintain merge-window rules consistent with existing detection (pair-based windows already tuned for Moon/inner planets).
- Add unit coverage: each aspect should appear in the degree map; scopes must map to the correct subsets.

## Angle reference notes
- Septile family values use extended decimals (360/7 ≈ 51.42857142857143; 3/7 ≈ 154.28571428571428) to stay stable near orb edges.[1]
- Semi-septile uses 180/7 ≈ 25.714285714285715 for consistency.
- Trebiquintile set to 108 (3/10 of 360); if a 216 variant is desired, add a distinct label to avoid collisions.

---
[1] Using more precise floats reduces missed detections near orb edges.
