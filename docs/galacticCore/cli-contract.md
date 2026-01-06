# CLI Contract (Compact Mode)

## New/updated flags
- --mode compact (or --compact): enables compact output formatting and requires location inputs.
- --ayanamsa {tropical,lahiri,galactic_core}: select offset.
- --lat <deg>, --lon <deg>, --elev <m optional>: required for houses in compact mode.
- --aspect-scope {major,all,complete}: complete uses the catalog list.
- --precision-deg <format>: optional; defaults to scheme in formatting guidelines (e.g., dms or decimal places).
- --precision-time: optional; defaults to HH:MM:SS.
- --ascii-only: reuse existing flag; impacts labels/glyphs.

### Future flags (parked)
- --ayanamsa-custom <deg>: not in scope now; note for future.
- --house-system <placidus|...>: fixed to placidus for this phase.

## Validation rules
- Compact mode must reject missing lat/lon or unknown ayanamsa choice.
- Fails fast on invalid numeric inputs or unsupported scope.
- Default status/product-id behavior unchanged unless overridden.
- If aspect-scope complete is chosen without compact mode, allow but keep formatting per legacy unless compact is on.
- Default ayanamsa when omitted: tropical.

## Examples
- Compact, galactic core, complete aspects:
  - python DailyTransitAspectCalendarGenerator.py --mode compact --ayanamsa galactic_core --lat 40.0 --lon -105.0 --aspect-scope complete --start 2030-01-01 --end 2030-01-07 --output compact.ics
- Compact, tropical, major only:
  - python DailyTransitAspectCalendarGenerator.py --mode compact --ayanamsa tropical --lat 51.5 --lon -0.1 --aspect-scope major --start 2030-01-01 --end 2030-01-02 --output compact_major.ics

## Backward compatibility
- Existing modes and flags remain; compact is opt-in.
- No change to default interpretation-mode; compact bypasses interpretations regardless of prior defaults.
- Precision defaults: decimal angles, HH:MM:SS time; overrideable via flags.
