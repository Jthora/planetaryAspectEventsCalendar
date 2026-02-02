# Testing Plan

## Padding and Clamping Cases
- Overlap keep/clamp: window Jan 1–Jan 31; retro Dec 20–Jan 15; padding=60; clamp=on → interval kept and clamped to Jan 1–Jan 15; `boundary_clamped == 1`, `boundary_drops == 0`.
- Overlap drop when clamp off: same data; clamp=off → interval dropped; `boundary_drops == 1`, `boundary_clamped == 0`.
- Outside window: retro Feb 5–Feb 20; window Jan 1–Jan 31; padding=30; clamp=on → dropped; `boundary_drops == 1`.
- Padding zero: padding=0 behaves like current (no detection outside window); assert metrics unchanged vs baseline.
- Chunked run: chunk_span_days small (e.g., 10d), interval spanning chunk boundary; ensure single clamped interval emitted, no duplicates.
- Metrics serialization: JSON contains both `boundary_drops` and `boundary_clamped` with correct counts; config_snapshot includes padding/clamp flags.

## Span Derivation Cases
- Ingress spans contiguity: ingress at Jan 5 (Aries), Feb 7 (Taurus), window Jan 1–Feb 28 → spans: Aries 01-05..02-07, Taurus 02-07..02-28; DTEND set; no gaps.
- Synodic spans wrap: phases 0° @ Jan 1, 90° @ Jan 10, 180° @ Jan 20, 270° @ Jan 30, next 0° @ Feb 15 → spans between consecutive events, including wrap 270→0 (Jan 30..Feb 15); DTEND set; window clip if needed.
- Single phase event: only one phase in window → no span emitted; ensure no crash.
- UID uniqueness: spans have distinct namespace; ensure no collision with instant UIDs in mixed calendar.
- Category/content: spans carry expected categories and metadata fields (phase_start/end, body or pair).

## CLI and Validation
- Parse new flags: positive padding accepted; negative rejected with clear message; clamp/spans flags set booleans.
- Compact mode: new flags are ignored or warn when mode=compact (cycles already off); no crash.

## Backward Compatibility
- Snapshot test: run a known scenario without new flags; assert ICS and metrics match previous baseline byte-for-byte.
- Metrics schema: ensure existing keys remain; new keys optional and zero when features off.

## Performance/Runtime Checks
- Padding overhead sanity: run with padding=90 on monthly window; ensure runtime within expected multiple vs baseline (document threshold).
- Span derivation overhead: assert negligible (<5% wall time change) for a mid-size scenario.

## Fixtures and Tools
- Use deterministic fixtures (small time windows) to avoid ephemeris variability.
- Mock detection outputs for unit tests on clamping and spans to avoid slow ephemeris calls.
