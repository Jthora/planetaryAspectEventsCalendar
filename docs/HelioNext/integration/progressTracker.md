# HelioNext Integration Progress Tracker

## Stage 1: Engine Selection & Config
Refs: [cli-and-config.md](cli-and-config.md)
### Phase 1.1: CLI & Config Plumbing
- [x] Step 1.1.1: Add `--engine {legacy,helionext}` to CLIs
	- [x] Sub-step: Update CLI parser in DailyTransitAspectCalendarGenerator.py
	- [x] Sub-step: Update CLI parser in tools/generate_yearly_calendars.py
	- [x] Sub-step: Propagate engine into config factory/helpers
- [ ] Step 1.1.2: Thread engine through config creation to engine_factory
	- [ ] Sub-step: Ensure GeneratorConfig carries engine selection end-to-end
	- [ ] Sub-step: Replace direct detector calls with engine_factory selection
- [ ] Step 1.1.3: Validate engine values and fail fast on invalid input
	- [ ] Sub-task: Add validation logic with clear error messages
- [ ] Step 1.1.4: Add aspect-scope options mapped to catalog (major/minor/tertiary)
	- [ ] Sub-task: Map scopes to aspect catalog in a single helper
	- [ ] Sub-task: Add CLI help text and defaults

### Phase 1.2: Defaults & Docs
- [ ] Step 1.2.1: Document defaults (engine=legacy, aspect_scope=major, orb, merge_window_hours, retro_probe_hours)
	- [ ] Sub-task: Update README
	- [ ] Sub-task: Update HelioNext integration docs
- [ ] Step 1.2.2: Optional ENV override documented for batch runs
	- [ ] Sub-task: Define ENV name and precedence

## Stage 2: Pipeline Hookup
Refs: [pipeline-hookup.md](pipeline-hookup.md)
### Phase 2.1: Detection Wiring
- [x] Step 2.1.1: Replace direct legacy detect calls with engine_factory in generator helpers
	- [x] Sub-task: Adjust generator helper functions to accept engine
	- [x] Sub-task: Ensure backward-compatible defaults
- [x] Step 2.1.2: Confirm ICS builder, titles, interpretations, compact formatter handle HelioNext outputs
	- [x] Sub-task: Smoke test ICS build with helionext
	- [x] Sub-task: Verify titles/interpretations generation paths unchanged (1-day run with aspects)

### Phase 2.2: Contract & Catalog
- [x] Step 2.2.1: Note AspectEvent field contract for downstream consumers
  - [x] Sub-task: Create a brief schema note
- [ ] Step 2.2.2: Align aspect catalog usage across scopes for HelioNext
	- [x] Sub-task: Ensure catalog defaults match scope selections
### Phase 2.3: Interpretation Expansion
Refs: [interpretation-expansion.md](interpretation-expansion.md), [aspect-coverage.md](aspect-coverage.md), [aspect-event-schema.md](aspect-event-schema.md), [guidance/overview.md](../guidance/overview.md)
- [x] Step 2.3.1: Add minor/tertiary routing (bucket or alias) so interpretations resolve for non-majors
- [x] Step 2.3.2: Add fallback text for unmapped aspects using aspect_meanings
- [ ] Step 2.3.3: Populate guidance entries for minor/tertiary aspects (start with standard, then other modes)
- [x] Step 2.3.4: Add alias mapping for synonymous names (Semisextile/Semi-Sextile, Semisquare/SemiSquare, Decile/Semiquintile, Tredecile/Trebiquintile, etc.)

## Stage 3: Testing & CI
Refs: [testing-and-ci.md](testing-and-ci.md)
### Phase 3.1: Integration Tests
- [ ] Step 3.1.1: CLI integration test for `--engine helionext` producing ICS
	- [ ] Sub-task: Add fixture run and assert exit code
	- [ ] Sub-task: Validate ICS file presence/basic structure
- [ ] Step 3.1.2: Generator-helper test path using HelioNext
	- [ ] Sub-task: Assert HelioNext events flow to ICS builder

### Phase 3.2: Parity & Edge
- [ ] Step 3.2.1: Diff-harness CI runs (short/week/medium) for majors
	- [ ] Sub-task: Wire jobs in CI
	- [ ] Sub-task: Store/report key metrics (counts, mismatches)
- [ ] Step 3.2.2: Edge tests for merge window, boundary clamping, retro/station flags, skip conditions
- [ ] Step 3.2.3: Config validation tests for engine flag and scope mapping

### Phase 3.3: Formatter & CLI Scope
- [ ] Step 3.3.1: Compact formatter smoke test with helionext events
- [ ] Step 3.3.2: CLI scope selection tests (major/minor/tertiary)

## Stage 4: Performance & Metrics
Refs: [performance-and-metrics.md](performance-and-metrics.md)
### Phase 4.1: Baselines
- [ ] Step 4.1.1: Record runtimes (legacy majors vs helionext majors; helionext all aspects) on 1-week scenario
	- [ ] Sub-task: Capture event counts and timings; store results

### Phase 4.2: Observability
- [ ] Step 4.2.1: Add optional metrics (ephem calls, cache hits, refine iterations, runtime) under timing_debug
- [ ] Step 4.2.2: Add benchmark script/CI job to catch regressions
	- [ ] Sub-task: Define pass/fail thresholds or alerts

## Stage 5: Ephemeris & Boundaries
Refs: [ephemeris-and-boundaries.md](ephemeris-and-boundaries.md)
### Phase 5.1: Ephemeris Handling
- [ ] Step 5.1.1: Validate required ephemeris presence with clear error
- [ ] Step 5.1.2: Document ephemeris selection/download/checksum guidance
	- [ ] Sub-task: Note default (de440s.bsp) and storage path

### Phase 5.2: Boundary Policy
- [ ] Step 5.2.1: Document clamp-to-window policy (no fabricated boundary hits) vs legacy
- [ ] Step 5.2.2: Gate any parity projection behind an explicit flag (if needed)
	- [ ] Sub-task: Describe implications for counts/time deltas

## Stage 6: Rollout & Naming
Refs: [rollout-and-risk.md](rollout-and-risk.md), [naming-and-scope.md](naming-and-scope.md), [aspect-coverage.md](aspect-coverage.md)
### Phase 6.1: Rollout Plan
- [ ] Step 6.1.1: Keep legacy default; document opt-in `--engine helionext`
- [ ] Step 6.1.2: Plan staged rollout and fallback to legacy
	- [ ] Sub-task: Define criteria to flip the default
	- [ ] Sub-task: Document rollback procedure

### Phase 6.2: Naming & Scope
- [ ] Step 6.2.1: Update user-facing naming to Astrological Event Calendar Generator in docs/help
- [ ] Step 6.2.2: Ensure CLI descriptions reflect ICS aspect interpretations as the primary output
	- [ ] Sub-task: Keep CLI flags stable; deprecate names only with warnings
