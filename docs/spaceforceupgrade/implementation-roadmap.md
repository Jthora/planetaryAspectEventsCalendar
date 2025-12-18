# Space Force Mode Implementation Roadmap

## Phase 0 — Alignment
- Review this folder + business mode implementation for reference.
- Confirm stakeholders, content timelines, and deliverables.

## Phase 1 — Scaffolding (Engineering)
1. **Dictionary Module Stub**
   - Create `astrological_spaceforce_dictionaries.py` with empty templates mirroring business structures.
   - Include helpers: `SPACEFORCE_PLANET_THEMES`, `spaceforce_aspect_guidance`, `spaceforce_pair_overrides`, `default_pair_message`, `all_spaceforce_planets`.
2. **Interpretation Registry Refactor**
   - Update `daily_transit/interpretations.py` to support a pluggable registry, e.g. `{mode: InterpretationAdapter}`.
   - Ensure fallback behavior when the module is missing (log warning + reuse standard copy).
3. **CLI Exposure**
   - Add `'space_force'` to `--interpretation-mode` choices in `DailyTransitAspectCalendarGenerator.py`.
   - Update README quickstart + sample commands.

## Phase 2 — Content Integration
1. Populate the dictionary module with Space Force copy.
2. Wire `PLANET_THEMES` usage in `ics_builder` to respect the active mode (inject via builder call or context object).
3. Add any extra metadata needed for Space Force planet profiles (e.g., mission badges, emoji choices).

## Phase 3 — Validation & Tooling
1. Build `tools/validate_spaceforce_dicts.py` (or extend existing validator) to enforce schema completeness.
2. Write unit tests in `tests/test_spaceforce_interpretations.py`:
   - Severity normalization, fallback text, summary truncation.
   - Pair insight selection (override vs default).
3. Generate sample ICS exports (short range) for manual QA; store under `output/samples/`.

## Phase 4 — QA & Docs
1. Follow `qa-checklist.md` to run lint/tests + multi-mode regressions.
2. Update docs (README, Quickstart, enhancement notes) with usage instructions.
3. Gather feedback from Space Force SMEs and iterate on copy.

## Phase 5 — Release
- Tag release notes with new CLI option and validation tooling.
- Announce in CHANGELOG/README.
- Plan follow-up backlog (e.g., dynamic mission presets, integration with Galactic Center workflow).

## Dependencies & Risks
- **Dependencies**: Content delivery schedule, SME availability, validator tooling.
- **Risks**:
  - Incomplete coverage causing empty interpretations (mitigate with validator gate).
  - Tone mismatch (schedule reviews with Space Force advisors).
  - Registry refactor inadvertently altering business mode (add regression tests before merging).

## Success Metrics
- 100% aspect coverage in Space Force dictionaries.
- Unit + validator tests passing in CI.
- Sample ICS reviewed and approved by stakeholders.
- Documentation updated and discoverable via README links.
