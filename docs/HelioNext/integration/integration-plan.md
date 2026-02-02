# HelioNext End-to-End Integration Plan

## Purpose
Document how to wire the HelioNext detection engine into the full calendar/ICS pipeline while preserving backward compatibility and allowing opt-in rollout.

## Scope
- Entry points: DailyTransitAspectCalendarGenerator.py, tools/generate_yearly_calendars.py, related helper modules.
- Config/CLI: engine selection, validation, and defaults.
- Detection: swap direct legacy calls for engine_factory selection.
- Outputs: ICS generation (builder, titles, interpretations), compact formatter.
- Tests, docs, and rollout toggle.

## Work Plan
- Engine selection
  - Add `--engine {legacy,helionext}` (default legacy) to main CLIs.
  - Thread engine into config creation and use `engine_factory.get_detection_engine`.
  - Optional: env var override for batch jobs.
- Config & validation
  - Allow `helionext` in validation; fail fast on bad values.
  - Require ephemeris path; document de440s.bsp recommendation.
- Pipeline hookup
  - Replace direct legacy detect calls with engine_factory in generator helpers so AspectEvents feed ICS builder unchanged.
  - Confirm downstream consumers do not assume legacy-only fields.
- Testing
  - CLI integration tests exercising `--engine helionext` to produce ICS without errors.
  - Generator helper tests using helionext path.
  - Reuse diff-harness tests for flag/time/delta tolerance checks.
- Performance sanity
  - Week benchmark: helionext (majors) vs legacy (majors) after wiring; record runtimes.
- Docs & UX
  - Update README and docs/HelioNext/build to show `--engine helionext`, ephemeris guidance, and known boundary behavior.
- Rollout toggle
  - Keep legacy default; allow opting into HelioNext per run.
  - Optionally add global config flag for batch jobs; document fallback to legacy.

## Risks & Mitigations
- Behavior drift vs legacy: use diff harness (short/week/medium) after integration.
- Boundary handling differences: document clamping policy; offer flag only if parity is required.
- Performance surprises: capture runtimes in week benchmark and track regressions.

## Acceptance
- CLIs accept `--engine helionext` and succeed end-to-end.
- ICS output shape unchanged; interpretations/titles still generated.
- Tests cover helionext path; diff harness shows expected parity on majors.
- Docs updated; legacy remains default with opt-in HelioNext.
