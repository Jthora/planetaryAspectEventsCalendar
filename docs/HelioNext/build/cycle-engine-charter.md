# Cycle Engine Charter (HelioNext Extension)

## Purpose and Scope
- Deliver a cycle-focused pipeline (extension or sibling engine) that emits cycle-aware events/intervals alongside HelioNext aspect events without breaking existing ICS/CLI defaults.
- Cycles covered: planetary ingresses (sign changes with ayanamsa applied), synodic phases per planet pair (0/90/180/270/360 and configurable phase lists), retrograde/station intervals per body, orbital perihelion/aphelion markers where ephemeris supports, lunation-adjacent points (Nodes, Apogee/Lilith, Perigee/Priapus), and Sun/Moon.
- Time horizons: days → centuries. Must remain stable across long spans; clamp to ephemeris validity with clear errors.

## Goals
- Accurate start/end timestamps (UTC) for intervals (retrogrades) and instants (ingress, synodic exact, station peaks), with deterministic ordering.
- Ayanamsa-aware outputs (e.g., galactic_core) applied before sign determination; tropical remains default.
- Compatibility with existing builders: ICS export, compact formatter, guidance/title layers. If new fields are needed, add them in a backward-compatible schema.
- Performance: acceptable runtime on year and decade spans; reuse HelioNext caching patterns to keep ephemeris calls bounded.

## Non-goals (initial phase)
- Changing existing aspect DTOs or ICS formatting for non-cycle events.
- Full-house calculations for non-Earth bodies if not already supported (documented if needed later).
- New ephemeris sources; reuse current kernels and fail clearly if coverage is insufficient.

## Event/DTO Shape (proposed)
- Shared fields: `start_time_utc`, `end_time_utc` (optional for instant events), `event_type` (ingress|synodic_phase|retro_interval|station|perihelion|aphelion), `body` (or `body1/body2` for synodic), `ayanamsa_mode`, `sign` (for ingress), `phase_angle` (for synodic), `retrograde` flag, `station_strength` (optional), `uncertainty_s`.
- Instant events: set `start_time_utc` = `end_time_utc`; intervals: distinct start/end.
- Display helpers: `label`, `summary`, `glyphs` if needed for ICS summary; keep optional to avoid breaking existing consumers.

## ICS Encoding Guidance
- Ingress and synodic instants: timed VEVENT with summary `Body → Sign` or `Body1 Phase Body2` and optional ayanamsa note.
- Retrograde intervals: VEVENT with start/end; include `STATUS` and retro marker in summary; consider all-day when duration > 2 days, else timed.
- Stations: single instant events tagged as station (forward/retro) with tolerance note if needed.
- Perihelion/aphelion: point events; include distance if available (optional field later).
- Folding remains 75 bytes; ASCII-safe option preserved.

## Edge Cases and Policies
- Sign crossings near 0/360 with ayanamsa applied; must unwrap angles per body to avoid false multiple ingress in one step.
- Multiple crossings between samples (fast Moon, high ayanamsa offsets): adaptive stepping and post-step sign check to detect missed crossings.
- Retrograde overlapping ingress: ingress derived from ayanamsa-adjusted longitude regardless of motion direction; retro interval boundaries computed separately.
- Station at boundary: emit station instant even if equal to ingress; de-dupe by merge window if desired.
- Synodic wrap: handle 0/360 crossings; ensure phase list sorted and wrap-safe.
- Ephemeris bounds: error early if requested range exceeds kernel coverage; no projected events beyond window.
- ΔT/time-scale: keep UTC + ts.utc consistent; document that long-range accuracy is limited by kernels/ΔT model.
- Leap seconds: rely on Skyfield/time scale; avoid naive datetime arithmetic for exact crossings.

## Performance and Caching
- Reuse HelioNext caches for positions/separations keyed by body+time and pair+time.
- Allow coarser base steps for outer pairs and long spans; tighten dynamically near sign/phase changes (adaptive on angle delta per step).
- For interval detection (retro), reuse velocities from sampled points; avoid repeated ephemeris calls inside refine.
- Measure ephemeris_calls, cache hits, refine iterations per event type; add scenario budgets for year/decade spans.

## Validation Matrix (initial)
- Synthetic ephemeris: craft ingress and retro intervals with known times; synodic phase crossings at predictable times; include ayanamsa offsets.
- Real ephemeris short: 7-day Moon-heavy window with multiple ingresses and one retro onset.
- Medium: 1-month Mercury/Venus retro window including stations and ingresses.
- Long: 1-year outer planets for ingresses + retro intervals; 1 synodic outer pair (Jupiter-Saturn) phase sample.
- Century sanity: sample endpoints for ephemeris coverage and ensure graceful failure outside bounds.
- Tolerances: time ≤ 2s for instants (short/medium); looser (e.g., 30s) allowed for long-span outers if justified; document per test.

## Integration and Toggle
- Engine selection: either extend engine_factory with `cycles`/`helionext-cycles` or add a mode flag to HelioNext; keep legacy default unaffected.
- Config: new options for `cycle_types`, `phase_angles`, `ingress_signs` (default all 12), `ayanamsa`, `retro_probe_hours`, `merge_window_hours` for cycle events, and output mode (timed vs all-day intervals).
- Downstream: ICS builder may need cycle-aware branch; compact formatter optional; avoid breaking aspect paths.

## Risks
- Kernel coverage gaps for Chiron, Nodes, Apogee/Perigee; must detect and fail clearly or provide fallbacks.
- Performance on century ranges if caches unbounded; may need chunked processing.
- Schema creep: keep DTO minimal and versioned if fields expand.

## Next Steps
- Decide engine name and toggle shape; draft CLI/config proposal.
- Design cycle detection algorithms: ingress scanner, retro interval finder, synodic phase finder, station detector, perihelion/aphelion marker.
- Define exact DTO and ICS field list and wire a minimal builder path.
- Author validation plan with fixtures (synthetic + real) and add to CI matrix.
