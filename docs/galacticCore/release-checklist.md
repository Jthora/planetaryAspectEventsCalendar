# Release Checklist (Compact Mode)

- [ ] Aspect catalog finalized (Trebiquintile resolved at 108) and wired into detection scopes.
- [ ] Ayanamsa constants validated (tropical/lahiri/galactic_core) with tests.
- [ ] Placidus house computation validated for sample locations; Whole Sign fallback documented and tested.
- [ ] Formatter outputs Z/H/time/Δ with expected precision; ascii-only verified; folding enforced at 75 bytes; retrograde markers present.
- [ ] CLI help updated; examples tested; compact mode enforces required inputs.
- [ ] Regression: legacy modes unaffected (spot-check existing outputs/tests).
- [ ] Docs in docs/galacticCore/ updated; open questions resolved or noted.
- [ ] Sample ICS generated and inspected (small date range) for each ayanamsa option and aspect scope (major/complete), with both precision modes (decimal/DMS).
- [ ] Tests green (unit/integration/snapshots); lint/format if applicable.
- [ ] Performance spot-check recorded (e.g., 7-day complete scope runtime) and documented (seconds-level timing target).
