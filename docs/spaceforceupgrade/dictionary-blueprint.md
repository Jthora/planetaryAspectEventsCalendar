# Space Force Dictionary Blueprint

This blueprint mirrors the business dictionaries while tailoring content to Space Force operations. Use it as the contract for `astrological_spaceforce_dictionaries.py`.

## Modules & Symbols
| Symbol | Type | Description |
| --- | --- | --- |
| `SPACEFORCE_PLANET_THEMES` | `Dict[str, str]` | Maps planet → mission theme (e.g., `"Mars": "tactical thrust"`). |
| `spaceforce_aspect_guidance` | `Dict[str, Dict[str, Dict[str, str]]]` | Nested map: `{"major_aspects": {aspect: guidance}, "minor_aspects": {...}}`. |
| `spaceforce_pair_overrides` | `Dict[Tuple[str, str], str]` | Optional bespoke copy for specific planet pairs. |
| `default_pair_message(planet_a, planet_b)` | `Callable[[str,str], str]` | Fallback when no override exists. |
| `all_spaceforce_planets()` | `Tuple[str, ...]` | Ensures coverage equals `DEFAULT_PLANETS` + mission extras.

## Guidance Entry Schema
Each aspect entry mirrors the current business template.

```python
guidance_entry = {
    "severity": "Opportunity|Watch|High Risk|Info",
    "headline": "<Situation + imperative>",
    "impact": "<Why it matters>",
    "action": "<Directive>",
    "watch": "<Sensor/metric to monitor>",
    "summary": "<≤120 char snippet for daily lists>",
}
```

Rules:
1. All required keys must be non-empty strings.
2. `summary` should read like a single breath mission note.
3. `action` should include a time horizon ("within 6 hours", "next watch").

## Coverage Expectations
- **Aspects**: every entry in `astrological_aspects["aspect_degrees"]` must be represented. Use helper script to diff keys regularly.
- **Planets**: align with `daily_transit.constants.DEFAULT_PLANETS` plus mission entities (North Node, South Node, Chiron) used by other modes.
- **Pairs**: Provide overrides for high-traffic combinations (Sun-Moon, Sun-Mars, Moon-Mars, etc.). Defaults should stitch the two theme strings into a mission insight.

## Validation Hooks
- Add `tools/validate_spaceforce_dicts.py` to assert:
  - No missing keys or blank strings.
  - Summaries ≤ 120 chars.
  - Severity in allowed enum.
- Extend CI/test suite to run the validator plus unit tests covering `generate_spaceforce_interpretation`.

## Content Workflow
1. Export required keys (`tools/export_aspect_keys.py` enhancement) to share with writers.
2. Draft copy in shared spreadsheet or markdown table following schema.
3. Convert to Python dict (script or manual) and drop into `astrological_spaceforce_dictionaries.py`.
4. Run validator + sample ICS to confirm integration.

## Future-proofing
- Keep dictionaries in Python for now, but design with potential JSON/YAML ingestion later.
- Consider splitting major/minor aspect files if content grows beyond ~800 lines for readability.
