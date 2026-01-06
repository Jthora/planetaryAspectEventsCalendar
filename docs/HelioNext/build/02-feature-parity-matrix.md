# HelioNext Feature Parity Matrix

## Summary
Legacy vs HelioNext coverage for all required features. HelioNext must meet or exceed legacy unless noted. Use this as the single source for parity definitions.

## Aspect Catalog
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| Major aspects | Yes | Yes | Same angles/orbs (e.g., 0, 60, 90, 120, 180 with legacy orbs).
| Minor aspects | Yes | Yes | Same angles/orbs (e.g., 30, 45, 72, 135 as defined in dictionaries).
| Tertiary/custom | Yes | Yes | Reuse dictionaries; allow config to enable/disable.
| Aspect scopes toggle | Yes | Yes | CLI/config parity.

## Bodies / Points
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| Core planets/lights | Yes | Yes | Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn (same identifiers as legacy).
| Outer planets | Yes | Yes | Uranus, Neptune, Pluto as in legacy.
| Additional points | Yes | Yes | Legacy points (e.g., nodes, galactic center) stay; names unchanged.
| Retrograde flags | Yes | Yes | Identical criteria and thresholds for retro/station labeling.

## Zodiac / Ayanamsa
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| Tropical | Yes | Yes | Default.
| Galactic/other ayanamsa | Yes | Yes | Reuse existing transforms.

## Houses
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| House computation | Yes | Yes | Same method and inputs (lat/lon/timezone as applicable).
| House labels in output | Yes | Yes | Preserve formatting.

## Output Payload / Formatting
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| Titles/labels/glyphs | Yes | Yes | Must match for ICS/title generator; glyph set unchanged.
| Δ (orb/delta) fields | Yes | Yes | Same semantics/units (distance from exact aspect angle).
| ICS folding | Yes | Yes | No change in formatter expectations.
| Timezones | Yes | Yes | Same handling.

## Config & Modes
| Item | Legacy | HelioNext Plan | Notes |
| --- | --- | --- | --- |
| Aspect scope flags | Yes | Yes | Map 1:1.
| Date range selection | Yes | Yes | Same inputs.
| Output modes (compact/full) | Yes | Yes | Keep downstream unchanged.

## Gaps / Decisions
- Track any deviations here; add rationale and mitigation (e.g., temporary mismatch, known limitation). Include expected resolution date/owner.

## Acceptance
- All rows marked "Yes" for HelioNext before rollout. Deviations require documented approval and test coverage in validation suite.
