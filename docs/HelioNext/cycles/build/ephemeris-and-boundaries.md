# Ephemeris and Boundaries

## Required Kernels and Assets
- Baseline: de440s.bsp (planets + Moon). Bundled in repo root. Size 32 MB; SHA256 c1c7feeab882263fc493a9d5a5b2ddd71b54826cdf65d8d17a76126b260a49f2. Span: ~1849–2150 UTC (per NAIF DE440s release).
- Additional bodies: Chiron, Lunar Nodes, Lilith (Apogee), Priapus (Perigee) **not present** in bundled kernels; users must supply external SPKs or run with `--cycle-missing-body-policy skip` to proceed without them.
- Versioning: minimum tested kernel = DE440s (NAIF short span). Warn that other DE/LE files may shift timestamps slightly; advise re-running regressions if swapping kernels.
- Packaging: DE440s is user-visible in repo; for fresh downloads, point to NAIF generic kernels. Verify via SHA256 above; store in project root or configure `--ephemeris`.

### Kernel Coverage Table (current bundle)

| Body/Point | Kernel | Coverage (UTC) | Status | Notes |
| --- | --- | --- | --- | --- |
| Sun, Mercury, Venus, Earth-Moon Barycenter, Mars Barycenter, Jupiter Barycenter, Saturn Barycenter, Uranus Barycenter, Neptune Barycenter, Pluto Barycenter, Moon | de440s.bsp | ~1849-01-01 to ~2150-01-01 | Supported | Baseline kernel bundled in repo |
| Chiron | none | n/a | Missing | Requires external SPK; defaults to fail unless `--cycle-missing-body-policy skip` |
| Lunar Nodes | none | n/a | Missing | Not provided; either skip or inject kernel |
| Lilith (Apogee) | none | n/a | Missing | Not provided; either skip or inject kernel |
| Priapus (Perigee) | none | n/a | Missing | Not provided; either skip or inject kernel |

### Validation and Startup Checks
- At startup, list any bodies missing from the selected kernel; default policy is **fail fast** with an actionable message naming missing bodies and the active kernel path.
- If `--cycle-missing-body-policy skip` is set, log skipped bodies and continue; expose counts in metrics once wired.
- Provide a helper to print effective coverage (min/max) per body for the selected SPK; runtime now probes SPK segments to derive coverage (DE440s yields ~1849–2150 UTC).

## Coverage Limits and Enforcement
- Publish min/max supported UTC for each kernel/body; include table with earliest/latest date. (DE440s only, see table above.) Runtime enforces coverage via SPK probe before detection.
- Startup validation: fail fast with descriptive error naming the body and coverage bound when the requested window exceeds kernel range (default = fail). If a truncate mode is added later, document it and gate behind a flag.
- Chunking policy: do not attempt to stride beyond kernel coverage. If chunking is enabled for long spans, ensure chunks are clipped to kernel bounds and stop with an error if any chunk would exceed coverage.
- No projection beyond coverage: never synthesize boundary events outside kernel validity; drop refined hits that fall outside after clamping and increment boundary drop metrics.

## Time Scales, ΔT, and Precision
- Use ts.utc consistently for all computations; avoid manual timezone handling.
- Rely on Skyfield for leap-second and ΔT models; note that long-range accuracy depends on ΔT assumptions; document expected drift for century spans.
- Avoid naive datetime arithmetic inside solvers; convert to timescale objects near ephemeris calls.
- Precision policy: retain sub-second internally; serialize ISO with seconds by default unless configured otherwise.

## Ayanamsa Constants and Application
- Names supported: tropical (0), lahiri (drifting), galactic_core (placeholder until authoritative constants supplied).
- Constants: Lahiri base offset 23°51'11" at 2000-01-01 00:00 UTC, drift 50.29"/yr (~0.013969°/yr). Galactic_core currently 0° offset, 0 drift at 2000-01-01 until supplied.
- Drift model: offset = base_offset + drift_deg_per_year * years_since_epoch; years computed using 365.2425-day year; wrap360 after applying drift.
- Application order: compute ecliptic longitude -> subtract ayanamsa -> wrap -> use for sign/phase detection.
- Validation: galactic_core logs a one-time warning about placeholder constants; plan to replace when authoritative values arrive.
- Sample check: Lahiri offset on 2025-01-01 ≈ 23.8530555556 + 0.013969*(25.0) ≈ 24.2023°.

## Missing Data Policy
- Detect absent kernels at startup and list missing bodies; configuration flag controls hard-fail vs soft-skip.
- When soft-skip, log skipped bodies and expose counters; never partially compute with stale placeholders.
- If distance is unavailable (for perihelion/aphelion), skip those event types with explicit note.

## Boundary Behavior (Runtime)
- Clamp refine brackets to the requested window; drop events that refine outside after clamping.
- Record boundary drops in metrics (e.g., boundary_drops count) and optional debug logs.
- Ensure chunk seams (when chunking long spans) include a small overlap to avoid missed crossings; dedupe with merge window across seams.

## Numerical Safety and Wrapping
- Always wrap angles to 0–360 after ayanamsa; use unwrapping for interpolation across 0/360.
- Guard against catastrophic cancellation when computing small deltas over long spans; prefer signed_min_diff helpers.

## Validation Aids
- Provide a utility to print effective coverage per body and current ayanamsa offsets for a given date.
- Include a dry-run check that walks the requested span at coarse cadence to detect imminent boundary violations before full run.
