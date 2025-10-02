# planetaryAspectEventsCalendar

Tooling and data files for generating planetary aspect calendars and lunar phase timelines.

## Daily Transit Aspect Generator

The `DailyTransitAspectCalendarGenerator.py` script builds an ICS file containing:

- Exact planetary aspect events with Δ/target degrees and retrograde indicators
- Optional daily summary entries listing planetary longitudes and exact aspects
- Optional lunar phase events (New, First Quarter, Full, Last Quarter) in the same calendar

### Requirements

Install the project dependencies (Python 3.10+):

```bash
pip install -r requirements.txt
```

Ensure the JPL SPICE kernel `de440s.bsp` (or a richer kernel such as `de441.bsp` for full outer-planet coverage) is present in the project root.

### Example usage

```bash
python DailyTransitAspectCalendarGenerator.py \
	--start 2024-01-01 --end 2024-01-31 \
	--timezone UTC \
	--lunar-phases \
	--daily-summary \
	--output output/transits_2024_01.ics
```

Helpful toggles:

- `--planets Sun,Moon,Mercury` → restrict aspects to a subset of bodies
- `--ascii-only` → emit ASCII planet/aspect labels and "R" for retrograde
- `--retrograde-probe-hours 12` → adjust retrograde look-ahead window
- `--lunar-phases` → append lunar phase events for the requested range
- `--thunderbird-friendly` → emit stable UIDs and CREATED/LAST-MODIFIED metadata
- `--timing-debug` → log adaptive step sizes, refined deltas, and retrograde probe diagnostics
- `--interpretation-mode business` → switch aspect narratives to business/market guidance (default `standard`)

Generated calendars land in the path specified by `--output` (default `transit_aspects.ics`).

## Additional scripts

Legacy utilities for lunar phases, CSV → ICS conversion, and bulk filtering live alongside the new generator. They remain useful as references while Phase 4–7 improvements are underway.

## Documentation

- Business interpretation rollout plan: `docs/businessInterpretations/business-interpretations-plan.md`
- Editorial tone + glossary: `docs/businessInterpretations/style-guide.md`
- Progress tracking & QA notes:
	- Tracker — `docs/businessInterpretations/progress-tracker.md`
	- Business sample QA — `docs/businessInterpretations/qa-business-mode-sample.md`
	- Standard regression QA — `docs/businessInterpretations/qa-standard-mode-regression.md`
