# Galactic Core Compact Mode Requirements

## Goals
- Deliver a compact ICS mode with per-event planet tuples including zodiac (Z) and house (H) after ayanamsa adjustment, suitable for machine or human parsing without narrative text.
- Support ayanamsa selection: tropical (none), Lahiri, Galactic Core (default) with a clear CLI contract and deterministic math.
- Use Placidus houses (requires lat/lon, optional elevation) at event timestamps; fail fast when inputs are missing.
- Expose a complete aspect preset covering major, minor, and tertiary aspects per provided list; allow existing scopes to remain unchanged.
- Output high-precision time and angles; forbid interpretations or profiles in compact mode so payload stays lean.

### Notes
- Compact mode should remain orthogonal to interpretation modes; no accidental cross-talk with raves/business.
- Defaults must be explicit to avoid surprises when switching modes.

## Success Criteria
- CLI enforces required inputs for houses (lat/lon) and ayanamsa selection; missing data halts with actionable errors.
- Each aspect event carries Z/H for both planets with ayanamsa-adjusted longitudes and Placidus house numbers.
- Aspect scope “complete” matches the catalog; detection respects provided orb/steps and merge windows.
- Compact formatting uses abbreviated labels (Z/H/Δ/UTC) and full precision per guidelines; ascii-only obeyed.
- Existing modes remain intact; default behavior unchanged unless compact mode is requested.

### Metrics
- Zero regressions in legacy tests; new tests cover ayanamsa, houses, and compact formatting.
- Runtime remains within acceptable bounds for a one-year run using the complete aspect set (document baseline timing).

## Defaults
- Ayanamsa: tropical when flag omitted (explicit choice; keep galactic_core optional).
- House system: Placidus, with Whole Sign fallback at high latitudes (see houses-spec).
- Aspect scope: major unless user selects complete.
- Timezone: UTC unless user overrides.

### Configuration Footnotes
- Elevation optional; if absent, assume sea level.
- Product ID and status remain inherited from existing defaults.

## Non-Goals
- No interpretations, raves/business tone, or daily profiles in compact mode.
- No additional house systems beyond Placidus for this phase.
- No graphical output or retrograde markers beyond what is already available.

## Dependencies
- skyfield for ephemeris; astropy (or equivalent) for Placidus houses.
- Ephemeris kernel must include all requested bodies; warn if outer planets missing.
- Access to Galactic Core ayanamsa constants; Lahiri reference from a trusted source.[1]

## Risks / Edge Cases
- High-latitude Placidus stability; Whole Sign fallback enabled (log clearly).
- Ayanamsa constants/epoch accuracy (Galactic Core reference pending).[2]
- Performance impact from full aspect set; prefer fine timing (seconds) but avoid millisecond scope; adjust coarse/refine if needed and document baseline.
- Line folding for ICS: enforce 75-byte folding; design lines to fit naturally where possible.

## Scope Guardrails
- Compact mode must be opt-in; legacy CLI defaults unchanged.
- Daily summaries remain off in compact mode unless explicitly enabled.

---
[1] Lahiri constants typically derive from IAU definitions; confirm source and epoch.
[2] Galactic Core reference may require drift handling; document chosen approach.
