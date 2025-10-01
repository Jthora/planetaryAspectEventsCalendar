# Timing Accuracy Testing Roadmap

_Last updated: 2025-10-01_

This roadmap defines the automated coverage required to guarantee second-level timing accuracy without changing the ephemeris kernel.

## Test Suites Overview
| Suite | Purpose | Priority | Notes |
|-------|---------|----------|-------|
| `tests/test_aspect_detection_precision.py` | Validate adaptive sampling, refinement, and orb enforcement using synthetic ephemeris fixtures. | High | Blocks rollout of new detection logic. |
| `tests/test_retrograde_precision.py` | Ensure retrograde probes remain stable around stations with sub-hour sampling. | Medium | Depends on retrograde heuristic rewrite. |
| `tests/test_merge_window_guardrails.py` | Confirm duplicate clustering keeps truly distinct events and honors tightened window. | Done | Uses synthetic AspectEvent samples to validate merging. |
| `tests/test_timing_helpers.py` | Exercise helper heuristics (_adaptive_step, probe sizing, merge window scaling). | Done | Guards edge-case parameter heuristics. |
| `tests/test_end_to_end_timing.py` | Integration regression using cached real Skyfield results for a 48h range. | High | Provides ground truth comparison within ±1 second. |
| `tests/test_boundary_inclusive.py` | Verifies inclusive end-date events serialize when exactly on the boundary second. | Medium | Shares fixtures with detection precision suite. |

## Fixture Plan
- **Synthetic Ephemeris (`fixtures/synthetic_ephemeris.py`)**
  - Provides deterministic `observe()` implementations with configurable angular velocities and retrograde segments.
  - Includes helpers to inject leap-second scenarios for boundary testing.
- **Cached Skyfield Results (`fixtures/real_world_samples/`)
  - Stores JSON or CSV snapshots (timestamp, planet pair, aspect, delta) for short ranges generated once with the current kernel.
  - Used by end-to-end timing regression to compare against live output.

## Acceptance Criteria per Suite
1. **Aspect Detection Precision**
   - Max absolute timestamp error ≤ 1 second for all synthetic test cases.
   - Assert `delta <= orb` for every detected aspect; raise failure otherwise.
2. **Retrograde Precision**
   - Retrograde flags match expected state before, during, and after station points.
   - Probe duration adapts to planet speed and remains ≤ 3 hours.
3. **Merge Window Guardrails**
   - Distinct events ≥ 5 minutes apart always persist.
   - Duplicate events within 0.01° and 5 minutes merge to the smallest delta instance.
4. **End-to-End Timing**
   - Live generator output matches cached baseline within ±1 second for each aspect.
   - ICS snapshot diff highlights only textual differences (folding, metadata) if any.
5. **Boundary Inclusive**
   - Events at exactly `end_date 23:59:59` appear when `--inclusive-end` is enabled.
   - Same events are excluded when the flag is absent.

## Execution & Automation
- **Local command**
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_aspect_detection_precision.py tests/test_end_to_end_timing.py
  ```
- **CI Pipeline**
  - Stage 1: run precision suites (fast synthetic tests).
  - Stage 2: run end-to-end regression (allowed to take longer; can be nightly if runtime exceeds 2 minutes).
  - Artifact retention: upload ICS outputs and comparison reports for traceability.

## Documentation Hooks
- Link this roadmap and the progress tracker from the main timing playbook for visibility.
- Update `README.md` once suites are implemented to guide contributors on running accuracy checks.

## Open Questions
- Should cached real-world fixtures be regenerated per release or locked until the ephemeris changes?
- What tolerance should we allow for floating-point drift when comparing deltas (<0.001°?).
- Do we need additional suites for ASCII/Unicode serialization impact on line folding at second-level timestamps?
