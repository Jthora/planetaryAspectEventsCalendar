# Edge Cases and Policies

## Ingress and Wraps
- Double ingress within one coarse step (fast Moon or large step): detect via angle delta > sign size; sub-step to find both crossings; add test.
- Station exactly at sign boundary: emit both station and ingress; merge policy should not drop either; ordering clarified.
- Ayanamsa-adjusted wrap at 0/360: unwrap across boundary for interpolation; avoid false sign flips from wrap artifacts.
- Sign list subsets: ensure skipping signs does not mis-detect crossings; if user restricts to a subset, still avoid false positives.

## Retro and Synodic Interactions
- Retro interval overlapping ingress: compute independently; both events emitted; merging only for identical types within merge window.
- Synodic wrap at 0/360: always use signed_min_diff to detect phase crossings; handle angle 0 vs 360 equivalence cleanly.
- Multiple phases near boundaries: ensure independent bracketing; guard against double-emitting same phase in one bracket.
- Slow pairs with long phases: ensure step size is large enough for performance but still respects gating; consider sparse output by design.

## Stations and Velocity Nuances
- Shallow velocity near station: solver may yield larger uncertainty; include uncertainty_seconds and possibly mark STATUS=TENTATIVE.
- Probe window too small: adaptively widen; cap max to avoid excessive ephemeris calls.
- Spurious rate sign flips due to noise: enforce minimum magnitude threshold before declaring station/retro change.

## Missing Data and Limits
- Missing kernels/unsupported bodies: policy flag fail|skip; always log skipped bodies; include in metrics.
- Missing distance for perihelion/aphelion: skip those events with note; do not emit placeholders.
- If ayanamsa constants are placeholders (galactic_core), add warning; allow override via config injection.

## Chunking and Seams
- When chunking long spans, include overlap to avoid missed crossings; dedupe across seams using merge window.
- Report chunk_id in debug to trace seam-related issues; ensure ordering after concat is stable.

## Boundary Behavior
- No projection beyond requested window or ephemeris bounds; discard refined hits outside window with counter increment.
- If user range partially exceeds coverage and policy is "fail", abort before work; if policy ever allows "truncate", document clearly (default = fail).

## Determinism
- Stable sorting: time, event_type, body tuple.
- Merge-window dedupe policy deterministic: prefer lowest uncertainty then earliest time.
- No random backoff or probabilistic retries.

## Error Surfacing
- Provide specific error codes/messages: MISSING_KERNEL(body), OUT_OF_RANGE(body, min, max), BAD_PHASE(angle), BAD_AYANAMSA(name).
- Retro/phase solver failures: mark events with convergence_status and uncertainty or drop with log; never silently degrade.

## User Overrides
- Allow config to tighten/loosen merge windows, tolerances, and probe sizes; document defaults and safe ranges.
- Allow disabling specific event types to avoid overload on long spans (e.g., disable synodic for all pairs on century runs).

## Testing Focus
- Explicit tests for: double ingress, station-at-boundary, wrap at 0/360, synodic duplicate suppression, retro overlap, seam dedupe, missing kernel handling.
