# HelioNext Algorithm Design

## Overview
Design for coarse scan, refine, retro/station detection, and supporting angle logic. Terms: "coarse" is the stepping phase; "refine" is the exact-time solver; "retro/station" covers motion state flags.

## Coarse Scan
- Adaptive step per pair (fast movers small step, slow pairs larger) to balance accuracy and speed.
- Gating: reject candidates when separation is far outside orb before refine ("orb" = allowed deviation from exact angle).
- Bracketing: detect crossings of separation-target sign to seed refine; ensures solver starts with a valid interval.
- Handles aspect scopes (major/minor/tertiary) via shared catalog; scope filters applied upfront.

### Proposed step heuristics
- Moon vs any: 15-minute coarse step; tighten to 5-minute if minor/tertiary enabled.
- Inner (Mercury/Venus) pairs: 30-minute coarse step.
- Inner vs outer: 60-minute coarse step.
- Outer vs outer (Jupiter+): 4–6 hour coarse step.
- All steps subject to max angular change heuristic (e.g., limit to 1/3 of smallest orb per step).

### Gating thresholds
- Skip refine if |separation - target_angle| > 2× orb at coarse sample boundary.
- Require sign change of (separation - target) within bracket before invoking refine.

## Refine (Exact Time)
- Root function: separation(angle(body1, body2)) - target_angle (target_angle comes from aspect catalog).
- Solver: small-step Brent or linear + 1 Newton using relative velocity (relative velocity = d/dt of separation estimate).
- Angle wrapping: normalize to 0–360; ensure continuity across 0/360 to avoid false jumps.
- Convergence: tolerance (time) and max iterations; fallback to bracket midpoint if needed.
- Output: refined time, separation delta (Δ), positions reused for payload and Δ computation.

### Solver details
- Initial estimate: linear interpolation using separation at bracket ends; seed Newton with relative velocity if available.
- Preferred solver: Brent within bracket [t0, t1] with f = separation - target_angle.
- Convergence: target ≤ 0.5s wall-clock tolerance; max iterations 12; fallback to mid if not converged.
- Handle wrap: unwrap separation across 0/360 within bracket before computing f.

## Retrograde / Station
- Use reused samples from refine for velocity sign checks (velocity sign change near zero = station).
- Detect retrograde flag and station proximity per legacy criteria; no change to thresholds.

### Criteria
- Retrograde: longitude rate < 0 for the body at refined time.
- Station: |rate| < epsilon (e.g., 0.01 deg/day) and sign change within ±12 hours window; epsilon matches legacy.

## Houses and Positions
- House calc via shared utility (lat/lon/time); same method as legacy (house system unchanged).
- Positions/longitudes drawn from shared ephemeris adapter with ayanamsa applied; ayanamsa = zodiac offset (e.g., galactic center).

## Angle and Orb Handling
- Apply orbs per aspect definition; support scope filters to include/exclude aspect sets.
- Normalize all angles consistently; handle cusp crossings (sign boundaries) and 0/360 wrap.

### Orb policy
- Use legacy orb map per aspect type; no changes unless config overrides.
- Evaluate |separation - target| using unwrapped separation around the aspect crossing.

## Error Handling
- Solver failure: retry with fallback bracket; log and skip if unrecoverable, marking the event as dropped.
- Invalid config/time: raise clear errors to caller (bad ranges, unsupported modes).

## Extensibility Hooks
- Plug-in solvers/step strategies via config for experiments (e.g., Newton vs Brent).
- Future batching/vectorization can reuse separation/position abstractions; keep function signatures array-friendly.
