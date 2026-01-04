# Raves Validation Plan

## Validator Requirements
- Required keys present and non-empty: severity, headline, impact, action, watch, summary
- Severity in enum: Opportunity | Watch | High Risk | Info
- Summary length <= 120 characters (trimmed)
- Optional extras (if present) non-empty and within length limits (set per field, e.g., 80–120 chars); extras may be omitted
- All aspects from astrological_aspects["aspect_degrees"] present
- Pair override keys valid sorted tuples; default_pair_message non-empty

## Tool
- tools/validate_raves_dicts.py
- Flags: --strict exits 1 on any issue

## Outputs
- Report counts for aspects and pairs
- List issues (missing keys, bad severity, long summary, missing aspect, malformed pairs)

## CI Hook
- Run validator in strict mode in test pipeline; fail build on issues

## Common Errors Checklist
- Missing North/South Node/Chiron themes
- Empty watch/action fields
- Severity typos
- Summaries over length
- Missing minor aspects
- Extras present but empty or over length
