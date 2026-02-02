# Performance Thresholds and Waiver Template

## Alert Thresholds
- **Runtime change vs baseline:**
  - Warning: >10% increase on any scenario (short, medium, long, extended).
  - Failure: >20% increase unless waived.
- **Ephemeris calls:**
  - Warning: >10% increase over baseline for a scenario.
  - Failure: >20% increase unless waived.
- **Refine failures:**
  - Warning: failure rate >0.1% of events.
  - Failure: failure rate >0.5% or any unflagged (missing uncertainty/convergence_status).
- **Cache evictions:**
  - Warning: evictions exceed 5% of cap for any cache.
  - Investigate if evictions correlate with runtime/ephem spikes.

## Baseline and Comparison
- Store baseline JSON reports under `output/perf/baseline/<scenario>.json` (matching metrics schema).
- Compare new run vs baseline using percentage deltas per metric (runtime_seconds, ephem_calls, refine_failures, cache_evictions, chunk_count).
- Scenario mapping:
  - short: 7d Moon window
  - medium: 1m Mercury/Venus retro
  - long: 1y outer focus
  - extended: decade/century (chunking sanity)

## Comparison Script
- Location: `tools/compare_cycle_perf.py`
- Usage: `python tools/compare_cycle_perf.py output/perf/baseline output/perf/latest --waivers output/perf/latest`
- File naming: supports `<scenario>.json` or `metrics-<scenario>.json` in both baseline and candidate dirs.
- Thresholds enforced:
  - runtime_seconds, ephem_calls: warn >10%, fail >20% unless waived.
  - refine_failures: warn >0.1% of events, fail >0.5% of events.
  - cache_evictions: warn when >5% of provided cache cap if given; otherwise uses delta thresholds.
  - chunk_count: reported via delta (warn/fail thresholds) to flag chunking changes.
- Waivers: accepts JSON or YAML using the template below; ignored when expired; applied per scenario+metric and optional report names.
- Exit: non-zero when any metric is in fail status without a valid waiver.

## Capturing Baselines and Latest Runs
- Generate metrics with `python tools/run_cycle_perf_scenarios.py --cli "python DailyTransitAspectCalendarGenerator.py" --output-dir output/perf` (produces `metrics-<scenario>.json`).
- Normalize report names and copy to baseline or latest directories:
  - Baseline: `python tools/prepare_cycle_perf_baseline.py --update-baseline`
  - Latest: `python tools/prepare_cycle_perf_baseline.py --update-latest`
- Resulting files are named `<scenario>.json` (prefix stripped) under `output/perf/baseline` and/or `output/perf/latest` so the comparator can run without extra flags.

## Waiver Template
```
waiver:
  id: PERF-YYYYMMDD-<short-id>
  scenario: <short|medium|long|extended>
  metric: <runtime_seconds|ephem_calls|refine_failures|cache_evictions>
  baseline_report: output/perf/baseline/<scenario>.json
  new_report: output/perf/latest/<scenario>.json
  delta_pct: <number>
  owner: <name>
  expires: <YYYY-MM-DD>
  rationale: <why acceptable>
  mitigation: <plan to remediate or monitor>
```
- Waivers must expire; renewed waivers require a new ID and justification.
- Track waivers alongside reports (same folder) for auditability.
