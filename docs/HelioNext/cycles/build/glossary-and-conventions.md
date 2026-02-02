# Glossary and Conventions

## Core Terms
- Ingress: sign change event after applying ayanamsa; timestamp is the exact boundary crossing.
- Synodic phase: event when separation(body1, body2) equals a configured phase angle (default 0/90/180/270/360), wrap-safe.
- Retro interval: duration where longitudinal rate < 0; start/end detected via rate sign flips.
- Station: instant where longitudinal rate crosses zero (forward→retro or retro→forward); may coincide with retro interval boundaries.
- Perihelion/Aphelion: events marking distance minima/maxima from the Sun (or central body); require distance data.
- Node: ascending/descending crossing of ecliptic latitude=0 for the Moon (if supported).
- Apogee/Perigee: distance extrema for Moon (Lilith/Apogee, Priapus/Perigee) if kernels available.

## Bodies and Points
- Major: Sun, Moon, Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto.
- Minor/points: Chiron, Lunar Nodes, Lilith (Apogee), Priapus (Perigee).
- When kernels are missing, bodies/points are marked unsupported; see ephemeris doc.

## Ayanamsa
- Supported names: tropical (0 offset), lahiri (drifted from reference epoch), galactic_core (placeholder constants until updated).
- Application: subtract ayanamsa from longitude, wrap to 0–360, then determine sign/phase.
- Drift model: degrees per Julian year from reference epoch; documented in ephemeris doc.

## Angle and Sign Conventions
- Wrap angles to [0,360); use signed_min_diff for differences in (-180,180].
- Sign order: Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces.
- Sign boundaries at multiples of 30 degrees; ingress occurs exactly at boundary crossing after ayanamsa adjustment.
- Unwrapping: when interpolating across 0/360, unwrap to maintain continuity and avoid artificial jumps.

## Phase Conventions
- Default phase list: 0, 90, 180, 270, 360 degrees; configurable via CLI/config.
- Phases must be unique and sorted; angles outside [0,360] are invalid.
- 0 and 360 are equivalent; implementation should treat them consistently to avoid double emission.

## Retro/Station Conventions
- Retrograde defined by negative longitudinal rate over probe window; probe hours adaptive by speed class.
- Station directions labeled: F→R (forward to retro) and R→F (retro to forward).
- Station strength/quality optional; when present, derived from rate magnitude before/after crossing.

## Event Ordering
- Sort key: (UTC time, event_type, body tuple). Determinism is required.
- Merge windows configured per event_type; dedupe policy prefers lowest uncertainty then earliest time.

## Abbreviations and Labels
- Sign abbreviations: Ar, Ta, Ge, Cn, Le, Vi, Li, Sc, Sg, Cp, Aq, Pi.
- Planet abbreviations (ASCII): Su, Mo, Me, Ve, Ma, Ju, Sa, Ur, Ne, Pl, Ch, No (Nodes), Li (Lilith), Pr (Priapus).
- Direction labels: F→R, R→F; Retro intervals labeled "Retrograde"; Stations labeled "Station".

## Formatting Notes
- Timestamps stored as UTC ISO; ICS uses folding at 75 bytes; ASCII mode replaces glyphs with labels.
- Uncertainty_seconds included only when non-zero; STATUS may be set to TENTATIVE when uncertainty exceeds threshold.

## Reference Docs
- See ephemeris-and-boundaries for kernels, coverage, and ayanamsa constants.
- See ICS schema for summary/description templates and UID strategy.
- See algorithm design for detection specifics and tolerances.
