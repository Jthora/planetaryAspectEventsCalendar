# Business Mode Sample QA — 2025-10-01

## Run Summary
- **Command:**
  ```bash
  python DailyTransitAspectCalendarGenerator.py --start 2025-01-01 --end 2025-01-07 --output output/sample_business_2025w1.ics --daily-summary --interpretation-mode business
  ```
- **Ephemeris:** Default `de440s.bsp`
- **Output:** `output/sample_business_2025w1.ics`
- **Orb:** 1.5° (default)
- **Notes:** Daily summaries enabled; aspect events retained; warnings only for candidates outside the orb threshold.

## Verification Checklist
- ✅ `Market Interpretation` block includes business-mode context, behavior, and action language for every aspect event.
- ✅ `Planetary Context / Behavior / Action` sections populate for both planets involved.
- ✅ `Interaction Dynamics` line reflects symmetric pair narratives.
- ✅ Daily summary events list business-tone blurbs in the "Exact Aspects Today" section.
- ✅ File serializes cleanly and imports into standard calendar clients (line folding confirmed at 75 bytes).

## Follow-Up Actions
- Share ICS sample with content reviewers for tone approval.
- Capture screenshots in client of choice if needed for BI-10 evidence (optional).
- Proceed to BI-11 regression snapshot for standard mode outputs.
