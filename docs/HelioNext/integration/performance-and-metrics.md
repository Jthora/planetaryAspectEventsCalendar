# Performance and Metrics

- Capture baseline runtimes: legacy majors vs helionext majors, and helionext all aspects, on 1-week scenario; record counts and timings.
- Add optional metrics collection (ephemeris calls, cache hit rates, refine iterations, runtime) when timing_debug is enabled.
- Consider cache reuse across runs for identical ephemeris/date ranges.
- Tune step heuristics per pair if minor/tertiary scopes regress performance.
- Add a simple benchmark script/CI job to detect regressions on short/week scenarios.
