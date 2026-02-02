# Retro Padding and Clamping

## Feature Definition
- New config fields
	- `retro_padding_days`: float/int, default 0; applies only to retro detection window (start minus padding, end plus padding).
	- `clamp_intervals`: bool, default false; when true, overlapping retro intervals are kept and clamped to the requested window.
- CLI flags
	- `--cycle-retro-padding-days <days>` (non-negative; validates as float).
	- `--cycle-clamp-intervals` (boolean switch).
- Applicability: retrograde intervals only. Ingress, synodic, stations (instants), perihelion/aphelion remain on the requested window.

## Algorithm (detection + filter)
1) Compute padded window: `retro_start = window_start - padding`, `retro_end = window_end + padding` (padding <=0 → no change).
2) Run retro detection in [retro_start, retro_end]; other detectors use [window_start, window_end]. Chunking still uses configured chunk spans with existing overlaps.
3) Filtering/clamping step per event:
	 - If `clamp_intervals` is false: drop any retro interval whose start < window_start or end > window_end; increment `boundary_drops` for each drop.
	 - If `clamp_intervals` is true: if interval is entirely outside, drop and increment `boundary_drops`. If it overlaps, keep and set start=max(start, window_start), end=min(end, window_end); increment `boundary_clamped`.
4) Non-retro events still pass through window filter (instants drop if outside; no clamping applied).

## Examples
- Example 1: padding=0, clamp=off, window Jan 1–Jan 31, retro Dec 20–Jan 15 → dropped, `boundary_drops += 1`.
- Example 2: padding=60, clamp=off, same window → detected (padding covers Dec 20), but dropped in filter, `boundary_drops += 1`.
- Example 3: padding=60, clamp=on, same window → detected and clamped to Jan 1–Jan 15, `boundary_clamped += 1`, `boundary_drops` unchanged.
- Example 4: interval Feb 5–Feb 20, window Jan 1–Jan 31, padding=30, clamp=on → detected (padding covers start?), actually start > window_end so dropped, `boundary_drops += 1`.

## Metrics Specification
- `boundary_drops` (int): increments when any event is discarded for being outside the requested window.
- `boundary_clamped` (int): increments when a retro interval overlaps and is clamped (only when clamp enabled).
- Optional logging (timing_debug): log padding value, clamp decisions with start/end before/after, and counts summary.
- Sample JSON snippet:
	```json
	{
		"boundary_drops": 1,
		"boundary_clamped": 2,
		"config_snapshot": {"retro_padding_days": 60, "clamp_intervals": true}
	}
	```

## Edge Cases and Rules
- Padding <= 0: treated as zero; no window expansion.
- Chunking: apply padded window per chunk; existing chunk overlap still used; dedupe unchanged.
- Extremely long intervals: clamp to window; duration may exceed all-day threshold—ensure DTEND is set, and all-day promotion rules stay intact.
- Missing bodies: respect existing skip/fail policy; padding does not change policy.
- Negative end after clamp: if start > end after clamp (e.g., interval entirely before window), treat as drop and increment `boundary_drops`.

## Validation and CLI UX
- Validate `--cycle-retro-padding-days` is numeric and >=0; error message: "cycle-retro-padding-days must be non-negative".
- Help text should note: applies to retro intervals only; use with `--cycle-clamp-intervals` to preserve cross-boundary retrogrades.
- Backward compatibility: defaults (0, false) must produce identical output and metrics as current behavior (guard with snapshot tests).
