# Open Questions

- Trebiquintile target degree: 108 confirmed for detection map; add 216 as a distinct label only if needed later.
- Galactic Core ayanamsa constants: reference longitude, epoch, drift; source file or values pending. Incorporate precession of the equinox and Sgr A* longitude; mirror Lahiri-style offset but anchored to Galactic Core.
- High-latitude Placidus fallback: switch to Whole Sign with clear logging.
- Precision scheme: support both DMS and decimal; default to decimal; keep consistent across summary/description.
- Default ayanamsa when flag omitted: tropical.
- Performance tuning: target second-level timing (milliseconds out of scope); adjust coarse/refine steps if runtime high and document baseline.
- Retrograde markers: include in compact mode (short form R); ensure consistent placement.
- Folding strategy: enforce 75-byte folding; design lines to avoid wrapping where possible.
