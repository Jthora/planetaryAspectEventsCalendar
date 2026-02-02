# Guidance Authoring Checklist

For each aspect in the catalog (major, minor, tertiary), per mode:
- [ ] Headline, impact, action (and watch if applicable) are authored and non-empty.
- [ ] Severity set (Opportunity/Watch/High Risk/Info) matches mode tone (see mode-style-guides).
- [ ] Alias normalization applied (use canonical key; map synonyms in alias-mapping).
- [ ] Pair override needed? If yes, add; else default pair message is acceptable.
- [ ] Summary length reasonable; headline/impact/action concise.

Batch workflow:
- [ ] Prioritize aspects per content-plan; mark progress in aspect-coverage-matrix using status codes (C/F/-).
- [ ] After authoring a batch, run unit tests to ensure no blanks; update fixtures if needed.
- [ ] Run an ICS integration (helionext complete scope) to spot-check rendered text.
