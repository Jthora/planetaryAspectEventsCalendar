# Raves Mode Implementation Roadmap

## Phases
- Phase 1: Scaffold raves dictionary module with planet themes, guidance template, pair overrides stub, default pair message, all_raves_planets.
- Phase 2: Register mode in interpretations (resources + theme map + optional generator wrapper).
- Phase 3: Add rave tone helpers (element/modality/sign) and make planet profiles mode-aware in ics_builder.
- Phase 4: Extend CLI choices (DailyTransitAspectCalendarGenerator, tools/generate_yearly_calendars) to include raves.
- Phase 5: Add optional extras fields (music/outfit/social/safety) to guidance contract and per-sign genre map helper.
- Phase 6: Add validator script for raves dictionaries, including optional extras length/non-empty checks when present.
- Phase 7: Add tests (interpretations, ICS builder including “Rave Extras”, validator strict failure/pass, per-sign genre defaults where used).
- Phase 8: Generate sample ICS (manual sanity) and capture notes on extras rendering.
- Phase 9: Update docs indexes or release notes if needed.

## Dependencies
- Registry update precedes tests and CLI generation.
- Tone plumbing precedes ICS profile expectations.
- Validator exists before CI hook.

## Exit Criteria
- Each phase ends with green tests (where applicable) and docs ticked here.
- Mode selectable via CLI, produces ICS with rave tone in interpretations and profiles.
- Validator catches missing/invalid entries.
- Sample ICS generated without errors.
