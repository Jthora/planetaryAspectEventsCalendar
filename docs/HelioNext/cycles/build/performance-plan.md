# Cycle Engine Performance Plan

## Goals
- Achieve performant runs across short, medium, long, and extended spans while preserving correctness.
- Provide measurable budgets and instrumentation to detect regressions early.
- Keep memory bounded via cache policies and chunking for long spans.

## Benchmark Scenarios (Concrete)
- Short: 7-day Moon-heavy window with multiple ingresses and one station; ayanamsa=tropical and ayanamsa=galactic_core.
- Medium: 1-month inner-planet retro window (Mercury or Venus) including both stations and multiple ingresses; run both tropical and galactic_core.
- Long: 1-year outer-planet focus (Jupiter–Pluto) with ingresses and at least one synodic phase for an outer pair.
- Extended: decade and century sanity (coverage check and chunking stress); may limit outputs to key event types to control runtime.
- Stress: dense phase list (additional phase angles) on Moon+Mercury pair to test gating and refine load.

## Metrics to Collect
- Runtime per stage: scan/coarse, refine, retro/station detection, distance/extrema search, ICS formatting.
- Ephemeris calls; position cache hits/misses; separation cache hits/misses; cache size peak.
- Refine attempts, refine successes, refine failures, max iterations, average iterations.
- Merge counts (pre/post merge) for instants and intervals; boundary_drops count.
- Memory footprint estimates (optional sampling) and chunk count when chunking enabled.

## Targets and Budgets
- Short: ≤ legacy-equivalent/3 where applicable; absolute budget e.g., < N seconds on reference hardware (to be set after first run).
- Medium: ≤ legacy-equivalent/3; refine iterations average < 8; ephemeris_calls within 10% of plan.
- Long: ≤ legacy-equivalent/3; no stage exceeds 50% of total runtime; cache hit rate target > 70%.
- Extended: chunked processing completes without OOM; runtime scales roughly linearly with span when chunked; acceptable slowdown documented.
- Refine caps: MAX_SOLVER_ITERS enforced; failures < 0.1% of total events and always flagged with uncertainty.

## Optimization Priorities
- First: cache reuse across ingress/retro/synodic; minimize duplicate ephemeris calls in refine and retro probes.
- Second: adaptive step tuning by body/pair class with guard on max angle delta; tighten near candidate crossings.
- Third: chunk long spans with overlap to avoid misses; dedupe across seams with merge window.
- Fourth: optional vectorization/batching after correctness is stable; consider LRU caps if memory spikes.

## Instrumentation Plan
- Emit JSON per run: scenario id, config snapshot, metrics (runtime per stage, counts, iterations, cache stats, boundary_drops, skipped_bodies).
- Debug mode: list top-K slowest refinements (by iterations) and pairs with highest ephemeris call counts.
- Log cache stats and chunk count when chunking enabled; include overlap size.

## Measurement Protocol
- Run each benchmark twice: warm cache and cold cache if applicable to evaluate cache benefit.
- Fix hardware baseline and Python version; note ephemeris file sizes and location (disk vs memory) for reproducibility.
- Record ayanamsa mode because offsets can affect sign crossings frequency.

## Regression Policy
- Any increase >10% in runtime or ephemeris_calls vs last baseline requires investigation; >20% requires remediation or documented waiver.
- Refine failure rate > target triggers quality review; may adjust solver or step heuristics.

## Reporting
- Store benchmark outputs under a consistent path (e.g., output/perf/cycles/*.json).
- Summaries included in release notes when performance materially changes.

## Open Items
- Set absolute time budgets after first measured runs on reference hardware.
- Decide whether to expose a "performance mode" toggle that coarsens steps for very long spans.
