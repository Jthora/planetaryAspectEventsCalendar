# Daily Transit Aspect Generator – Upgrade Tracker

_Last updated: 2025-10-01_

This tracker pairs with the upgrade plan and records implementation progress, owners, and validation status per task.

## Legend
- **Status**: `Backlog`, `In Progress`, `Blocked`, `Ready for Review`, `Done`
- **Owner**: Primary engineer or reviewer responsible
- **Target Release**: Planned semantic version or date milestone
- **QA**: Summary of validation (tests, manual checks)

## Snapshot Summary
| Phase | Focus | Overall Status | Notes |
|-------|-------|----------------|-------|
| Phase 0 | Baseline snapshot | Done | Baseline tagged on 2025-09-28 (commit hash TBD). |
| Phase 1 | Core correctness & data quality | Done | Phase 1 implementation merged; generator smoke-tested on 2025-01-01→2025-01-03 range. |
| Phase 2 | Structural & maintainability | Done | Modules extracted, config introduced, verbose logging live (see test_transits_2025_01_01_03_phase2.ics). |
| Phase 3 | Feature enhancements | Done | Retrograde/ASCII/filters live; lunar phases + guidance validated. |
| Phase 4 | Standards & interoperability | Done | RFC folding, PRODID guard, deterministic ordering folded into serializer. |
| Phase 5 | Performance & scaling | Backlog | Triggered only if profiling warrants. |
| Phase 6 | Testing & quality gates | In Progress | Pytest suite + harness landed; expanding coverage next. |
| Phase 7 | Documentation & release | Backlog | Will trail major feature drops. |

## Detailed Task Board

### Phase 1 – Core Correctness & Data Quality
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P1-01 | Preserve raw separation + delta reporting | Done | GitHub Copilot | v0.2.0 | Manual ICS inspection: raw + Δ recorded for Moon–Venus conj (2025-01-03). |
| P1-02 | Fix cluster best-selection heuristic | Done | GitHub Copilot | v0.2.0 | Verified dedupe retains minimum Δ within 4h window. |
| P1-03 | Enhance detection triggers (orb-entry + sign change) | Done | GitHub Copilot | v0.2.0 | Synthetic scan (1–3 Jan 2025) confirmed capture despite coarse step. |
| P1-04 | Implement binary/ternary refinement | Done | GitHub Copilot | v0.2.0 | Refined Moon–Venus conjunction now timed to 16:20:47Z (vs coarse 16:20). |
| P1-05 | Remove global `PLANETS` mutation | Done | GitHub Copilot | v0.2.0 | Code review: planet list now passed explicitly; no globals mutated. |
| P1-06 | Add `--inclusive-end` control | Done | GitHub Copilot | v0.2.0 | CLI flag verified: inclusive filter includes boundary events when enabled. |

### Phase 2 – Structural & Maintainability
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P2-01 | Extract aspect math module | Done | GitHub Copilot | v0.3.0 | `daily_transit/aspect_detection.py` created; generator imports shared logic. |
| P2-02 | Extract ICS builder module | Done | GitHub Copilot | v0.3.0 | `daily_transit/ics_builder.py` handles event construction; ICS run verified. |
| P2-03 | Introduce configuration dataclass | Done | GitHub Copilot | v0.3.0 | `daily_transit/config.py` dataclass wired through CLI. |
| P2-04 | Add `--verbose` logging + structured logging levels | Done | GitHub Copilot | v0.3.0 | `--verbose` flag prints INFO/DEBUG to console; seen in latest run. |

### Phase 3 – Feature Enhancements
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P3-01 | Retrograde flagging in events | Done | GitHub Copilot | v0.4.0 | Mercury ℞ vs. Venus conjunction captured in `output/test_retro.ics`. |
| P3-02 | `--planets` subset filter | Done | GitHub Copilot | v0.4.0 | `output/test_subset_month.ics` shows Sun/Moon-only calendar. |
| P3-03 | Lunar phases integration | Done | GitHub Copilot | v0.4.x | `output/test_with_phases.ics` includes 4 Jan 2024 cycle events. |
| P3-04 | ASCII-only mode | Done | GitHub Copilot | v0.4.x | ASCII sample `output/test_ascii_full.ics` verified (labels & retro marker "R"). |
| P3-05 | Outer planet support guidance | Done | GitHub Copilot | v0.4.x | Warns when kernel lacks requested bodies; see verbose log w/ `de440s.bsp`. |

### Phase 4 – Standards & Interoperability
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P4-01 | Implement RFC 5545 line folding | Done | GitHub Copilot | v0.5.0 | `output/test_with_summary_phase4.ics` shows folded DESCRIPTION lines. |
| P4-02 | Reintroduce configurable PRODID safely | Done | GitHub Copilot | v0.5.0 | PRODID preserved via manual serializer; see header in phase4 samples. |
| P4-03 | Deterministic event ordering | Done | GitHub Copilot | v0.5.0 | `test_with_summary_phase4.ics` lists daily → lunar phases → aspects. |
| P4-04 | UID stability guard | Done | GitHub Copilot | v0.5.0 | Deterministic hash-based UIDs verified across reruns. |

### Phase 5 – Performance & Scaling
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P5-01 | Adaptive coarse step logic | Backlog | _Unassigned_ | TBD | Profiling before/after; acceptance threshold defined. |
| P5-02 | Longitudes caching | Backlog | _Unassigned_ | TBD | CPU sample count reduction >30%. |
| P5-03 | Parallel processing exploration | Backlog | _Unassigned_ | TBD | Ensure reproducible output order. |

### Phase 6 – Testing & Quality Gates
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P6-01 | Pytest harness with synthetic ephemeris | Done | GitHub Copilot | v0.5.0 | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest` → 7 tests passing. |
| P6-02 | Static typing with mypy | Backlog | _Unassigned_ | With Phase 2 completion | mypy config and CI target. |
| P6-03 | Linting (ruff/flake8) | Backlog | _Unassigned_ | With Phase 2 completion | Lint command documented. |
| P6-04 | Build scripts (`make`/`tox`) | Backlog | _Unassigned_ | With Phase 2 completion | New developers can run setup quickly. |

### Phase 7 – Documentation & Release
| ID | Task | Status | Owner | Target Release | QA Notes |
|----|------|--------|-------|----------------|----------|
| P7-01 | README refresh (new flags & workflow) | Backlog | _Unassigned_ | After Phase 1 | README diff reviewed. |
| P7-02 | CHANGELOG creation | Backlog | _Unassigned_ | After Phase 1 | v0.2.0 entry drafted. |
| P7-03 | Example ICS samples | Backlog | _Unassigned_ | After Phase 3 | Zip/tested ICS artifacts added. |
| P7-04 | Contributor guide | Backlog | _Unassigned_ | After Phase 6 | Covers tests, review expectations. |

## Risk & Dependency Notes
- Phase 2+ ticket work should not begin until Phase 1 tasks are marked `Done` to avoid compounding defects.
- Testing infrastructure (Phase 6) is best started alongside Phase 1 so future PRs have safety nets.
- Performance optimization (Phase 5) hinges on profiling data; keep tasks in `Backlog` until metrics warrant investment.

## Change Log
- **2025-09-28**: Phase 2 completed; modularization + verbose logging validated with `test_transits_2025_01_01_03_phase2.ics`.
- **2025-09-28**: Phase 1 completed and tracker updated after ICS regression (`test_transits_2025_01_01_03_phase1c.ics`).
- **2025-09-28**: Tracker initialized with baseline status and tasks (authored by GitHub Copilot).
