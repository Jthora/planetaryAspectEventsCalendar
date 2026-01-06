# Houses Specification (Placidus)

## House system
- Placidus only for this phase; no fallback unless explicitly decided.[1]
- Cusp computation should be time-aware and location-aware; reuse astropy where possible.

## Required inputs
- Latitude (decimal degrees), Longitude (decimal degrees), optional Elevation (meters, defaults to 0 if omitted).
- Event timestamp in UTC (convert to local sidereal as needed by the library).
- Timezone not required for houses if UTC is used end-to-end.

### Validation rules
- Reject lat outside [-90, 90] or lon outside [-180, 180].
- Reject missing lat/lon in compact mode with a clear error.

## Computation flow
1) Convert event UTC to observer local sidereal time (library-assisted if available).
2) Compute Placidus cusps (C1..C12) using astropy (preferred) or equivalent formulas.
3) Apply ayanamsa-adjusted ecliptic longitudes to the planet positions.
4) Assign house number via cusp spans; ensure wrap-around logic (C12→C1) is correct.
5) Cache cusps per day/hour if performance is an issue; validate cache invalidation when day/hour changes.

## Edge cases
- High latitudes where Placidus may fail; fallback to Whole Sign with clear logging.[2]
- Near poles, some libraries return NaN/None; surface as explicit error (before fallback if Whole Sign cannot compute either).
- Leap seconds/timezone shifts irrelevant when operating in UTC, but note if future local-time mode appears.

## Outputs
- House numbers 1-12 per planet, included in compact event payloads.
- Keep cusp values internal (optionally expose for debugging only when a debug flag is set).
- Consider adding an optional debug line with cusp degrees in logs (not in ICS).

---
[1] If a fallback system is chosen later, document the trigger conditions.
[2] Whole Sign fallback is chosen; log when activated and note reduced resolution compared to Placidus.
