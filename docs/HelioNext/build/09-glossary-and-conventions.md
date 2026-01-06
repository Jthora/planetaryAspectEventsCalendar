# HelioNext Glossary and Conventions

## Terms
- Aspect: angular relationship between two bodies/points per catalog (major/minor/tertiary angles defined in dictionaries).
- Orb: allowable deviation from exact aspect angle (Δ reported as distance from exactness).
- Retrograde/Station: motion states per legacy criteria (retrograde = negative longitude rate; station = near-zero rate with sign change).
- Houses: positions relative to house system used in legacy (same house calculation method).

## Angle Conventions
- Normalize to 0–360 degrees; handle wrap at 0/360 explicitly to avoid jumps.
- Apply ayanamsa adjustments consistently before comparisons (ayanamsa = zodiac offset such as galactic center).

## Time Conventions
- Use UTC internally; respect configured timezone where displayed downstream.
- Consistent conversion utilities shared with legacy to avoid drift between engines.

## Modes
- Tropical and galactic/ayanamsa variants using shared transforms; names/ids match legacy.

## Naming
- Event fields and labels follow legacy names to keep formatter compatibility (titles, glyphs, Δ field names).
