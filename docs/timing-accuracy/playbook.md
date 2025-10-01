# Daily Transit Timing Accuracy Playbook

_Last updated: 2025-10-01_

## Scope & Constraints
- **Goal**: Improve event timestamps to second-level accuracy using the existing `de440s.bsp` kernel (no ephemeris upgrades).
- **Context**: Applies to `DailyTransitAspectCalendarGenerator.py` and supporting modules in `daily_transit/`.
- **Why it matters**: Downstream calendars (Thunderbird, Apple Calendar) display planetary events in chronological order. Even a 60-second miss can flip the perceived sequence or alter retrograde flags.

## Guiding Principles
1. **Preserve kernel fidelity** – treat ephemeris data as authoritative; we may interpolate more often but never resample beyond Skyfield’s precision.
2. **Tighten the bracket** – of all parameters, the coarse scan interval has the largest impact on timing drift. Shrink it intelligently before adding more iteration complexity.
3. **Fail loudly** – every detected aspect should prove it satisfies the configured orb; if it slips outside, we abort instead of logging and continuing.
4. **Benchmark continuously** – couple each algorithm tweak with deterministic tests so regressions are caught immediately.

## Improvement Roadmap (Ephemeris-Unchanged)

### 1. Adaptive Coarse Sampling _(Done – 2025-10-01)_
- **Problem**: Fixed 60-minute sweep can overshoot fast movers (Moon, Mercury) by several minutes.
- **Actions**:
  - ✅ Runtime relative-speed heuristic chooses tighter coarse steps (`_adaptive_step_minutes`).
  - ✅ Planet/pair velocity cache reused per iteration to limit recalculation.
- **Validation**:
  - ✅ `tests/test_aspect_detection_precision.py::test_detect_aspects_produces_precise_event` verifies adaptive loop hits the second-level target.

### 2. Higher-Fidelity Refinement _(Done – 2025-10-01)_
- **Problem**: Current ternary search stops once the span is smaller than `refine_step_mins`; this can still be several minutes.
- **Actions**:
  - ✅ Added final one-second sweep after ternary refinement to reach sub-second precision.
  - ✅ Additional sampling stops once span ≤ 30 seconds, preventing runaway loops.
- **Validation**:
  - ✅ `tests/test_aspect_detection_precision.py::test_refine_exact_time_reaches_second_precision` confirms behaviour.

### 3. Strict Orb Enforcement _(Done – 2025-10-01)_
- **Problem**: Minor floating-point drift could accept events outside the orb.
- **Actions**:
  - ✅ Detection now raises when `delta > orb + 1e-6`, logging an error with context.
- **Validation**:
  - ✅ `tests/test_aspect_detection_precision.py::test_detect_aspects_raises_when_refined_delta_beyond_orb` guards the failure mode.

### 4. Retrograde Probe Tightening _(Done – 2025-10-01)_
- **Problem**: 6-hour probe window may cross a direction-change, flipping the retrograde flag.
- **Actions**:
  - ✅ `_dynamic_probe_hours` shrinks probes based on speed; `is_retrograde` samples before and after.
- **Validation**:
  - ✅ `tests/test_aspect_detection_precision.py::test_is_retrograde_detects_negative_motion` covers retrograde vs. direct motion.

### 5. Merge Window Precision _(Done – 2025-10-01)_
- **Problem**: 4-hour merge window can swallow distinct events when timestamps are seconds apart.
- **Actions**:
  - ✅ `_pair_merge_window_hours` scales windows (Moon ≤ 30 min, Mercury/Venus ≤ 1 hr).
- **Validation**:
  - ✅ `tests/test_merge_window_guardrails.py` ensures clusters collapse while slow movers persist.

### 6. Boundary & Inclusivity Safeguards _(Done – 2025-10-01)_
- **Problem**: Inclusive end-date logic may discard events exactly at the boundary.
- **Actions**:
  - ✅ Generator filtering now honours 23:59:59 cut-off when inclusive.
- **Validation**:
  - ✅ `tests/test_boundary_inclusive.py` verifies inclusive vs. exclusive behaviours.

## Testing Strategy Updates
- **Unit Tests**
  - ✅ `tests/test_aspect_detection_precision.py`: adaptive sampling, refinement, orb guards, retrograde detection.
  - ✅ `tests/test_boundary_inclusive.py`: inclusive vs. exclusive end-date handling.
  - ⏳ `tests/test_merge_window_guardrails.py` / `tests/test_end_to_end_timing.py`: pending clustered + real-kernel coverage (see Testing Roadmap).
- **Fixtures**
  - Deterministic synthetic ephemeris classes with controllable angular velocity and retrograde segments.
  - Snapshot ICS outputs stored under `tests/fixtures/timing_accuracy/` for regression.
- **CI Commands**
  ```bash
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest --maxfail=1 -q
  ```

## Monitoring & Diagnostics
- Use `--timing-debug` to emit:
  - Coarse step duration chosen per pair.
  - Pre/post-refinement timestamps and deltas.
  - Retrograde probe results and merge window sizing.
- Provide a helper script (`tools/analyze_timing_debug.py`) to parse logs and summarize worst-case deltas.

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Increased runtime from tighter sampling | Cache longitudes per timestamp; allow users to opt into "standard" mode via flag. |
| False positives from synthetic tests diverging from real dynamics | Pair every synthetic test with at least one integration test using actual `de440s` data. |
| Floating-point noise around leap seconds | Rely on Skyfield for UTC handling; include tests straddling leap-second dates (e.g., 2016-12-31). |

## Next Steps Checklist
- [x] Prototype adaptive coarse-step logic and benchmark runtime impact.
- [x] Implement second-level refinement and compare precision vs. ternary.
- [x] Add orb enforcement assertions and corresponding failure tests.
- [x] Introduce timing-focused pytest modules with synthetic fixtures.
- [ ] Document `--timing-debug` usage in `README.md` once implemented.
- [ ] Add clustered-event and real-kernel regression suites per testing roadmap.

With these deliverables, we can honor second-level accuracy expectations without changing the ephemeris while keeping the codebase observable and testable throughout the upgrade.
