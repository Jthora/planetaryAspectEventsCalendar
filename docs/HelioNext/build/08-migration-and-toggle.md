# HelioNext Migration and Toggle

## Toggle Design
- CLI flag/env/config to select engine: `legacy` or `helionext` (engine names are literal strings).
- Default: legacy until rollout criteria met (see performance/validation docs).

## Rollout Plan
- Phase 1: internal testing with dual-run diff reports (no user-visible change).
- Phase 2: opt-in HelioNext for power users; monitor metrics (runtime, diff pass rate).
- Phase 3: make HelioNext default once parity and performance targets met; legacy remains switchable.
- Phase 4: deprecate legacy and remove after stability period with user sign-off.

## Rollback
- Always allow switching back to legacy in the same release (flag/env).
- Keep configs backward compatible during transition; no breaking CLI changes.

## Compatibility Notes
- Payload and formatting must remain stable across toggle (titles, Δ, houses, glyphs, folding).
- Document any temporary deviations and workarounds; track in changelog.

## Observability
- Log which engine is active per run (engine name recorded).
- Capture runtime stats and diff outcomes during rollout; alert on regressions.

## User Messaging
- Release notes describing toggle, expected benefits, how to opt-in/out; include known limitations if any.
