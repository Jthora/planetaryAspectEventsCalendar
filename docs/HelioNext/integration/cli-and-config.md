# CLI and Config Wiring

- Goal: allow selecting HelioNext end-to-end without breaking legacy defaults.
- Actions:
  - Add `--engine {legacy,helionext}` to main CLIs (DailyTransitAspectCalendarGenerator.py, tools/generate_yearly_calendars.py) and to any batch wrappers.
  - Thread engine into config creation; use engine_factory for detection selection.
  - Validate engine values; fail fast with clear message on invalid input.
  - Add aspect-scope options that map to the aspect catalog (major/minor/tertiary) and keep defaults stable.
  - Document defaults: engine=legacy, aspect_scope=major, orb, merge_window_hours, retrograde_probe_hours.
  - Optionally add ENV override (e.g., CAL_ENGINE) for batch runs.
