# ICS Schema and Formatting

## Goals
- Represent cycle events in ICS without breaking aspect ICS outputs; maintain folding, encoding, and UID conventions.
- Provide clear summaries and descriptions that convey event type, bodies, ayanamsa (if non-tropical), and uncertainty when applicable.

## VEVENT Mapping
- Instants: timed events for ingress, synodic_phase, station, perihelion, aphelion, node/apogee/perigee (if enabled).
- Intervals: retrograde periods (start/end); optional long-duration representation as all-day when above threshold (configurable).
- Categories/tags: optional CATEGORIES field per event_type (e.g., CYCLE, INGRESS, SYNODIC, RETRO, STATION, PERIHELION).
- UID namespace: `cycles-<sha256>@helionext-cycles` (SHA256 over engine|schema_version|event_type|bodies|sign/phase|start_time). Distinct from aspect UID namespace to avoid collisions when mixing calendars.

## Core ICS Fields
- DTSTART/DTEND or DURATION: UTC for timed events; all-day events use DATE only if enabled.
- SUMMARY: concise, deterministic templates per event_type.
- DESCRIPTION: multiline detail including time(s), ayanamsa label (when non-tropical), uncertainty, distance (if available), retro/station markers, phase angle, and any computation notes.
- UID: stable per event (hash of engine, bodies, event_type, time, phase/sign); namespace distinct from aspect UID to avoid collision.
- PRODID: include engine name (HelioNext-Cycles) for traceability.
- STATUS: default CONFIRMED; use TENTATIVE if uncertainty exceeds threshold (optional policy).
- CATEGORIES: optional tagging; configurable on/off.

## Summary Templates (Examples)
- Ingress: "Mercury → Aries" (tropical) or "Mercury → Aries [ayanamsa: galactic_core]" when non-tropical.
- Synodic phase: "Mars 180° Sun" (tropical) or "Mars 180° Sun [ayanamsa: lahiri]"; include ayanamsa tag only when non-tropical.
- Retro interval start: "Mercury Retrograde Begins"; end: "Mercury Retrograde Ends".
- Station: "Mercury Station (F→R)" or "Mercury Station (R→F)".
- Perihelion/Aphelion: "Earth Perihelion" / "Earth Aphelion"; append distance if available.
- Node/Apogee/Perigee: "Moon Ascending Node", "Moon Apogee", "Moon Perigee" when enabled.

## Description Content
- Time(s): UTC formatted; include local time if downstream chooses (same as aspect ICS policy).
- Ayanamsa: include when not tropical; label uses ayanamsa name.
- Uncertainty: include when solver fallback used ("Uncertainty: ±Xs").
- Phase/angle: for synodic_phase, include target angle and raw separation if helpful.
- Retro/station flags: retro intervals explicitly marked; station direction noted.
- Distance: perihelion/aphelion include distance_au to 6 decimals when available.
- Schema version: optionally echo `schema_version` in DESCRIPTION footer for diagnostics.
- Chunking note: optionally include chunk id if run was chunked (debug mode only).

## Formatting Rules
- Folding: 75-byte lines; respect ASCII-only mode (replace glyphs with ASCII labels and remove special symbols).
- Time zones: base UTC; allow tz conversion upstream if existing pipeline supports; keep consistent with aspect ICS.
- All-day vs timed: if interval duration exceeds threshold (configurable, e.g., >48h), may emit all-day with DTEND exclusive; document policy and keep retro intervals timed by default.
- Ordering: events should be emitted sorted by time/type per ordering rules before ICS serialization.

## Optional Fields and Clean Omission
- UNCERTAINTY: only when non-zero; otherwise omit.
- DISTANCE: only for perihelion/aphelion when available; omit cleanly otherwise.
- CATEGORIES: optional; omit if user disables tagging.
- GEO/HOUSE: not used for cycles by default; omit unless policy changes.
- AYANAMSA LABEL: include in SUMMARY/description only when ayanamsa != tropical.

## Collision and Merge Policies
- UID namespace distinct from aspect events; ensure no collision when mixed calendars are produced.
- Merge window dedupe happens before ICS generation; ICS should not attempt merge.

## ASCII vs Unicode
- ASCII mode replaces glyphs with ASCII labels (planet abbreviations, simple arrows); ensure summaries stay under folding limits.
- Unicode mode may include arrows/glyphs consistent with aspect ICS; keep consistent styling.

## Validation Checks
- ICS generation should validate required fields per event_type before writing; fail or skip with log if missing.
- Run a smoke test to ensure generated ICS opens in common clients and passes ical lint (line folding, DTSTART/DTEND correctness).
- Verify UID namespace distinct from aspect ICS; add collision test against sample aspect calendar.
- CI lint plan: add `icalendar`/`ics` round-trip and `ics-validate` (or equivalent) smoke in CI for cycle sample output once generators are wired.
