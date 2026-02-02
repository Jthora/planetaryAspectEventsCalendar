# Clamp + Padding + Span Emission Overview

## Problem Statement (with examples)
- Monthly ICS runs drop retro intervals that start before the window (e.g., retro begins 2025-12-20, ends 2026-01-15; Jan window loses it). Users of cycle-only monthly exports see gaps in retro bands.
- Yearly runs still drop intervals that began in the prior year. Visualization systems expecting continuous color bands show missing segments at year boundaries.
- Ingress and synodic phases are instants, so visualization consumers must infer spans (sign stays; phase arcs) on their own, increasing client complexity and duplication risk.

## Objectives
- Add optional retro padding + clamping so cross-boundary retro intervals are retained and clipped to the requested window without scanning huge ranges.
- Add optional derived spans (ingress stays, synodic phase arcs) to produce DTEND-bearing events for visualization while keeping instant events intact.
- Preserve default behavior: no change when flags are not provided; output remains byte-for-byte identical.

## Definitions
- Padding: extend only the retro detection window by N days before start and after end; other detectors remain on the requested window.
- Clamping: if an interval overlaps the requested window, keep it and set start=max(ev.start, window_start) and end=min(ev.end, window_end).
- Derived spans: additional ICS events (e.g., `ingress_span`, `synodic_phase_span`) built from detected instants to represent continuous stays/arcs.

## Success Criteria
- With padding=60d and clamping on, a retro interval spanning Dec→Jan is present in the January ICS as a clamped interval; `boundary_clamped` increments, `boundary_drops` unchanged for in-scope intervals.
- Defaults off produce the same ICS/metrics as before (snapshot-stable regression test).
- Derived spans emit correct DTEND and UID namespace, and do not remove or mutate original instants.
- Runtime overhead is bounded: padding applies only to retro detection; span derivation is linear in detected events.

## Non-Goals
- No automatic enablement; users must opt in via flags.
- No new ephemeris data or body support; this is window handling and post-processing only.
- No change to compact-mode policy (compact still disables cycles).

## Risks and Mitigations
- Runtime cost if padding is too large: mitigate with modest defaults (60–90d) and document per-body expectations.
- Overlap density in visualization: offer categories for spans so consumers can lane/stack; spans are optional.
- UID churn: use distinct namespace for derived spans; keep existing cycle UIDs untouched.
- Metrics confusion: add `boundary_clamped` and keep `boundary_drops`; document semantics and sample JSON.

## Stakeholders and Consumers
- CLI users generating monthly/yearly ICS for downstream visualization (spectrograph-like bands).
- CI/perf reviewers ensuring defaults remain stable and runtimes acceptable.
- Visualization pipeline developers needing categories and spans without client-side inference.

## Acceptance Checklist
- Flags documented and validated; defaults off.
- Tests cover drop vs clamp vs keep; spans wrap 360→0 and ingress contiguity.
- README/HELIONEXT guides updated with examples (monthly with padding/clamp; yearly with spans).
- Metrics schema additions are noted in rollout docs and validated via tests.
