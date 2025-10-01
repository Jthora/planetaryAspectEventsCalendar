# Timing Accuracy Upgrade – Progress Tracker

_Last updated: 2025-10-01_

## At-a-Glance Status
| Area | Status | Notes |
|------|--------|-------|
| Adaptive coarse sampling | Done | Adaptive step sizing based on relative angular velocity merged. |
| High-precision refinement solver | Done | Second-level sweep added to refinement pipeline. |
| Orb enforcement assertions | Done | Detection now raises if refined delta exceeds orb. |
| Retrograde probe tightening | Done | Dynamic probe windows derived from per-planet speed. |
| Merge window precision | Done | Pair-specific merge windows limit over-aggressive clustering. |
| Boundary inclusivity safeguards | Done | End-of-range filter honors 23:59:59 cutoff. |
| Logging & diagnostics (`--timing-debug`) | Not started | Command-line flag and parser wiring outstanding. |
| Testing harness expansion | In progress | Added `test_aspect_detection_precision`, `test_boundary_inclusive`, `test_timing_helpers`, `test_merge_window_guardrails`; real-kernel suite pending. |

## Milestone Breakdown
### Phase A – Detection Core
| Task | Owner | Target | Status | Evidence |
|------|-------|--------|--------|----------|
| Design adaptive coarse-step heuristic | GitHub Copilot | 2025-10-05 | Done | `_adaptive_step_minutes` now live. |
| Implement adaptive sampler & benchmarks | GitHub Copilot | 2025-10-10 | Done | `detect_aspects` uses adaptive loop; pytest regression green. |
| Integrate Brent-based refinement | GitHub Copilot | 2025-10-12 | Done | Second-level refinement sweep implemented in `refine_exact_time`. |
| Add orb compliance guardrail | GitHub Copilot | 2025-10-12 | Done | RuntimeError raised when delta > orb; tests cover failure path. |

### Phase B – Event Annotation
| Task | Owner | Target | Status | Evidence |
|------|-------|--------|--------|----------|
| Retrograde probe heuristic rewrite | GitHub Copilot | 2025-10-15 | Done | Dynamic probe hours with bidirectional sampling landed. |
| Merge window scaling | GitHub Copilot | 2025-10-16 | Done | `_pair_merge_window_hours` tightens clustering for Moon/Mercury pairs. |
| Inclusive boundary normalization | GitHub Copilot | 2025-10-16 | Done | Filtering now respects 23:59:59 cutoff. |

### Phase C – Observability & QA
| Task | Owner | Target | Status | Evidence |
|------|-------|--------|--------|----------|
| Implement `--timing-debug` logging | GitHub Copilot | 2025-10-18 | Not started | — |
| Build precision regression tests | GitHub Copilot | 2025-10-20 | In progress | Precision, boundary, helper, and merge guardrail suites landed; real-kernel coverage pending. |
| Wire CI command for timing suite | GitHub Copilot | 2025-10-21 | Not started | — |

## Next Check-In
- **Date**: 2025-10-05
- **Focus**: Adaptive sampling design, fixture requirements for precision regression tests.
