# Guidance Testing Plan

Unit tests
- Validate every canonical aspect has guidance per mode (no blanks; allow known gaps only if marked in aspect-coverage-matrix).
- Alias normalization: aliases resolve to canonical entries (sample set per mode, include minor/tertiary cases).
- Severity present and within allowed set; tone patterns per mode hold (see mode-style-guides).
- Tertiary/minor aspects in complete scope return populated guidance payloads.
- Snapshots/fixtures: headline/impact/action (and watch if present) are non-empty for emitted aspects.

Integration tests
- Generate ICS via HelioNext, scope=complete, across a short window; assert no blank interpretation sections for enabled modes.
- Spot-check severity and pair overrides appear in formatted ICS.

Manual QA
- Readability/tone pass for each new batch.
- Update aspect-coverage-matrix after authoring and testing a batch.
