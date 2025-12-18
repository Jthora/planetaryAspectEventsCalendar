# planetaryAspectEventsCalendar

Tooling and data files for generating planetary aspect calendars and lunar phase timelines.

## Daily Transit Aspect Generator

The `DailyTransitAspectCalendarGenerator.py` script builds an ICS file containing:

- Exact planetary aspect events with Δ/target degrees and retrograde indicators
- Optional daily summary entries listing planetary longitudes and exact aspects
- Optional lunar phase events (New, First Quarter, Full, Last Quarter) in the same calendar

### Quickstart

1. **Install dependencies** (Python 3.10+):

	 ```bash
	 pip install -r requirements.txt
	 ```

2. **Place the ephemeris kernel** (`de440s.bsp` or the larger `de441.bsp`) in the project root. Download fresh kernels from the [JPL NAIF archive](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/).

3. **Run your first export**. The example below creates a one-week business-mode calendar with daily summaries and lunar phases:

	 ```bash
	 python DailyTransitAspectCalendarGenerator.py \
		 --start 2025-10-03 --end 2025-10-09 \
		 --daily-summary \
		 --lunar-phases \
		 --interpretation-mode business \
		 --output output/zodiac_week_2025-10-03_to_2025-10-09.ics
	 ```

The generated `.ics` file is written to the location specified by `--output` (default `transit_aspects.ics`).

### Helpful toggles

- `--planets Sun,Moon,Mercury` → restrict aspects to a subset of bodies
- `--ascii-only` → emit ASCII planet/aspect labels and "R" for retrograde
- `--retrograde-probe-hours 12` → adjust retrograde look-ahead window
- `--lunar-phases` → append lunar phase events for the requested range
- `--thunderbird-friendly` → emit stable UIDs and CREATED/LAST-MODIFIED metadata
- `--timing-debug` → log adaptive step sizes, refined deltas, and retrograde probe diagnostics
- `--interpretation-mode business` → switch aspect narratives to business/market guidance (default `standard`)
- `--interpretation-mode space_force` → experimental guardian-mode copy tuned for Space Force mission life

### Space Force mode (experimental)
- Invoke with `--interpretation-mode space_force` to receive mission-brief style narratives for Guardians and allied crews.
- Follow the authoring and QA guidance in `docs/spaceforceupgrade/` (style guide, dictionary blueprint, validator instructions).
- A sample export lives at `output/sample_space_force_2025-01-01_to_2025-01-03.ics` for quick previews.

### Year-by-year recipes

Copy and paste any of these ready-made commands to generate full-year calendars:

```bash
# 2025 — business tone, glyphs on, includes lunar phases
python DailyTransitAspectCalendarGenerator.py \
	--start 2025-01-01 --end 2025-12-31 \
	--daily-summary \
	--lunar-phases \
	--interpretation-mode business \
	--product-id "-//Planetary Aspect Events//EN" \
	--output output/zodiac_year_2025.ics

# 2026 — standard tone, no lunar phases (pure aspects + daily summaries)
python DailyTransitAspectCalendarGenerator.py \
	--start 2026-01-01 --end 2026-12-31 \
	--daily-summary \
	--interpretation-mode standard \
	--output output/transits_2026.ics

# ASCII-friendly export for text-only calendar clients
python DailyTransitAspectCalendarGenerator.py \
	--start 2024-01-01 --end 2024-12-31 \
	--daily-summary \
	--lunar-phases \
	--ascii-only \
	--output output/transits_2024_ascii.ics
```

Pro tips:

- Long ranges (full year) can take hours with default precision. For faster previews, narrow the planet list or raise `--coarse-step-mins`.
- Add `--timezone America/New_York` (or any `pytz` zone) to localise timestamps.
- Include `--thunderbird-friendly` when syncing with Thunderbird to stabilise UIDs.

## Additional scripts

Legacy utilities for lunar phases, CSV → ICS conversion, and bulk filtering live alongside the new generator. They remain useful as references while Phase 4–7 improvements are underway.

## Documentation

- Business interpretation rollout plan: `docs/businessInterpretations/business-interpretations-plan.md`
- Editorial tone + glossary: `docs/businessInterpretations/style-guide.md`
- Progress tracking & QA notes:
	- Tracker — `docs/businessInterpretations/progress-tracker.md`
	- Business sample QA — `docs/businessInterpretations/qa-business-mode-sample.md`
	- Standard regression QA — `docs/businessInterpretations/qa-standard-mode-regression.md`
