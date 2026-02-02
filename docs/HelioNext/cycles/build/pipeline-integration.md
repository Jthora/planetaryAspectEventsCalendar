# Pipeline Integration

## Engine Factory
- Add cycle engine entry (name TBD) to engine_factory alongside legacy/helionext; deterministic lookup; clear error on unknown name.
- Ensure cycle engine is isolated from aspect engine selection; enabling cycles does not alter aspect path unless explicitly requested.
- Provide construction helper that wires config -> cycle detector -> DTO list; allows chunking wrapper if enabled.

## Config and Wiring
- Extend config object with cycle fields (cycle_engine, cycle_types, phase_angles, ingress_signs, retro_probe_hours, merge_window, ayanamsa, chunk_span_days, missing_body_policy, timing_debug/metrics) without altering existing aspect fields.
- Validation layer to run before engine selection; fail fast on invalid values.

## Data Flow
- Aspect pipeline remains unchanged; cycle pipeline produces a separate list of CycleEvents.
- Downstream: either emit distinct ICS files (cycle vs aspect) or combine with clear tagging; document chosen strategy.
- Avoid shared mutable state: caches scoped per run; metrics separate for aspects vs cycles.

## ICS/Formatter Touchpoints
- Add cycle-aware branch in ICS builder to render instants and intervals using cycle templates; preserve folding/ASCII rules.
- If combining outputs, ensure sort order (time, type) is enforced before writing ICS.
- Decide on compact formatter handling: either extend to cycles with new templates or explicitly skip cycles with a log message.

## Guidance/Titles
- If no guidance content exists for cycles, set expectation in summaries/descriptions (e.g., factual only). If titles needed, define minimal deterministic patterns per event_type.
- Ensure absence of guidance does not trigger empty fields; supply neutral text.

## Merge and Ordering Policies
- Maintain separate merge windows for cycles vs aspects unless explicitly unified; document defaults.
- Dedupe across chunk seams when chunking long spans; ensure seam overlap and merge post-concat.

## Downstream Contracts
- ICS consumers: confirm they tolerate new categories/summary shapes; document any required fields.
- JSON/API consumers: publish DTO schema; ensure unknown fields do not break consumers.
- Logging/metrics consumers: namespaced metrics (cycle_*) to avoid collisions with aspect metrics.

## Testing Hooks
- Provide integration tests that run the full pipeline with cycle engine on: config -> engine_factory -> detection -> ICS builder -> file output.
- Add smoke tests to ensure aspect-only runs remain unchanged when cycles disabled.

## Deployment Considerations
- Ensure CLI tools accept new flags and pass through to engine_factory; batch scripts updated.
- Backward compatibility: older configs without cycle fields should still parse (fields optional with defaults).

## Observability
- Log active engines (aspect and cycle) and key config; emit metrics files when requested.
- Optionally emit a manifest per run listing output files (aspect ICS, cycle ICS) and counts.
