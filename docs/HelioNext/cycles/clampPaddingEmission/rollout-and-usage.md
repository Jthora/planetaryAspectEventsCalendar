# Rollout and Usage

## CLI Examples
- Monthly with padding/clamp (cycles-only example):
	```bash
	python DailyTransitAspectCalendarGenerator.py \
		--cycle-engine helionext-cycles \
		--cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion \
		--cycle-phase-angles 0,90,180,270 \
		--cycle-retro-padding-days 60 \
		--cycle-clamp-intervals \
		--skip-aspect-detection --no-aspects \
		--start 2026-01-01 --end 2026-01-31 \
		--output output/cycles_monthly_2026/cycles_2026-01.ics \
		--cycle-metrics-path output/cycles_monthly_2026/metrics/cycle-metrics-2026-01.json
	```
- Yearly with spans enabled:
	```bash
	python DailyTransitAspectCalendarGenerator.py \
		--cycle-engine helionext-cycles \
		--cycle-types ingress,synodic_phase,retro_interval,station,perihelion_aphelion \
		--cycle-phase-angles 0,90,180,270 \
		--cycle-retro-padding-days 30 \
		--cycle-clamp-intervals \
		--cycle-derive-spans \
		--start 2026-01-01 --end 2026-12-31 \
		--output output/cycles_yearly_2026.ics \
		--cycle-metrics-path output/cycles_yearly_2026_metrics.json
	```

## Guidance by Use Case
- Monthly exports: recommend padding 60–90 days for outer-planet retro continuity; enable clamping to keep spans inside the month. If runtime is high, lower padding to 45 days and evaluate gaps.
- Yearly exports: small padding (0–30 days) typically sufficient; clamping avoids losing cross-year retro starts; spans optional for visualization bands.
- Visualization styling: use categories `ingress_span`, `synodic_phase_span`, and `retro_interval` for spans; instants remain for markers (ingress, synodic_phase, station, perihelion/aphelion).

## Risks and Mitigations
- Over-padding → runtime increase: start modest; document runtime deltas in metrics; consider body-based padding if needed later.
- Under-padding → missed cross-boundary intervals: observe `boundary_drops`/`boundary_clamped` metrics and adjust padding.
- Span density/overlap: visualization should lane/stack; spans are opt-in and can be limited to ingress only if needed.
- Metrics drift: ensure downstream parsers tolerate added keys; keep defaults off to avoid surprise.

## CI and Verification
- Add a regression that runs without new flags and asserts identical ICS/metrics (byte-for-byte) to baseline.
- Add a targeted run with padding+clamp to verify `boundary_clamped > 0` in a crafted fixture (retro crossing boundary).
- Optional: add a spans-enabled run that asserts presence of `ingress_span` and `synodic_phase_span` categories.

## Communication Notes
- Release notes (add to changelog/README):
	- New opt-in flags: `--cycle-retro-padding-days`, `--cycle-clamp-intervals`, `--cycle-derive-spans` (defaults off, backward compatible).
	- Metrics now include `boundary_clamped` alongside `boundary_drops` and config snapshot fields for padding/clamp/spans.
	- Span events use UID namespace `helionext-cycles-span` and categories `ingress_span`, `synodic_phase_span`; instants unchanged.
- Docs: README updated with padding/clamp/spans example and guidance; link metrics expectations and thresholds.
