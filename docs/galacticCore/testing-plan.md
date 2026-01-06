# Testing Plan

- Ayanamsa offsets: tropical=0, Lahiri known date, Galactic Core reference date; include wrap360 edge near 0/360; confirm precession handling.
- House assignment: Placidus cusp computation and planet-to-house mapping for known coordinates/date; validate against reference outputs; verify Whole Sign fallback triggers correctly and logs.
- Aspect catalog: every listed aspect present with correct degrees; scope selection works; ensure Trebiquintile handled per final decision (108).
- Formatter: compact output includes Z/H/time/Δ with expected precision; ascii-only toggles labels and symbols; check folding; retrograde markers present and correctly placed.
- Precision config: degree/time precision switches respected; default decimal verified; DMS path covered.

- CLI runs (short ranges) for each ayanamsa option and compact mode with location; snapshot ICS checks (golden files).
- Error handling: missing lat/lon, invalid ayanamsa, unsupported scope -> fails with clear message and non-zero exit.
- Performance sanity: run a 7-day window with complete aspect scope to ensure runtime within expected bound; target second-level timing (no milliseconds needed).

## Regression
- Existing modes unaffected: standard/raves/business output unchanged when compact not used; run a known prior sample and diff.

## Tooling
- Prefer pytest snapshots/golden files for compact events; float comparisons with tolerances for Δ.
- Use property-based tests for wrap360 and house assignment boundaries if feasible.
