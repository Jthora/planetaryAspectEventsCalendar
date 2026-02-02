# Cycle Engine Architecture and Scope

## Purpose and Objectives
- Deliver cycle-focused events and intervals (ingress, synodic phases, retrograde windows, station instants, perihelion/aphelion, Nodes/Apogee/Perigee, Sun/Moon) alongside existing aspect outputs without breaking defaults or user workflows.
- Preserve determinism, ordering, and toggle-ability so users can opt in/out and compare against legacy aspect pipelines without schema drift.
- Guarantee success criteria: correct timestamps within explicit tolerances, correct ayanamsa application before sign logic, stable ICS outputs (folding, ASCII), bounded runtime on long spans, and clear failure modes when inputs exceed ephemeris limits.
- Keep scope crisp: cycle engine extends capabilities rather than replacing existing aspect DTOs; any shared logic must be consciously reused to avoid divergence.

## Explicit Scope
- Bodies in scope: Mercury, Venus, Earth, Mars, Chiron, Jupiter, Saturn, Uranus, Neptune, Pluto; Lunar Nodes; Lunar Apogee (Lilith); Lunar Perigee (Priapus); Sun; Moon. Capture kernel requirements and any exclusions per body.
- Cycle types in scope:
- Missing-body policy: default fail-fast when requested bodies lack kernels (e.g., Chiron, Nodes, Lilith, Priapus). Optional skip mode via CLI (`--cycle-missing-body-policy skip`) to proceed without them.
	- Sign ingress (tropical and ayanamsa-adjusted) with exact boundary timestamps.
	- Synodic phases with configurable phase list (default 0/90/180/270/360) for each ordered body pair.
	- Retrograde intervals with start/end instants and optional station instants at the boundaries or interior.
	- Stations as instants (forward-to-retro, retro-to-forward) with optional strength/quality metric.
	- Perihelion/aphelion markers where distance data is available; skip cleanly otherwise.
	- Optional lunar-point events (Nodes, Lilith, Priapus) are **off by default** for v1 due to missing kernels; enable only when external kernels are supplied.
- Outputs: ICS events (timed or all-day per policy), optional compact lines, JSON DTOs for downstream builders.
- Modes: support ayanamsa choices (tropical default, lahiri, galactic_core placeholder) and interpretation modes where relevant for summaries; no change to house calculations.

## Boundaries and Constraints
- Ephemeris bounds: detect min/max coverage; clamp refinement windows; fail fast when user ranges exceed coverage; no projection or fabricated boundary events.
- Time scales: UTC via ts.utc; avoid naive datetime math for exact crossings; respect leap seconds via Skyfield.
- Determinism: stable ordering (time, event_type, body tuple), stable merge/dedupe rules; no randomness or dependency on dict iteration order.
- Compatibility: aspect DTOs and ICS formatting must remain unchanged; new fields gated to cycle DTOs only; default behavior keeps cycles off unless explicitly requested.
- Memory and runtime: cache reuse is allowed but must be bounded; chunk long spans to avoid unbounded growth.

## Success Criteria (Concrete)
- Accuracy: ingress and station instants within defined tolerances (short/medium ≤2s; long outer cases documented), retro intervals with start/end within tolerance and uncertainty noted when fallback is used.
- Coverage: all enabled cycle types emit for all supported bodies within ephemeris coverage; missing bodies reported clearly.
- Observability: metrics for ephemeris_calls, cache hits, refine iterations, boundary drops, skipped bodies; logs capture active engine/config.
- Resilience: predictable failure modes (missing kernel, out-of-range request, unsupported ayanamsa) with actionable error text; no partial silent skips.

## Non-Goals (Reiterated)
- No introduction of new ephemeris sources in the first iteration; only reuse existing kernels shipped/required today.
- No change to house systems or aspect orb policies.
- No schema changes to aspect DTOs or ICS produced by the aspect pipeline; cycles are additive and isolated.
- No user-facing guidance authoring for cycles in this iteration (titles allowed; guidance text optional/absent).
- No fallback approximations for Nodes/Lilith/Priapus in v1; if kernels are absent and skip policy is disabled, runs will fail fast.

## Ayanamsa Policy (Detailed)
- Default tropical offset = 0.0; support named offsets (galactic_core placeholder, lahiri with drift) applied before sign detection and phase evaluation.
- Drift constants must be sourced and documented; placeholder values flagged until authoritative numbers provided.
- Ayanamsa offsets logged when non-tropical; ICS summaries may include ayanamsa label when configured.

## Kernel and Coverage Expectations
- Enumerate kernel names required per body/point; for any missing (e.g., Chiron or Nodes) define whether to hard-fail or soft-skip with warning.
- Define maximum supported span for performance baselines (e.g., 1900–2100 if kernels allow) and state that outside requests are rejected.

## Risks and Mitigations (Expanded)
- Missing kernels for minor bodies/points: startup validation; per-body skip list; user-facing guidance to install kernels.
- Performance on decade/century spans: chunk processing, adjustable step heuristics, cache size caps, optional sparse outputs for long phases.
- Schema creep: introduce DTO version; gate optional fields; keep a changelog of additions.
- Edge correctness: codify handling for wrap/sign boundaries, simultaneous station+ingress, and double ingress in one coarse step; add tests in the matrix.
- User confusion on ayanamsa: document defaults, log active ayanamsa, and provide CLI validation on allowed names.

## Determinism and Ordering
- Sort by UTC time, then event_type, then (body) or (body1, body2) tuple for reproducible outputs.
- Merge/dedupe policy: configurable merge window per event_type (default small for instants); document precedence rules (prefer lowest uncertainty then earliest time).
- No projection beyond requested window; refinement brackets clamped to range.

## Deliverables Checklist
- Engine code path (detector) plus factory hook with toggle.
- DTO schema documented with required/optional fields and version tag.
- ICS mapping rules per cycle type; sample summaries and descriptions.
- Validation fixtures and CI wiring per test matrix.
- Performance baselines and benchmark scripts with JSON outputs.
- Rollout plan and user-facing toggle documentation.

## Open Questions to Resolve
- Should perihelion/aphelion be enabled by default if kernels allow? What to do when distance is missing?
- Do we expose uncertainty_seconds in ICS descriptions by default or only when fallback convergence occurs?
- Are Nodes/Lilith/Priapus computed via existing kernels or approximated? If approximated, document method and precision.
- Do we need house or location context for any cycle summaries? Current stance: no; confirm.

## Acceptance Gates
- Docs in this folder accepted; DTO and ICS contracts frozen for MVP; toggle behavior validated; ephemeris validation implemented; baseline tests passing with defined tolerances; performance within agreed budgets.
