# Validation and Test Matrix

## Goals
- Prove correctness, determinism, and robustness across cycle types, bodies, ayanamsas, and spans.
- Detect regressions quickly via PR-time tests; catch slow drifts via nightly extended runs.
- Validate boundary/error handling so missing kernels and out-of-range requests fail predictably.

## Synthetic Fixtures (Deterministic)
- Ingress cases: crafted longitudes that cross sign boundaries at known times (with and without ayanamsa); include double-cross (fast Moon) to verify sub-stepping.
- Retro/station cases: velocity sign flips at precise times; station exactly on boundary; shallow velocity to test uncertainty reporting.
- Synodic cases: analytic linear-motion bodies with known phase crossings (0/90/180/270/360) and wrap across 360→0; multiple phase hits in tight windows.
- Ayanamsa variants: tropical, galactic_core placeholder, lahiri with drift; verify sign changes shift appropriately.
- Perihelion/aphelion analogs: simple radial distance parabola to validate extrema detection and uncertainty behavior.

## Real Fixtures (Ephemeris)
- Short: 7-day Moon-heavy window with multiple ingresses and one station; run tropical and galactic_core.
- Medium: 1-month Mercury/Venus retro including both stations and ingresses; run tropical and galactic_core; ensure retro interval bounds match expectations.
- Long: 1-year outer-planet focus (e.g., Saturn, Uranus, Neptune, Pluto) with ingresses and at least one outer synodic phase.
- Boundary: request outside kernel coverage to confirm hard fail with clear messaging; ensure no partial output.
- Optional: decade sanity to ensure chunking does not lose events at seams; validate dedupe across chunk overlaps.

## Tolerances (Per Class)
- Instants (short/medium): ≤2 seconds target; strict mode option at ≤1 second for synthetic.
- Instants (long outer): allowance up to 30 seconds if justified by solver limits; must record uncertainty.
- Intervals: start/end within above instant tolerances; if fallback used, attach uncertainty_seconds and flag in results.
- Distance extrema: tolerance in seconds plus distance delta threshold (to be set after first measurements).

### Per-Class Tolerance Table
| Class | Scope | Instant tolerance (s) | Interval tolerance (s) | Notes |
| --- | --- | --- | --- | --- |
| Fast (Moon) | short real + synthetic | 2 (strict 1) | 2 | Use strict in PR suite; require uncertainty if solver fallback triggers |
| Inner retro (Mercury/Venus) | medium real + synthetic | 5 | 5 | Allow station intervals to widen when probe widens; require uncertainty on widened bounds |
| Outer (Mars–Pluto) | long real + synthetic | 30 | 30 | Prefer 10–15s when solver converges; require uncertainty on fallback |
| Distance extrema | synthetic only (for now) | TBD seconds + distance delta | TBD | Set after first distance perf run; require uncertainty on shallow curvature |

- When tolerance is exceeded but event identity is correct, mark test as deviation instead of outright fail if policy allows (see below).
- Any result produced via fallback or widened probe must emit `uncertainty_seconds` and `convergence_status` in DTO and be asserted in tests.

## Assertions and Outputs
- Presence: expected events exist with correct event_type/body/sign/phase.
- Timing: within tolerance; record delta in report.
- Flags: retro/station booleans match expected; station_direction correct.
- Metadata: ayanamsa_mode matches input; uncertainty_seconds present when fallback used.
- Ordering: events sorted as specified; no duplicates beyond merge rules.

## Edge-Case Checks
- Station on ingress boundary (coincident timestamps) produces both events; merge policy honored.
- Retro interval overlapping ingress does not suppress either event; ordering stable.
- Double ingress per coarse step detected; sub-stepping prevents misses.
- 0/360 wrap in synodic separation handled; no false crossings.
- Missing kernel behavior: hard fail vs soft skip honored; skipped bodies logged.
- Chunk seams (when enabled): no lost/duplicated events beyond merge window dedupe.

## CI Strategy
- PR suite: synthetic fixtures (ingress, retro/station, synodic) and short real window (Moon) in tropical + galactic_core.
- Nightly/weekly: medium Mercury/Venus retro, long outer-year, boundary failure test, chunking seam test.
- Reporting: JSON with counts of matches/mismatches, max deltas, reason codes, skipped bodies, boundary_drops; human-readable summary for CI logs.
- Deviations: any approved deviation recorded with owner/expiry in report; failure if expired.

### Suite Commands
- PR: `python tools/run_cycle_validation_suites.py --suite pr`
- Nightly: `python tools/run_cycle_validation_suites.py --suite nightly`
- All (includes timing/slow): `python tools/run_cycle_validation_suites.py --suite all --extra-pytest-args "-m require_ephemeris"`
- Add `--no-quiet` to see full pytest output; pass additional filters via `--extra-pytest-args`.

Artifacts: store JSON results or junitxml under `output/ci/<suite>/` when integrating with CI (e.g., add `--extra-pytest-args "--junitxml output/ci/pr/results.xml"`).

### Deviation Approval Template
```
deviation:
	id: DEV-YYYYMMDD-<short-id>
	scenario: <synthetic|short|medium|long|extended>
	event: <ingress|synodic_phase|retro_interval|distance_extrema>
	body_or_pair: <Moon|Mercury|Jupiter|Jupiter-Sun|...>
	metric: <time_delta_seconds|interval_delta_seconds|distance_delta>
	observed_delta: <number>
	tolerance: <number>
	reason: <why deviation is acceptable>
	owner: <name>
	expires: <YYYY-MM-DD>
	mitigation: <plan or follow-up ticket>
```
- Store deviations alongside the related fixture results (e.g., `tests/fixtures/results` or `output/perf/latest`) and expire them; expired deviations must fail the suite.

## Tooling
- Harness to generate expected vs actual for synthetic cases; diff with tolerances.
- CLI scripts to run real fixtures with fixed seeds/config; output stored under tests/fixtures/results.
- Helpers to assert ayanamsa-adjusted sign at event times to catch drift.

## Open Items
- Set concrete distance tolerance for perihelion/aphelion once distance calculation path is defined.
- Decide whether to snapshot long-run outputs for regression diffing or rely on metrics + spot checks.
