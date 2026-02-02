# Pipeline Integration

## End-to-End Flow (standard mode)
1) CLI parse: new flags read (`--cycle-retro-padding-days`, `--cycle-clamp-intervals`, `--cycle-derive-spans`). Defaults: 0 / false / false.
2) Config build: CycleConfig gains `retro_padding_days`, `clamp_intervals`, `derive_spans` fields; stored in config_snapshot for metrics.
3) Detection:
	- Aspect path unchanged; can be skipped with existing flags.
	- Cycle path: ingress/synodic/station/perihelion/aphelion run on requested window. Retro detection runs on padded window if padding>0.
4) Filtering:
	- All events pass through window filter. Instants outside are dropped (boundary_drops increment). Retro intervals: drop or clamp based on `clamp_intervals`.
	- Metrics updated (`boundary_drops`, `boundary_clamped`).
5) Span derivation (optional): if `derive_spans` true, build derived spans from detected (and potentially clamped) events; append to cycle event list.
6) ICS build: convert cycles (and spans if present) to ICS with stable UIDs; write metrics if path provided.

## Hook Points and Ownership
- Retro padding: applied inside retro detector caller (engine) before iterating chunks; only affects retro.
- Clamp/filter: implemented in the shared window filter to keep metrics consistent.
- Span derivation: post-filter, pre-ICS builder; lives in cycle ICS pipeline to avoid touching aspect path.

## Config and CLI Table
- `retro_padding_days` (float>=0, default 0) ← `--cycle-retro-padding-days`
- `clamp_intervals` (bool, default false) ← `--cycle-clamp-intervals`
- `derive_spans` (bool, default false) ← `--cycle-derive-spans`
- Validation: non-negative padding; spans flag only affects cycles; compact mode still forces `cycle_engine=off`.

## Performance Expectations
- Padding cost: retro detection window expands by 2*padding; runtime grows roughly linearly with added days. Recommend starting at 60–90d for monthly runs; 0–30d for yearly.
- Span derivation: O(n) in cycle events per body/pair; negligible vs detection; memory minimal.
- Metrics write unaffected; log volume unchanged unless timing_debug adds clamp logs.

## Compatibility and Stability
- Defaults preserve current outputs: no padding, no clamp, no spans. Add snapshot test to assert byte-for-byte ICS and metrics match prior behavior when flags absent.
- UIDs: existing cycle UIDs unchanged; spans use distinct namespace to avoid collisions.
- Compact mode: still disables cycles; new flags should warn/no-op under compact.

## Data Flow Considerations
- Chunking: padding applied per chunk; overlap remains 12h; dedupe unchanged. Ensure clamping happens after dedupe so spans aren’t duplicated.
- Metrics: config_snapshot should include new fields; ensure JSON schema remains valid for downstream parsers.
- Error handling: padding validation errors should exit early; spans should skip emission on malformed inputs without crashing.
