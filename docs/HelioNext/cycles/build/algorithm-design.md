# Cycle Algorithm Design

## Shared Principles
- Reuse HelioNext coarse/refine structure, but adapt step sizing to cycles (ingress/retro/phase) rather than aspect orbs.
- Always apply ayanamsa before sign/phase evaluation; maintain wrap-safe operations (0–360) with unwrapping to detect crossings cleanly.
- Deterministic: fixed ordering of checks; no randomness; repeatable given same inputs.
- Safety: clamp to requested window and ephemeris coverage; no projections beyond range.

## Ingress Detection
- Input: body, ayanamsa offset, sign list (default all 12), date window.
- Sampling: adaptive step based on body speed class (fast Moon: ≤10–20 minutes; inner: 30–60 minutes; outers: hours) bounded by max angle delta (e.g., ≤1/3 of sign span per step).
- Crossing logic: track previous sign (after ayanamsa) and current sign; if different, bracket crossing between timestamps.
- Refinement: root-find longitude(t) - boundary_angle with wrap-safe unwrapping; use Brent/secant hybrid within bracket; tolerance target ≤2s (short/medium), relaxed if configured for long spans.
- Double-cross detection: after each step, verify no skipped intermediate sign by checking angle delta vs sign size; if suspicious, sub-step the interval.
- Station-at-boundary: if velocity magnitude near zero at crossing, tag ingress with station_adjacent note; keep station as separate event.
- Output: ingress instant with sign, uncertainty_seconds if solver fallback used; optional longitude_at_event.

## Synodic Phase Finder
- Input: body1/body2, phase list (sorted, unique), date window, ayanamsa offset (applied to both bodies before separation).
- Sampling: pair-based coarse step (fast body combos tighter); compute separation = wrap360(lon2 - lon1) after ayanamsa.
- Bracketing: detect sign change of sep - phase_angle or minimal_abs within gate; ensure unwrapped continuity to avoid 0/360 jumps.
- Refinement: same solver family as ingress; objective = signed_min_diff(sep, target_phase); tolerance similar to ingress; record iterations.
- Multiple phases near boundary: process phases in ascending order with independent brackets to avoid double counting; merge-window resolves collisions.
- Output: synodic_phase event with phase_angle, bodies, raw separation, delta, uncertainty_seconds if fallback.

## Retrograde and Station Logic
- Velocity estimation: sample longitudes before/after probe window; use signed_min_diff to detect rate sign; adaptive probe based on approximate speed (faster bodies → smaller window).
- Retro interval start: detect forward→retro sign flip; bracket with prior/next sample; refine on rate zero crossing.
- Retro interval end: detect retro→forward similarly; produce start/end times as interval.
- Probe window table: Moon 2h; Mercury/Venus 6h; Mars/Sun 12h; Jupiter/Saturn 18h; outers 24h. User override allowed within CLI bounds.
- Station events: emit instants at each zero crossing with direction flag; default station_strength computed as |rate_before| + |rate_after| using probe velocities; set to None on refinement fallback.
- Overlaps: ingress computed independently; merge rules decide ordering display; both events persist.
- Handling noisy rates: enforce minimum probe window; if sign flip ambiguous, widen window or mark uncertainty and fallback to midpoint.

## Perihelion/Aphelion Markers
- Applicability: only when distance available for body; skip otherwise with log.
- Detection: sample distance over coarse grid; look for derivative sign change (min/max); bracket extremum and refine with golden-section or Brent on distance derivative approximation.
- Tolerance: relaxed (e.g., ≤30s) given slow variation; record uncertainty if curvature is shallow.
- Output: event_type perihelion/aphelion with distance_au and optional uncertainty.

## Nodes/Apogee/Perigee (Optional)
- If kernels provide positions, treat as single-body longitude/latitude; for apogee/perigee use distance extrema similar to perihelion/aphelion.
- For Nodes, consider ecliptic latitude zero crossing (ascending/descending); bracket and refine latitude sign change.

## Performance Levers
- Base step per body class and per pair class; cap maximum angle change per step to avoid skipped crossings.
- Cache positions and separations; share caches across ingress, retro, and synodic computations within a run.
- Chunk long windows (e.g., per quarter or per year) to bound cache; carry forward last samples to avoid gaps at chunk seams.
- Early gating: if separation far from any target phase (>guard band), skip refine.
- Optional vectorization: future hook; current design keeps scalar but cache-friendly.

## Error Handling and Fallbacks
- Out-of-range requests: immediate error with coverage info; no partial results.
- Missing kernels: configurable hard fail vs soft skip with warning; always report skipped bodies.
- Solver fallback: if iterations exceed limit or bracket invalid, return best sampled time with uncertainty_seconds set and convergence_status="fallback"; optionally mark for validation review.
- Numerical wrap issues: enforce unwrapping on brackets; validate monotonicity where required; log anomalies.

## Logging and Metrics (Algorithm-Level)
- Counters: ephemeris_calls, pos_cache_hits/misses, sep_cache_hits/misses, refine_calls, refine_failures, max_iterations, boundary_drops, skipped_bodies.
- Debug hooks: emit brackets and deltas when timing_debug enabled; record per-event uncertainty when fallback.

## Quality Guards
- Minimum step sizes per body; maximum step guard; configurable orb/guard for phase gating.
- Validation hooks: synthetic tests for double ingress, wrap-at-zero, station-on-boundary, long shallow extrema.
