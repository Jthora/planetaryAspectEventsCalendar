# Daily Transit Aspect Generator – Upgrade Plan

_Last updated: 2025-10-01_

## Context
The `DailyTransitAspectCalendarGenerator.py` script now delivers Thunderbird-friendly tropical aspect calendars, but it still contains data-quality gaps and structural debt (duplicate aspects, coarse detection heuristics, mutable globals, etc.). This document captures a staged plan to evolve the generator safely while keeping the tool usable after every step.

## Assumptions
- Work continues on Linux with Python 3.11+ and the existing `.venv` environment.
- The short JPL kernel `de440s.bsp` remains the default, though the plan anticipates optional support for richer kernels.
- Calendar clients tested: Thunderbird (primary), Apple Calendar (secondary sanity check as needed).
- Feature cadence should favor incremental pull requests/commits per phase.

## Guiding Principles
1. **Continuous usability** – each phase yields a working script with documented changes.
2. **Deterministic outputs** – calendar re-generation should remain stable (UIDs unchanged unless behavior legitimately shifts).
3. **Precision first, features second** – correctness and data clarity improvements take priority over new capabilities.
4. **Test as we go** – add automated coverage alongside meaningful behavior changes.

## Phase Breakdown

### Phase 0 – Baseline Snapshot
- Tag or archive the current script (e.g., `DailyTransitAspectCalendarGenerator_baseline.py`).
- Purpose: quick rollback reference before deeper refactors.

### Phase 1 – Core Correctness & Data Quality (High Priority)
- **Separation Representation**: track both raw separation (0–360°) and delta-to-target; surface delta in descriptions.
- **Cluster Selection Fix**: choose aspect occurrences using delta-to-target instead of raw separation magnitude.
- **Detection Trigger Enhancements**: add orb-entry and sign-change triggers to catch minima between coarse samples.
- **Binary/Ternary Refinement**: replace linear sweep with iterative midpoint refinement for higher timing accuracy.
- **No Global Mutation**: stop mutating `PLANETS`; pass filtered lists explicitly.
- **Boundary Inclusion Flag**: add `--inclusive-end` to control end-date event inclusion semantics.

### Phase 2 – Structural & Maintainability
- **Module Split**: separate aspect math, ICS builders, and CLI entry point.
- **Dependency Injection**: thread ephemeris, timescale, and planet sets via parameters/config.
- **Config Dataclass**: centralize runtime knobs for easier testing.
- **Logging Controls**: add `--verbose` for richer console insight; keep default output quiet.

### Phase 3 – Feature Enhancements
- **Retrograde Indicators** _(Done)_: annotate retrograde planets at event time (`℞` glyph or `R` in ASCII mode).
- **Planet Subset Filtering** _(Done)_: allow `--planets` to restrict pair generation.
- **Lunar Phases Integration** _(Done)_: optional events from existing lunar phase logic; cross-reference near-aspect events.
- **ASCII Fallback** _(Done)_: glyph-free presentation for limited-font environments.
- **Outer Planet Support Guidance** _(Done)_: detect missing bodies and suggest larger kernels.

### Phase 4 – Standards & Interoperability
- **RFC 5545 Folding** _(Done)_: ensure long lines (DESCRIPTION, SUMMARY) are compliant.
- **PRODID Management** _(Done)_: safely apply configurable PRODID without causing ics library issues.
- **Deterministic Ordering** _(Done)_: enforce event sorting (daily summary → phases → aspects).
- **UID Stability Checks** _(Done)_: automated guard to ensure repeated runs keep identifiers intact.

### Phase 5 – Performance & Scaling (as needed)
- **Adaptive Coarse Step**: tighten sampling automatically for Moon pairs, relax for slow movers.
- **Caching Longitudes**: reuse per-timestamp longitude calculations across pairs.
- **Parallelization Exploration**: profile and, if beneficial, parallelize pair evaluation.

### Phase 6 – Testing & Quality Gates
- **Pytest Suite**: add fixtures and tests (cluster selection, retrofit detection, retrograde flags, ASCII mode).
- **Static Analysis**: introduce `mypy` + linter (e.g., `ruff` or `flake8`).
- **Build Scripts**: provide `make` or `tox` targets for lint/test/run-sample.

### Phase 7 – Documentation & Release
- **README Update**: detail new flags, tuning advice, ephemeris requirements.
- **CHANGELOG**: begin versioning (e.g., `v0.2.0` for Phase 1 completion).
- **Examples**: include short-range ICS samples demonstrating features.
- **Contributor Guide**: expectations for tests, style, and release process.

## Dependencies & Sequencing Notes
- Phase 1 should land before any large refactor; later phases assume the data-layer corrections.
- Structural refactors (Phase 2) should coincide with test scaffolding (Phase 6) to preserve behavior.
- Feature work (Phase 3) can be split into independent sub-branches once core is stable.
- Standards adjustments (Phase 4) are low-risk but should follow feature additions to avoid constant re-folding.

## Exit Criteria Summary
| Phase | Key Deliverable | Verification |
|-------|-----------------|--------------|
| 1     | Accurate aspect detections & deltas | Regression run vs. baseline + manual spot checks |
| 2     | Modularized codebase | Unit tests import modules; CLI still works |
| 3     | Feature toggles & retrograde | Targeted fixtures confirm feature output |
| 4     | Standards compliance | ICS validator / Thunderbird import |
| 5     | Runtime efficiency | Profiling before/after showing gains |
| 6     | Automated safety net | `pytest -q` + linting pass |
| 7     | Updated docs & samples | README + CHANGELOG present changes |

## Open Questions
- Should lunar phases share the same calendar output by default or live in a companion file?
- Do we version releases semantically (`v0.x`) or date-based? (recommend semantic).
- Preferred threshold for retrograde detection (6h vs. 24h look-ahead/back).

## Next Steps
1. Launch Phase 6 testing initiative (pytest suite + static analysis) to lock in recent behavior.
2. Begin Phase 4 review/validation with strict ICS clients (Thunderbird, Apple Calendar).
3. Draft documentation artefacts (README expansions, CHANGELOG entries) in preparation for v0.4.0.
