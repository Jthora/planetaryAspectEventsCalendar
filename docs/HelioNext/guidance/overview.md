# Guidance Expansion Overview

## Objectives
- Deliver non-empty, mode-appropriate interpretations for every aspect emitted (major, minor, tertiary) across all four modes (standard, business, space_force, raves).
- Normalize aspect naming/aliasing so guidance lookups are consistent across engines (legacy, HelioNext) and catalogs.
- Provide a maintainable authoring and testing process to keep coverage current as catalogs evolve.

## Deliverables
- Mode style guides defining tone, severity usage, and headline/impact/action patterns.
- Aspect coverage matrix showing which aspects have custom copy per mode vs fallback.
- Alias map tying canonical names to accepted variants.
- Authoring checklist and content plan for prioritizing aspect writeups.
- Testing plan (unit + integration) to prevent blank or degraded guidance.

## Scope
- Aspects: majors plus the extended minor/tertiary set in the unified catalog (see aspect-coverage-matrix).
- Modes: standard, business, space_force, raves.
- Outputs: ICS aspect event descriptions; compact/standard modes both rely on the same interpretation layer.

## Success Criteria
- Every emitted aspect in any mode renders a non-empty headline/impact/action (or watch) and a summary; no blank interpretation sections.
- Alias names resolve to canonical guidance without duplication or mismatch.
- Tests cover representative majors/minors/tertiaries per mode and guard against regressions.

## Workflow
1) Define tone/voice and severity framing per mode (mode-style-guides).
2) Finalize alias mapping and unified catalog (alias-mapping, aspect-coverage-matrix).
3) Prioritize aspects (content-plan) and author guidance using the checklist.
4) Track completion in the coverage matrix; add tests per testing-plan.
5) Run integration/ICS smoke to verify no blanks in output.

## Near-term focus
- Waves 1–4 authored and validated; maintain tone alignment for majors via spot checks.
- Final ICS reference: [output/final_helionext_complete.ics](output/final_helionext_complete.ics) (helionext, complete scope, orb 1.5°).
- Keep alias-mapping synced to aspect_catalog canon; matrix remains all `C`.
- If tone drift is found, patch guidance and re-run a targeted ICS smoke as needed.

## Quick links
- Mode tone/structure: mode-style-guides
- Priorities/batching: content-plan
- Coverage tracking: aspect-coverage-matrix
- Authoring steps: authoring-checklist
- Validation: testing-plan
