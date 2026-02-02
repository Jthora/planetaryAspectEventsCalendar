# Step Tuning Plan (4.2.1.2.b)

Use the existing metrics buckets (per-body ephem/caches; per-pair sep cache) to tune step overrides.

Recommended scenarios
- **Moon short range (7 days):** Stress fast ingress and synodic sampling.
- **Inner month (Mercury/Venus, 30–45 days):** Capture stations/ingresses around retro windows.
- **Outer year (Jupiter–Pluto, 1 year):** Ensure outer pairs’ synodic scans stay efficient.

How to run
- Preferred: `python tools/run_cycle_perf_scenarios.py --cli ./your_cli_entry` (writes metrics to `output/perf/metrics-*.json` and summary txt).
- Manual flags if needed:
  - `--cycle-engine helionext-cycles`
  - `--cycle-types ingress,synodic_phase`
  - `--cycle-phase-angles 0,90,180,270`
  - `--cycle-metrics-path output/perf/metrics-<name>.json`
  - `--cycle-chunk-span-days 180` (default; set 0 to disable chunking for A/B)
  - `--planets <list>` and date ranges per scenario above.

What to inspect
- `ephem_calls_by_body` / `pos_cache_*_by_body`: spot bodies needing finer steps vs over-sampling.
- `sep_cache_*_by_pair`: highlight synodic pairs dominating misses.
- Compare counts with runtime to identify candidates for overrides (`ingress_step_overrides`, `synodic_pair_step_overrides`).

Adjustment loop
- Lower step minutes for bodies/pairs with high miss/ephem ratios and tight windows; raise where counts are low and tolerance is generous.
- Re-run scenarios after overrides; keep chunking on/off runs to ensure seam logic unaffected.

Exit criteria
- Per-class overrides chosen and recorded in config (4.2.1.2.b), with before/after metrics snapshots saved in `output/perf/`.
