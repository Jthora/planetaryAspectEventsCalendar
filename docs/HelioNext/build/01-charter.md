# HelioNext Charter

## Purpose
- Build a parallel event-detection engine (HelioNext) to replace/augment legacy detection with higher performance and maintainable algorithms while preserving all current capabilities.
- "Parallel" means it can run alongside the legacy engine with a runtime switch; no user-visible regression during transition.

## Goals
- Feature parity with legacy for aspects, bodies/points, ayanamsas (zodiac offsets), houses, retro/station flags, titles/labels/Δ (orb delta).
- Speedup target: ≥3× end-to-end vs legacy on representative ranges (same date ranges, scopes, and modes).
- Stability: deterministic outputs within defined tolerances; clear fallbacks to legacy when HelioNext is disabled.
- Observability: metrics for coarse/refine counts, runtime per stage, cache hit rates; all terms defined in validation/perf docs.

## Non-goals
- Changing user-facing ICS formatting or titles beyond necessary parity alignment (ICS folding stays 75 bytes, same glyphs/labels).
- Altering aspect catalogs or orbs unless explicitly flagged (major/minor/tertiary definitions stay the same).
- Replacing ephemeris sources (Skyfield + current kernels remain).

## Success Criteria
- Event diff: no missing/extra events vs legacy; time deltas within tolerance (see validation doc for threshold definition).
- Performance: meets or beats speedup target on benchmark scenarios (defined in perf plan).
- Toggle: runtime switch between legacy and HelioNext; safe rollback path always available.
- Quality: validation suite passes across modes (tropical/galactic), scopes (major/minor/tertiary), and edge cases (retrogrades, cusps).

## Constraints
- Must reuse existing ephemeris/time/house utilities where feasible to avoid divergence in math and formatting.
- Maintain ICS folding (75-byte lines) and payload fields expected by downstream formatters (titles, Δ, houses, glyphs).
- Preserve configurability of aspect scopes and ayanamsa modes; CLI/flags remain stable.

## Risks & Mitigations
- Regression risk (mismatched events/times): use dual-run diff harness and staged rollout; keep legacy fallback.
- Performance shortfall: prioritize refine/root-finding and caching; profile early with benchmarks.
- Scope creep: feature parity matrix to gate changes; changelog records any temporary deviations.

## Stakeholders
- Engineering: implementation/maintenance of HelioNext and toggle.
- QA/Analyst: validation, diffing, performance checks.
- Users: consumers of ICS/calendar exports; must experience no regressions.

## Milestones
- M1: Interfaces and toggle scaffold in place (factory, DTO alignment).
- M2: HelioNext coarse/refine/retro implemented with caching and angle wrapping handled.
- M3: Validation harness + parity pass on golden ranges (diff reports clean within tolerance).
- M4: Performance targets met; rollout plan approved (HelioNext default possible).
- M5: Legacy path retired after stability window and user confirmation.
