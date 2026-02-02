# HelioNext Cycle Engine Guide (opt-in)

Use this guide to generate ICS files that include HelioNext cycle events (ingress, synodic phases, retro/stations, distance extrema) alongside the existing aspect outputs.

## Prerequisites
- Python 3.10+ and project deps: `pip install -r requirements.txt`
- Ephemeris: `de440s.bsp` in repo root (bundled). For bodies not in DE440s (e.g., Chiron, Lilith), either add kernels or run with `--cycle-missing-body-policy skip`.
- Time window within kernel coverage (~1849–2150 UTC for DE440s).

## Quick commands

Full-year cycles + aspects:
```bash
python DailyTransitAspectCalendarGenerator.py \
  --cycle-engine helionext-cycles \
  --cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion \
  --cycle-phase-angles 0,90,180,270 \
  --start 2026-01-01 --end 2026-12-31 \
  --output output/cycles_2026.ics \
  --cycle-metrics-path output/ci/cycle-metrics-2026.json
```

Cycles-only (skip aspect computation/serialization):
```bash
python DailyTransitAspectCalendarGenerator.py \
  --cycle-engine helionext-cycles \
  --cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion \
  --cycle-phase-angles 0,90,180,270 \
  --skip-aspect-detection --no-aspects \
  --start 2026-01-01 --end 2026-12-31 \
  --output output/cycles_only_2026.ics \
  --cycle-metrics-path output/ci/cycle-metrics-2026.json
```
Notes: leave `--daily-summary` off (it uses aspect lists); compact mode disables cycles, so run cycles-only in standard mode. Aspects are neither computed nor emitted.

Padding/clamp + spans (yearly example):
```bash
python DailyTransitAspectCalendarGenerator.py \
  --cycle-engine helionext-cycles \
  --cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion \
  --cycle-phase-angles 0,90,180,270 \
  --cycle-retro-padding-days 30 \
  --cycle-clamp-intervals \
  --cycle-derive-spans \
  --skip-aspect-detection --no-aspects \
  --start 2026-01-01 --end 2026-12-31 \
  --output output/cycles_only_2026_spans.ics \
  --cycle-metrics-path output/ci/cycle-metrics-2026-spans.json
```
Guidance: use moderate padding (15–45 days) for yearly exports; clamping keeps retro intervals within the requested window while counting `boundary_clamped`/`boundary_drops`; spans add `ingress_span` and `synodic_phase_span` bands with DTEND and span UID namespace. Defaults keep these features off for backward compatibility.

Ingress-only sanity slice:
```bash
python DailyTransitAspectCalendarGenerator.py \
  --cycle-engine helionext-cycles \
  --cycle-types ingress \
  --cycle-ingress-signs Aries,Libra \
  --start 2026-01-01 --end 2026-01-05 \
  --output output/ingress_sample.ics \
  --cycle-metrics-path output/ci/ingress-sample.json
```

## Important flags
- `--cycle-engine helionext-cycles` (enable) | `--cycle-engine off` (disable/rollback; default)
- `--cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion` (comma list)
- `--cycle-phase-angles 0,90,180,270` (degrees 0–360)
- `--cycle-ingress-signs Aries,Libra` (optional subset)
- `--cycle-retro-probe-hours <hours>` (bounded; defaults per body if omitted)
- `--cycle-metrics-path <path>` (write JSON metrics: runtime, refine stats, cache stats, skipped_bodies, boundary_drops, config_snapshot)
- `--cycle-missing-body-policy fail|skip` (default fail)
- `--chunk-span-days <days>` (set 0 or <0 to disable chunking; otherwise chunks with overlap)

## Behavior notes
- Aspect outputs remain unchanged when cycles are on; compact mode auto-disables cycles.
- Boundary enforcement: events outside the requested window (or chunk seams) are dropped and counted in `boundary_drops` metrics.
- ICS: cycle categories carry distinct UIDs and do not collide with aspect UIDs.

## Monitoring & thresholds (summary)
- Warn if `refine_failures` >0.5% of cycle events; investigate >1.0%.
- Warn if `boundary_drops` >0; investigate immediately if >5 per run.
- Warn if `skipped_bodies` non-empty; add kernels or document skip policy.
- Store metrics JSON and perf comparator outputs under `output/ci/<suite>/` for review.

For deeper design, validation, and rollout guidance, see docs/HelioNext/cycles/build (especially rollout-and-migration.md and validation-and-test-matrix.md).
