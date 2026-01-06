# HelioNext Validation and Diffing

## Dual-Run Harness
- Run legacy and HelioNext over identical inputs; collect events; diff outputs (presence and timing).
- Report timing stats for both engines for side-by-side performance comparison.

### Harness essentials
- Input parity: same date range, aspect scope, ayanamsa, lat/lon/elev, and output mode (compact/full).
- Ordering: sort events by time then aspect/body pair to ensure deterministic comparison.
- Output formats: emit CSV/JSON with fields [time_utc, aspect_id, bodies, delta_deg, flags, houses, title].

### Suggested CLI shape
- `--engine legacy|helionext` (default legacy) used in dual-run invocations.
- Dual-run script produces `{engine}-events.json` and a diff report.

## Diff Rules
- Match by aspect + body pair + date window (date window = range covering expected time tolerance).
- Time tolerance: define allowed delta (e.g., seconds) for equality; specify units and default.
- Label/title/flags must match; Δ within small numeric tolerance; glyphs must align.

### Tolerances
- Time tolerance (default): 2 seconds absolute difference; strict mode: 1 second.
- Δ tolerance: 0.005 degrees (18 arcseconds); strict mode: 0.002 degrees.
- House/sign match: exact integer match after ayanamsa adjustment.
- Labels/glyphs: exact string match (respect ascii-only flag).

## Test Matrix
- Ranges: short (days), medium (weeks/month), long (year).
- Modes: tropical vs galactic/ayanamsa variants.
- Aspect scopes: major, minor, tertiary, combinations; include compact/full output modes where relevant.

### Concrete scenarios
- Short: 2025-01-01 to 2025-01-03, aspect scope complete, tropical and galactic_core, lat/lon set.
- Medium: 2025-01-01 to 2025-01-31, aspect scope major, tropical.
- Long: 2025-01-01 to 2025-12-31, aspect scope complete, tropical.
- Stress: 7-day window with dense Moon activity (include minor/tertiary), galactic_core mode.

## Edge Cases
- Retrogrades and stations near aspect times (test timing accuracy around velocity sign changes).
- Sign/house cusp crossings; angle wrap at 0/360.
- Tight orbs and dense Moon periods to stress solver and gating.

### Additional checks
- Ayanamsa transitions: verify adjusted longitudes wrap correctly near 0/360.
- Placidus fallback: high-latitude case triggers Whole Sign with log.

## ICS/Formatter Checks
- Folding constraints preserved (75-byte lines); houses and glyphs present; Δ rendered same as legacy; titles unchanged.

## Pass/Fail Criteria
- No missing/extra events; time deltas within tolerance; payload parity on labels/flags/Δ/houses.
- Log and track any approved deviations; include owner and expiry.

### Deviation handling
- Record mismatches in report with fields: aspect, bodies, time_delta, delta_deg_diff, flags_diff, houses_diff.
- Approved deviations require owner, reason, and expiry date; track in changelog.

## Tooling
- Script to produce side-by-side CSV/JSON and diff results; include timing metrics.
- Summary report with counts of matches/mismatches and max deltas; highlight worst offenders.

### Outputs
- `diff_report.json`: per-event comparisons and summary counts.
- `timing_report.json`: runtime per engine, counts of coarse/refine, cache hits if available.
