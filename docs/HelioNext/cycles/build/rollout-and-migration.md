# Rollout and Migration

## Goals
- Introduce cycle engine safely with opt-in controls, measurable quality gates, and easy rollback.
- Keep aspect users unaffected unless they opt in; maintain trust via transparent metrics and documentation.

## Phases (Detailed)
- Phase 1: Internal opt-in only. Run synthetic + short real fixtures; gather perf and correctness metrics; cycles disabled by default.
- Phase 2: Limited external opt-in. Document flags; encourage early adopters; monitor validation reports and error logs (missing kernels, boundary drops, fallback events).
- Phase 3: Candidate default. Criteria met; turn cycle engine on by default for supported commands, but keep off switch; broaden validation (medium/long runs) in CI and release gating.
- Phase 4: Stabilization and optional deprecation of off mode once usage and reliability are proven; keep off switch for at least one release window before removal.

## Promotion Criteria
- Validation: all required scenarios in test matrix passing within tolerances; deviations documented with owner/expiry.
- Performance: meets scenario budgets; no stage regression vs prior baselines beyond thresholds.
- Reliability: zero unresolved critical errors (e.g., missing kernel crashes) in opt-in telemetry; fallback event rate below target.
- Documentation: CLI help, docs, and ICS schema notes published; known limitations listed.

## Rollback and Safety
- Off switch available in every release: --cycle-engine off (or env override); tested in CI.
- If severe issue detected post-release, guidance to disable cycles in release notes; ensure aspect-only path unaffected.

### Rollback Playbook
- **Disable cycles at CLI:** run with `--cycle-engine off` (default) and omit cycle-only flags. Compact mode also auto-disables cycles.
- **Force aspect-only outputs:** keep `--mode standard` (or compact for aspect-only compact lines) and avoid passing `--cycle-*` options; logs should not mention a cycle engine.
- **Hotfix guidance:** if a bad build ships, advise users to rerun with `--cycle-engine off` and re-issue ICS to restore prior behavior; aspect outputs are regression-tested for stability when cycles are off.
- **Verification:** generated ICS should contain aspect and optional daily/lunar categories only; no cycle categories present. CI test `test_aspect_only_regression` locks this behavior.
- **Communication snippet:** "If you encounter issues with cycle events, rerun with `--cycle-engine off` to revert to the legacy aspect-only output."

## Observability and Reporting
- Per-run logs: active cycle engine, config snapshot, ayanamsa, cycle_types, chunking, missing-body policy.
- Metrics: runtime, ephemeris_calls, cache stats, refine stats, boundary_drops, skipped_bodies, fallback count; stored in JSON for analysis.
- Telemetry (if used): aggregate opt-in success/failure counts; privacy-safe.

## Known Limitations Tracking
- Maintain list of approved deviations (e.g., placeholder ayanamsa constants) with owner and sunset date.
- Track missing kernels and their impact; suggest remedies.

## User Messaging
- Release notes: toggle usage, benefits (cycle coverage), kernel requirements, known limitations, how to disable.
- Upgrade guide: config changes, new flags, defaults, and examples.

### Release Notes Template (Cycle Opt-In)
- **What changed:** Added HelioNext cycle engine (ingress, synodic phases, retro/stations, distance extrema) behind `--cycle-engine helionext-cycles`.
- **How to enable:** pass `--cycle-engine helionext-cycles` plus optional `--cycle-types`, `--cycle-phase-angles`, `--cycle-ingress-signs`, `--cycle-metrics-path`.
- **How to disable/rollback:** omit the flag or set `--cycle-engine off` (default); compact mode auto-disables cycles.
- **Kernel requirements:** de440s.bsp present locally; if a body is missing and policy=fail (default) run aborts with message; policy=skip logs missing body in metrics under `skipped_bodies`.
- **Known limitations:** boundary_drops reported in metrics; fallback events emit `convergence_status` and `uncertainty_seconds`; distance extrema only available where ephemeris provides distances.
- **Artifacts:** metrics JSON if `--cycle-metrics-path` is set; perf reports under `output/perf/<scenario>.json` for CI gating.
- **Support:** If ICS output looks off, rerun with cycles disabled and attach metrics/log snippets (including config snapshot) when filing an issue.

## Changelog Expectations
- Log feature introduction, changes to defaults, new flags, and any breaking changes with schema_version increments.
- Document when off mode is slated for deprecation; include date/version targets.

## Post-Launch Monitoring
- Watch CI and user reports for increased fallback/uncertainty or runtime regressions.
- Run periodic smoke on long spans to catch drift in ayanamsa or coverage assumptions.

### Monitoring Thresholds and Cadence
- Fallback/uncertainty: warn if `refine_failures` >0.5% of cycle events in a run; investigate if >1.0% or if any event lacks `uncertainty_seconds` when fallback is set.
- Boundary health: warn if `boundary_drops` >0; investigate immediately if >5 per run.
- Missing bodies: warn if `skipped_bodies` non-empty; ensure policy decision is documented or add kernel.
- Runtime/ephem: rely on perf comparator budgets (warn >10%, fail >20%).
- Cadence: review PR perf runs weekly; review nightly/weekly long-run metrics at least once per week; file follow-up tickets for any threshold breach.
- Artifacts: collect metrics JSON (with config_snapshot) and perf comparator output; store dashboards or summaries under `output/ci/<suite>/`.

### Alerting Checklist
- Confirm scenario/config matches baseline (ayanamsa, phases, chunking, bodies).
- Inspect `refine_samples` for slow or failing events; note pairs/signs involved.
- Check cache eviction and chunk_count for unexpected changes.
- For boundary_drops/skipped_bodies, list bodies/signs and decide on kernel fix vs policy waiver.

## Default Promotion Plan
- Entry gates: validation matrix green with no open waivers; perf comparator within budgets; fallback/uncertainty and boundary_drops below thresholds; docs (CLI, ICS schema, rollout notes) refreshed.
- Decision cadence: review weekly during opt-in phase; when two consecutive reviews stay green, schedule candidate-default in the next minor release.
- Toggle plan: switch default to `helionext-cycles` while keeping `--cycle-engine off` for at least one full release cycle; retain compact-mode auto-disable behavior.
- Deprecation window: announce intent to remove the off switch no earlier than the second release after defaulting (e.g., default in 2026.02, earliest removal 2026.04) and only if metrics remain green.
- Changelog stub: "HelioNext cycles now default on; legacy aspect-only mode remains available via `--cycle-engine off` (planned deprecation: >=2026.04)." Include reminder to rerun with off mode if users hit issues.

## Exit Criteria for Deprecating Off Mode
- Sustained period (e.g., one release cycle) with no critical issues and minimal deviations.
- User feedback positive or neutral; performance and accuracy stable; docs up to date.
