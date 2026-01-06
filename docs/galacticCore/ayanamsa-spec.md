# Ayanamsa Specification

## Supported options
- tropical: 0 offset (baseline ecliptic longitudes).
- lahiri: sidereal offset per Lahiri ayanamsa (epoch/constant to be sourced from authoritative reference).
- galactic_core: offset using Galactic Core reference (constants pending from user-provided file or values); consider precession of the equinox and Sgr A* longitude as reference.

### Additional notes
- Offsets are applied uniformly to all bodies before sign and house determination.
- Keep naming stable for CLI and internal enums to avoid downstream breakage.

## Application
- For each planet longitude L_trop: L_adj = wrap360(L_trop - ayanamsa_offset_deg).
- Apply before sign determination and house assignment; store both raw and adjusted if needed for debugging.
- Ensure wrap360 is applied after subtraction to keep values in [0, 360).

## Computation notes
- Tropical: offset = 0; serves as control case in tests.
- Lahiri: derive offset for a given datetime; prefer astropy sidereal transformations if available, else use stored constant + precession rate (document source and epoch).[1]
- Galactic Core: define reference longitude, epoch, and any drift; compute offset at datetime. If no drift, treat as constant; otherwise model precession rate explicitly. Consider precession of the equinox and actual Galactic Core longitude in sidereal frame.[2]

## CLI mapping
- Flag: --ayanamsa {tropical,lahiri,galactic_core}
- Default: tropical when omitted (explicit decision).
- Validation: reject unknown strings; provide help text with examples.

## Validation
- Unit tests with fixed datetimes and known offsets (golden values from external calculators).
- Cross-check against external calculator for Lahiri and Galactic Core once constants are finalized.
- Include regression test ensuring wrap360 correctness near 0/360 boundaries.

## Pending inputs
- Galactic Core constants/file; Lahiri reference details.
- Whether to expose custom ayanamsa via CLI (not in scope now, but note as future expansion).

## Notes on galactic_core
- Consider the longitude of Sgr A* as reference; apply precession similarly to Lahiri’s handling but anchored to the Galactic Core instead of a fixed star.
- Document chosen epoch and any drift so results are reproducible.

---
[1] Lahiri commonly referenced to 285d 0m 0s at 1 Jan 1900; verify exact definition before coding.
[2] If using the physical Galactic Core, document source (e.g., Sagittarius A*) longitude and epoch; confirm drift handling.
