# Raves Mode Technical Specification

## New Files
- astrological_raves_dictionaries.py: RAVES_PLANET_THEMES, raves_aspect_guidance, raves_pair_overrides, default_pair_message, all_raves_planets.
- tools/validate_raves_dicts.py: validator CLI.
- tests/test_raves_interpretations.py: structured mode coverage.
- tests/test_raves_ics_builder.py (or extend existing): ICS description/profile assertions for raves.
 - (Optional helper) per-sign genre/theme mapping table if not in the dictionary module.

## Modified Files
- daily_transit/interpretations.py: add _STRUCTURED_MODE_RESOURCES["raves"], add _PLANET_THEME_MAP["raves"], optional generate_raves_interpretation helper.
- daily_transit/ics_builder.py: make planet profiles pick tone helpers by mode (raves vs business); ensure interpretation_mode is threaded.
- daily_transit/zodiac_metadata.py: add rave tone helpers (element/modality/sign) and exports.
- daily_transit/ics_builder.py: add a mode-gated "Rave Extras" section emitting optional music/outfit/social/safety fields when present.
- DailyTransitAspectCalendarGenerator.py: CLI choices include raves.
- tools/generate_yearly_calendars.py: CLI choices include raves (and space_force parity).

## Data Contracts
- Required keys per aspect entry: severity, headline, impact, action, watch, summary (non-empty, summary <= 120 chars).
- Optional raves extras (if present, non-empty, length-limited): music_genre, music_subgenre, music_theme, music_style, music_speed, music_tone, music_vibe, outfit_cue, social_mode, friend_making_risk, chaos_order, safety_flag, conflict_risk, crowd_profile.
- Severity enum: Opportunity | Watch | High Risk | Info.
- Coverage: all astrological_aspects["aspect_degrees"] keys; planets = DEFAULT_PLANETS + North Node + South Node + Chiron.
- Pair overrides: tuple(sorted) keys; default_pair_message must be non-empty.
- Per-sign genre/theme mapping: deterministic list per sign (e.g., 7 entries) for genre/subgenre/theme defaults.

## Behavior Notes
- Fallback when headline/impact/action all blank: use pending info copy (same as current structured mode behavior).
- Summary trimming: reuse existing _format_summary logic.
- Pair precedence: overrides > default_pair_message > theme-stitch fallback.
- Profiles currently business-toned; must switch by mode.
- Rave Extras render only when interpretation_mode == "raves" and fields are populated; keep ASCII-safe and concise.

## Optional Design Choices
- Whether to auto-fill music fields from sign/element/modality map or require explicit entries.
- Include tempo labels (slow/mid/fast/peak) vs plain text.
- Whether to reuse the extras structure for other modes later (design for expansion).
