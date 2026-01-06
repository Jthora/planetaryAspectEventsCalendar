# HelioNext Performance Plan

## Baseline
- Measure legacy: coarse iterations (steps per body pair), refine count/time (exact-time solver invocations), retro checks, total runtime on representative ranges (short, monthly, yearly spans; Moon-heavy vs outer pairs). Define measurement units (seconds, counts) to align comparisons.

### Baseline capture
- Scenarios (matching benchmarks below) with legacy engine only.
- Metrics stored as JSON: {scenario, duration_s, coarse_steps, refine_calls, refine_time_s, retro_checks, ephemeris_calls, cache_hits/misses(if avail)}.

## Targets
- Overall: ≥3× faster than legacy on benchmark set (same inputs/scopes).
- Stage budgets: refine dominates; aim ≥5× speedup in refine path. Coarse and retro keep at or below legacy costs.

### Acceptance per scenario
- Short (3d): HelioNext runtime ≤ legacy/3.
- Medium (1mo): HelioNext runtime ≤ legacy/3.
- Long (1y): HelioNext runtime ≤ legacy/3; no phase exceeding 50% of total time.

## Benchmarks
- Scenarios: short (3 days), medium (1 month), long (1 year) across aspect scopes and ayanamsa modes.
- Include edge cases with dense Moon activity (fast mover) and slow outer pairs (Saturn-Pluto) to test adaptive steps.

### Concrete scenarios
- Short: 2025-01-01 to 2025-01-03, aspect scope complete, tropical and galactic_core (two runs), lat/lon provided.
- Medium: 2025-01-01 to 2025-01-31, aspect scope major, tropical.
- Long: 2025-01-01 to 2025-12-31, aspect scope complete, tropical.
- Stress: 7-day dense Moon window with minor/tertiary enabled, galactic_core.

## Instrumentation
- Metrics: coarse steps per pair, refine attempts/success, solver iterations, cache hit rates, ephemeris calls, runtime per stage, total runtime.
- Logging: summary per run; optional debug sampling (e.g., slowest aspects, worst-case iterations).

### Metric definitions
- `coarse_steps`: count of coarse time steps evaluated per pair.
- `refine_attempts`: number of refine solver invocations; `refine_success`: those converged.
- `solver_iterations`: per-refine iteration counts; log max/avg.
- `cache_hit_rate`: positions/separations if cache enabled.
- `ephemeris_calls`: total calls to ephemeris adapter.
- `runtime_stage`: time per stage (coarse, refine, retro/station, format) and total.

## Acceptance
- Meet targets without event regressions (per validation doc tolerance rules).
- No pathological slowdowns on any tested scenario; watch for worst-case refine loops.

## Profiling Approach
- Use profiling on hot runs to confirm hotspots (focus on ephemeris calls and solver iterations).
- Compare solver choices (Brent vs Newton hybrid) under same scenarios with identical inputs.

## Optimization Priorities
- First: refine solver replacement and caching reuse (largest impact).
- Second: adaptive coarse step/gating to cut unnecessary refine calls.
- Third: optional batching/vectorization once correctness is stable.
