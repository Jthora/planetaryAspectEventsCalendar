# Space Force Mode QA Checklist

Use this checklist before merging any change that affects the Space Force interpretation mode.

## 1. Automated Validation
- [ ] `pytest tests/test_spaceforce_interpretations.py`
- [ ] `python tools/validate_spaceforce_dicts.py`
- [ ] Existing standard/business tests still pass.

## 2. Dictionary Completeness
- [ ] Every aspect key present in `astrological_aspects["aspect_degrees"]` has a non-empty entry.
- [ ] `SPACEFORCE_PLANET_THEMES` covers `DEFAULT_PLANETS` + supplemental entities.
- [ ] Summaries ≤ 120 characters.
- [ ] Severity values limited to `Opportunity`, `Watch`, `High Risk`, `Info`.

## 3. ICS Output Verification
- [ ] Generate a 7-day sample with `--interpretation-mode space_force` (include major & minor aspects). Reference sample: `output/sample_space_force_2025-01-01_to_2025-01-03.ics`.
- [ ] Spot-check 3 aspect events (different severities) for formatting and copy accuracy.
- [ ] Confirm daily summary entries display the new summaries without truncation issues.
- [ ] Verify Planet Profiles reference Space Force themes when mode is active.
- [ ] Run `python tools/ics_sanity_check.py --ics <file>.ics --reference horizons --output-csv output/reports/<file>_sanity.csv` and attach the CSV summary (use `--reference skyfield` only for offline dry-runs).

## 4. Regression Checks
- [ ] Run the same date range under `standard` and `business` modes and diff descriptions to confirm no unintended changes.
- [ ] Thunderbird-friendly export still serializes correctly when the new mode is selected.

## 5. Documentation & Changelog
- [ ] README and Quickstart mention the new CLI option.
- [ ] `docs/spaceforceupgrade` updated if process or guidelines changed.
- [ ] Changelog entry summarises feature + validation status.

## 6. Stakeholder Sign-off
- [ ] Content/Space Force SME approved copy samples.
- [ ] Engineering lead reviewed code diffs and tests.
- [ ] QA lead signed off on checklist.

Keep the filled checklist (with links or logs) attached to the PR for transparency.
