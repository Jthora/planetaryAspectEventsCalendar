# HelioNext Engine Interface

## Overview
Define the contract between HelioNext and the rest of the system, enabling a runtime switch between legacy and HelioNext without changing downstream formatters/builders. Clarify terms: "engine" is the detection pipeline; "DTO" is the event data object consumed by formatters.

## Engine Factory / Toggle
- Config entry (CLI flag/env/setting) selecting `legacy` or `helionext`.
- Factory produces an engine implementing the shared interface (see below).
- Default remains legacy until rollout criteria are met (see migration doc).

### CLI/Config shape
- CLI flag: `--engine {legacy,helionext}`; default `legacy`.
- Env override (optional): `ENGINE_MODE=helionext`.
- Config precedence: CLI > env > default.

## Core Interfaces
- Engine methods:
  - `generate_events(config) -> Iterable[Event]`: full pipeline for a date range.
  - Internal hooks: coarse scan, refine timing, retro/station check (exposed for testing where useful).
- Error contracts: well-defined exceptions for config/time errors; recoverable fallbacks where possible.
- "Coarse scan" = initial stepping to find candidate aspect crossings; "refine" = exact timing solver; "retro/station" = motion state checks.

### Ordering and determinism
- Events sorted by `exact_time` then `(aspect_id, body_pair)` for stable outputs.
- Deterministic given same ephemeris and config; no randomness.

## Event DTO Schema (must satisfy existing formatters)
Fields should cover (names align to legacy):
- `start_time` / `exact_time` (UTC) and any local/tz representations expected downstream.
- `aspect` (name/id/angle), `orb/Δ` (difference from exact angle), `bodies` involved (names, positions/longitudes), ayanamsa mode.
- `houses` info as currently emitted (house numbers/labels).
- Flags: `retrograde`, `station`, any legacy flags.
- Display fields: titles/labels/glyphs if produced here, or keys for downstream to render identically to legacy.

### Suggested field names
- `exact_time_utc`, `local_time` (if needed), `aspect_id`, `aspect_deg`, `delta_deg`, `body1`, `body2`, `lon1_deg`, `lon2_deg`, `ayanamsa_mode`, `house1`, `house2`, `retro1`, `retro2`, `station1`, `station2`, `title`, `glyphs`.

## Inputs / Config
- Date range, aspect scope (major/minor/tertiary), orbs, ayanamsa mode, location info (lat/lon) for houses, output mode (compact/full) as needed by formatter.
- Performance knobs (step sizes, tolerances) should be internal defaults with optional config for testing. Document defaults and units.

### Defaults
- Ayanamsa default: tropical.
- Aspect scope default: major.
- Time precision default: seconds.
- Step sizes/tolerances: defined in algorithm design doc; expose for testing only.

## Integration Touchpoints
- Downstream consumers: ICS builder, title generator, any logs/metrics.
- Ensure payload compatibility so downstream code remains unchanged under engine swap.
- Clarify which fields are mandatory vs derived downstream.

### Mandatory vs derived
- Mandatory: times, aspect id/angle, delta_deg, bodies, houses, retro/station flags, ayanamsa mode.
- Derived downstream: titles/glyphs if not produced in engine; ICS formatting.

## Extensibility
- Allow plugging different solvers/step strategies behind the same interface (for experimentation) without breaking the DTO.
- Keep naming/versioning for engines (e.g., `legacy`, `helionext`, potential `helionext-batched`).

## Testing Hooks
- Ability to run coarse/refine in isolation for unit tests.
- Deterministic behavior given same inputs/ephemeris (no randomness, stable ordering).
