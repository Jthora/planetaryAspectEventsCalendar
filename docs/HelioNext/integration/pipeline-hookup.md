# Pipeline Hookup

- Replace direct legacy detect calls with engine_factory in generator helpers so AspectEvents feed ICS builder, titles, interpretations, and compact formatter unchanged.
- Confirm downstream consumers do not assume legacy-only quirks (boundary projection, merge order, station/retro flags).
- Keep merge window, orb, and retro probe parameters honored by both engines.
- Verify aspect catalog lookups are consistent with scope choices for HelioNext.
- Ensure ICS output shape remains stable; note any schema guarantees in a short contract doc.
