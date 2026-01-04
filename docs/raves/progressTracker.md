# Raves Mode Progress Tracker

Stage 1: Foundations
- [x] Phase 1.1: Planning & Contracts
  - [x] Step 1.1.1: Confirm scope and schema
    - [x] Sub-Step 1.1.1.1: Lock dictionary contract
      - [x] Task 1.1.1.1.1: Review dictionary-contract.md
        - [x] Sub-Task 1.1.1.1.1.1: Capture any gaps or conflicts
      - [x] Task 1.1.1.1.2: Align severity/summary constraints
        - [x] Sub-Task 1.1.1.1.2.1: Note trimming rules and fallback behavior
    - [x] Sub-Step 1.1.1.2: Confirm tone strategy
      - [x] Task 1.1.1.2.1: Approve element/modality/sign tone plan
        - [x] Sub-Task 1.1.1.2.1.1: Validate tone-mapping coverage
  - [x] Step 1.1.2: Delivery plan
    - [x] Sub-Step 1.1.2.1: Finalize roadmap
      - [x] Task 1.1.2.1.1: Mark phase dependencies
        - [x] Sub-Task 1.1.2.1.1.1: Identify critical path items

Stage 2: Dictionary Scaffolding
- [x] Phase 2.1: Module Creation
  - [x] Step 2.1.1: Add astrological_raves_dictionaries.py
    - [x] Sub-Step 2.1.1.1: Define RAVES_PLANET_THEMES
      - [x] Task 2.1.1.1.1: Populate all planets + nodes + Chiron
        - [x] Sub-Task 2.1.1.1.1.1: Cross-check with planet-themes-mapping.md
    - [x] Sub-Step 2.1.1.2: Build guidance template (major/minor)
      - [x] Task 2.1.1.2.1: Pre-seed all aspect keys
        - [x] Sub-Task 2.1.1.2.1.1: Verify against astrological_aspects["aspect_degrees"]
    - [x] Sub-Step 2.1.1.3: Pair insights
      - [x] Task 2.1.1.3.1: Add default_pair_message
        - [x] Sub-Task 2.1.1.3.1.1: Ensure non-empty fallback text
      - [x] Task 2.1.1.3.2: Seed high-traffic overrides
        - [x] Sub-Task 2.1.1.3.2.1: Cover Sun-Moon, Sun-Mars, Moon-Mars, etc.
    - [x] Sub-Step 2.1.1.4: Add optional extras fields to guidance entries
      - [x] Task 2.1.1.4.1: Define music/outfit/social/safety field names
        - [x] Sub-Task 2.1.1.4.1.1: Set per-field length limits
      - [x] Task 2.1.1.4.2: Document optional nature and defaults
        - [x] Sub-Task 2.1.1.4.2.1: Ensure non-empty if present

Stage 3: Engine Wiring
- [x] Phase 3.1: Interpretation Registry
  - [x] Step 3.1.1: Register mode in interpretations.py
    - [x] Sub-Step 3.1.1.1: Add _STRUCTURED_MODE_RESOURCES["raves"]
      - [x] Task 3.1.1.1.1: Wire guidance/themes/pairs/defaults
        - [x] Sub-Task 3.1.1.1.1.1: Ensure major/minor fallback sets
    - [x] Sub-Step 3.1.1.2: Update _PLANET_THEME_MAP
      - [x] Task 3.1.1.2.1: Include raves mapping
        - [x] Sub-Task 3.1.1.2.1.1: Validate fallback behavior for unknown modes
- [x] Phase 3.2: Tone Plumbing
  - [x] Step 3.2.1: Add rave tone helpers to zodiac_metadata.py
    - [x] Sub-Step 3.2.1.1: Implement element_raves_tone
      - [x] Task 3.2.1.1.1: Map Fire/Earth/Air/Water
        - [x] Sub-Task 3.2.1.1.1.1: Keep strings concise
    - [x] Sub-Step 3.2.1.2: Implement modality_raves_tone
      - [x] Task 3.2.1.2.1: Map Cardinal/Fixed/Mutable
        - [x] Sub-Task 3.2.1.2.1.1: Align wording with rave context
    - [x] Sub-Step 3.2.1.3: Implement sign_raves_tone
      - [x] Task 3.2.1.3.1: Cover all 12 signs
        - [x] Sub-Task 3.2.1.3.1.1: Confirm ASCII safety
  - [x] Step 3.2.2: Mode-aware profiles in ics_builder.py
    - [x] Sub-Step 3.2.2.1: Select tone helpers by interpretation_mode
      - [x] Task 3.2.2.1.1: Preserve business behavior for other modes
        - [x] Sub-Task 3.2.2.1.1.1: Add tests for mode switch
  - [x] Step 3.2.3: Rave Extras rendering in ics_builder.py
    - [x] Sub-Step 3.2.3.1: Add mode-gated extras section
      - [x] Task 3.2.3.1.1: Output only populated optional fields
        - [x] Sub-Task 3.2.3.1.1.1: Keep lines concise and ASCII-safe
    - [ ] Sub-Phase 3.2.3.2: Hook per-sign genre/theme map if auto-fill used
      - [ ] Task 3.2.3.2.1: Bias by sign/element/modality
        - [ ] Sub-Task 3.2.3.2.1.1: Ensure deterministic selection

Stage 4: CLI & Tooling
- [x] Phase 4.1: Main Generator
  - [x] Step 4.1.1: Extend DailyTransitAspectCalendarGenerator choices
    - [x] Sub-Step 4.1.1.1: Add raves to argparse choices
      - [x] Task 4.1.1.1.1: Update help text and default behavior
- [x] Phase 4.2: Batch Helper
  - [x] Step 4.2.1: Update tools/generate_yearly_calendars.py choices
    - [x] Sub-Step 4.2.1.1: Add raves (and space_force parity)
      - [x] Task 4.2.1.1.1: Verify command assembly includes mode

Stage 5: Validation
- [x] Phase 5.1: Validator Script
  - [x] Step 5.1.1: Create tools/validate_raves_dicts.py
    - [x] Sub-Step 5.1.1.1: Enforce required keys/severity/summary length/aspect coverage
      - [x] Task 5.1.1.1.1: Print report counts and issues
        - [x] Sub-Task 5.1.1.1.1.1: Implement --strict exit code
    - [x] Sub-Step 5.1.1.2: Check pair overrides and default_pair_message
      - [x] Task 5.1.1.2.1: Detect malformed/duplicate pairs
        - [x] Sub-Task 5.1.1.2.1.1: Note uncovered planets for defaults
    - [x] Sub-Step 5.1.1.3: Validate optional extras
      - [x] Task 5.1.1.3.1: Enforce non-empty and length limits when present
        - [x] Sub-Task 5.1.1.3.1.1: Keep extras optional (no failure if absent)

Stage 6: Testing
- [x] Phase 6.1: Interpretation Tests
  - [x] Step 6.1.1: Add tests/test_raves_interpretations.py
    - [x] Sub-Step 6.1.1.1: Structured guidance path
      - [x] Task 6.1.1.1.1: Assert severity/headline/action surfaced
        - [x] Sub-Task 6.1.1.1.1.1: Confirm summary trimming
    - [x] Sub-Step 6.1.1.2: Fallback path
      - [x] Task 6.1.1.2.1: Missing aspect returns pending info
        - [x] Sub-Task 6.1.1.2.1.1: Pair insight still present
    - [x] Sub-Step 6.1.1.3: Theme switching
      - [x] Task 6.1.1.3.1: raves planet themes used; unknown mode falls back
        - [x] Sub-Task 6.1.1.3.1.1: Cover major vs minor buckets
- [x] Phase 6.2: ICS Builder Tests
  - [x] Step 6.2.1: Extend or add test_raves_ics_builder.py
    - [x] Sub-Step 6.2.1.1: Aspect event description contains rave copy
      - [x] Task 6.2.1.1.1: Check badge/headline/action/watch lines
        - [x] Sub-Task 6.2.1.1.1.1: Confirm Interaction Insight appended
    - [x] Sub-Step 6.2.1.2: Planet profiles use rave tones
      - [x] Task 6.2.1.2.1: Verify element/modality/sign lines swap to rave strings
        - [x] Sub-Task 6.2.1.2.1.1: ASCII-only path still valid
    - [x] Sub-Step 6.2.1.3: Rave Extras block renders correctly
      - [x] Task 6.2.1.3.1: Ensure extras appear when provided
        - [x] Sub-Task 6.2.1.3.1.1: Ensure extras omitted when absent
- [x] Phase 6.3: Validator Test
  - [x] Step 6.3.1: Add validator invocation test
    - [x] Sub-Step 6.3.1.1: Strict mode fails on bad fixture
      - [x] Task 6.3.1.1.1: Include missing key + bad severity sample
        - [x] Sub-Task 6.3.1.1.1.1: Assert exit code 1
    - [x] Sub-Step 6.3.1.2: Strict mode passes on good fixture
      - [x] Task 6.3.1.2.1: Assert exit code 0

Stage 7: Content Population (Initial Pass)
- [x] Phase 7.1: Major Aspects
  - [x] Step 7.1.1: Fill top aspects (Conjunction, Opposition, Trine, Square, Sextile)
    - [x] Sub-Step 7.1.1.1: Encode CEO asks (day quality, chaos/order, social, safety, music/style)
      - [x] Task 7.1.1.1.1: Ensure summary <= 120 chars
        - [x] Sub-Task 7.1.1.1.1.1: Include action time horizon
- [x] Phase 7.2: Minor Aspects
  - [x] Step 7.2.1: Fill minor set with concise, useful cues
    - [x] Sub-Step 7.2.1.1: Cover friction/adjustment/social shifts
      - [x] Task 7.2.1.1.1: Maintain severity discipline
        - [x] Sub-Task 7.2.1.1.1.1: Keep watch/action specific
- [x] Phase 7.3: Pair Overrides
  - [x] Step 7.3.1: Populate high-traffic pairs
    - [x] Sub-Step 7.3.1.1: Include social/safety/style levers per pair
      - [x] Task 7.3.1.1.1: Balance themes and keep succinct
        - [x] Sub-Task 7.3.1.1.1.1: Avoid duplication across pairs
- [x] Phase 7.4: Extras Population
  - [x] Step 7.4.1: Seed optional extras for key aspects
    - [x] Sub-Step 7.4.1.1: Populate music_genre/subgenre/theme/style/speed/tone/vibe where helpful
      - [x] Task 7.4.1.1.1: Keep under length limits
    - [x] Sub-Step 7.4.1.2: Add outfit_cue, social_mode, safety_flag/conflict_risk when relevant
      - [x] Task 7.4.1.2.1: Keep concise and actionable
  - [x] Step 7.4.2: Define per-sign genre list (7 entries) with overlaps
    - [x] Sub-Step 7.4.2.1: Store in dictionary module or helper
      - [x] Task 7.4.2.1.1: Align with tone-mapping guidance

Stage 8: Validation & CI Hook
- [x] Phase 8.1: Run Validator
  - [x] Step 8.1.1: tools/validate_raves_dicts.py --strict
    - [x] Sub-Step 8.1.1.1: Resolve reported issues
      - [x] Task 8.1.1.1.1: Iterate until clean
        - [x] Sub-Task 8.1.1.1.1.1: Record outcomes in notes
- [ ] Phase 8.2: Wire CI
  - [ ] Step 8.2.1: Add validator to pipeline
    - [ ] Sub-Step 8.2.1.1: Ensure failures block merges
      - [ ] Task 8.2.1.1.1: Document step in CI config
        - [ ] Sub-Task 8.2.1.1.1.1: Confirm green run

Stage 9: Sample ICS & Sanity
- [x] Phase 9.1: Generate Sample
  - [x] Step 9.1.1: Run DailyTransitAspectCalendarGenerator with mode raves
    - [x] Sub-Step 9.1.1.1: Inspect aspect event description
      - [x] Task 9.1.1.1.1: Confirm rave tone and interaction insight
        - [x] Sub-Task 9.1.1.1.1.1: Check summary line fits 120 char limit
    - [x] Sub-Step 9.1.1.2: Inspect planet profiles
      - [x] Task 9.1.1.2.1: Verify tone swap worked
        - [x] Sub-Task 9.1.1.2.1.1: Check ASCII path if used

Stage 10: Documentation Update
- [ ] Phase 10.1: Docs
  - [ ] Step 10.1.1: Update any high-level references/readme if needed
    - [ ] Sub-Step 10.1.1.1: Add raves mode mention
      - [ ] Task 10.1.1.1.1: Link to raves docs set
        - [ ] Sub-Task 10.1.1.1.1.1: Confirm links valid

Stage 11: Final Review
- [ ] Phase 11.1: Consolidation
  - [ ] Step 11.1.1: Re-run tests and validator
    - [ ] Sub-Step 11.1.1.1: Confirm clean tree
      - [ ] Task 11.1.1.1.1: Note any residual risks
        - [ ] Sub-Task 11.1.1.1.1.1: Prepare release notes if needed
