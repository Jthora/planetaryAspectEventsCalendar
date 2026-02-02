# Span Derivation (Ingress and Synodic)

## Goals
- Provide DTEND-bearing spans so visualization tools can render continuous bands without client-side inference.
- Keep instant events intact; spans are additive and opt-in.

## Ingress Spans (per body)
- Input: ordered ingress instants for a body within the window (after any clamping applied elsewhere).
- Derivation:
	- Sort ingress events by start_time_utc.
	- For each ingress[i], span_start = ingress[i].start_time_utc, span_end = ingress[i+1].start_time_utc (or window_end for the last span).
	- If span_end < span_start (rare due to ordering), skip or clamp to window.
	- Clip to window: span_start = max(span_start, window_start); span_end = min(span_end, window_end).
- Emission:
	- event_type: `ingress_span` (distinct from `ingress`).
	- Summary suggestion: "{body} in {sign} (span)".
	- Categories: `Cycle`, `ingress_span`, body, sign.
	- DTEND set to span_end; all-day promotion if duration exceeds threshold rules used elsewhere.
- Metadata fields to include: body, start_sign (from ingress), end_sign (from next ingress if inside window), ayanamsa_mode, merge_window_seconds optional.

## Synodic Phase Spans (per pair)
- Input: ordered synodic phase instants for a pair and their phase angles.
- Angle ordering:
	- Normalize angles to sorted unique list (e.g., 0, 90, 180, 270). When wrapping, treat sequence cyclically.
- Derivation:
	- Sort events by start_time_utc; also map each to its phase_angle.
	- For each event[i], define next_phase = event[i+1] (or wrap to event[0] with +360 context if needed). Span covers phase_range [phase_i, phase_next) in time between event[i] and event[i+1].
	- Clip to window: span_start = max(event[i].start_time_utc, window_start); span_end = min(event[i+1].start_time_utc, window_end). If span_end <= span_start, drop.
	- Wrap handling: last event to first event crosses 360→0; still emit span if within window.
- Emission:
	- event_type: `synodic_phase_span`.
	- Summary suggestion: "{body1}/{body2} phase {phase_i:.0f}→{phase_next:.0f} span".
	- Categories: `Cycle`, `synodic_phase_span`, pair key (e.g., Mercury|Venus).
	- DTEND set; no all-day unless duration crosses threshold (rare but use same rule as other spans).
- Metadata fields to include: body1, body2, phase_start_deg, phase_end_deg, ayanamsa_mode.

## UID Namespace and Uniqueness
- Use a distinct namespace suffix, e.g., `helionext-cycles-span` to avoid collisions with instant UIDs.
- UID components: namespace, schema_version, span_type, bodies/pair, start_phase/end_phase (if applicable), span_start timestamp.
- Deterministic hashing to keep stability across regenerations given same inputs.

## Window and Clipping Rules
- Spans always clipped to requested window, even if source instants were padded/clamped for retro; no padding applies to span derivation.
- If no next ingress within window, span_end = window_end.
- If only one synodic event exists in window, skip span emission for that pair (insufficient boundary).

## Opt-In Behavior and Flags
- Flag: `--cycle-derive-spans` (bool) to enable span emission; default off.
- Optional sub-flags (future): limit to ingress spans or synodic spans; for now, emit both when enabled.
- When off: zero span events emitted; output identical to current behavior.

## Examples (conceptual)
- Ingress spans: Aries at 2026-01-05, Taurus at 2026-02-07 → span Aries 01-05 to 02-07; last span in window ends at window_end.
- Synodic spans: phases at 0° on 01-01, 90° on 01-10, 180° on 01-20, 270° on 01-30 → spans [0→90]: 01-01..01-10, [90→180]: 01-10..01-20, [180→270]: 01-20..01-30; wrap [270→0]: 01-30..(next 0° or window_end).

## Error Handling
- Missing or unsorted angles: normalize/dedupe; if fewer than 2 phases present, skip span emission for that pair.
- Overlapping instants at same timestamp: handle deterministically by input order or stable sort; spans with zero duration are skipped.
- Validation: ensure DTEND > DTSTART before emitting.
