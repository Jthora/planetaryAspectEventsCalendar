# Standard Mode Regression QA — 2025-10-02

## Run Summary
- **Command:**
  ```bash
  python DailyTransitAspectCalendarGenerator.py --start 2025-01-01 --end 2025-01-07 --output output/sample_standard_2025w1.ics --daily-summary --interpretation-mode standard
  ```
- **Ephemeris:** Default `de440s.bsp`
- **Output:** `output/sample_standard_2025w1.ics`
- **Orb:** 1.5° (default)
- **Notes:** Daily summaries enabled for parity with business sample; warnings only for aspect candidates outside the orb threshold.

## Verification Checklist
- ✅ Aspect event bodies retain the legacy `Meaning:` line sourced from `astrological_dictionaries.astrological_aspects`.
- ✅ No business-only sections (Market Interpretation, Planetary Context/Action, Interaction Dynamics) appear in standard mode output.
- ✅ Daily summary "Exact Aspects Today" entries render the short-form meanings as before.
- ✅ Generated timestamps, UIDs, and categorization match expectations for equivalent runs in earlier builds.
- ✅ Diff against business sample confirms scope-limited divergence (interpretation blocks only).

## Follow-Up Actions
- Store `output/sample_standard_2025w1.ics` as the current reference for any future snapshot comparisons.
- Optionally archive both standard and business samples for release packaging (zip bundle).
