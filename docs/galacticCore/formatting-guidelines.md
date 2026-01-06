# Formatting Guidelines (Compact Mode)

## Summary line
- Abbreviated, no prose. Example pattern:
  - P1 Z:<Sign> <deg> H:<n> Δ<deg> <Aspect> P2 Z:<Sign> <deg> H:<n>
- Use planet glyphs unless ascii-only requested (then short labels).
- Keep spacing consistent; avoid trailing whitespace to reduce ICS diff noise.

### Variants
- If space is tight, drop Raw separation from summary and keep it in description only.
- For ascii-only, wrap aspect symbol in brackets if desired: [TRI], [OPP], etc.

## Description body
- Minimal fields only; no interpretations or profiles.
- Recommended field order:
  - UTC: YYYY-MM-DD HH:MM:SS
  - Δ: separation degrees (full precision per config)
  - P1: Z:<Sign> <deg_precise> H:<n>
  - P2: Z:<Sign> <deg_precise> H:<n>
  - Raw: raw separation (optional)
- Blank lines discouraged; keep concise.

### Optional fields
- Retrograde markers: include (short form: R) because they are important; ensure consistent placement.
- Orb distance could be added if requested (Δ vs target).

## Precision
- Time: include seconds (HH:MM:SS); milliseconds out of scope.
- Angles: support both, default to decimal; stay consistent across the file:
  - DMS: 00°00'00"
  - Decimal: 000.0000° (four decimals recommended for sub-arcminute clarity)
- Separation Δ: match angle precision to main angle scheme.

## Labels
- Use short labels: Z (zodiac), H (house), Δ (separation), UTC (time).
- No emojis in ascii-only mode; glyph mode allowed when not ASCII.
- Planet labels: glyphs or short ASCII from existing maps.

## Prohibited
- Interpretations, raves/business tone, planet profiles, daily summaries (unless explicitly enabled outside compact mode).
- Long prose; keep to one line per field.

## Folding and length
- ICS folding limit is 75 bytes per line; enforce folding and design lines to fit naturally to minimize wraps.
