# Business Interpretation Expansion Plan

## 1. Purpose
Provide a blueprint for introducing market-focused astrological interpretations alongside the existing standard narratives without disrupting current exports. The new content targets business, finance, economy, industry, and trading use cases and must remain selectable via `--interpretation-mode business`.

## 2. Guiding Principles
- **Parallelism:** Maintain the legacy story set untouched; business copy ships as an additive layer.
- **Single Source of Truth:** Centralize all interpretation data (standard + business) in the dictionary layer so every generator consumes the same interface.
- **Traceability:** Track coverage of every aspect, planet, and pairing to ensure no gaps during exports.
- **Editorial Consistency:** Deliver concise, actionable language that speaks to corporate decision-makers and traders.
- **Future Proofing:** Make it easy to extend interpretations when new bodies/aspects are added.

## 3. Scope & Deliverables
- New dictionary module containing market-focused narrative components:
  - Aspect context, behavior, and action guidance (major & minor splits).
  - Planet-specific context, behavior, and action summaries.
  - Planet pair interaction blurbs.
- Updated documentation and schema definitions.
- Validation harness (unit checks + sample ICS output review).
- Optional template/YAML assets for non-developer contributions.

## 4. Integration Architecture
1. **Dictionary layer additions** (recommended file: `astrological_business_dictionaries.py`).
   - Expose nested dictionaries mirroring the structures consumed by `daily_transit/interpretations.py`.
   - Import or load these dictionaries inside `interpretations.py`, guarding with fallbacks for missing files (matching legacy patterns).
2. **Interpretation selection** remains in `daily_transit/interpretations.get_interpretation`.
   - `mode="standard"` → current `astrological_aspects["aspect_meanings"]`.
   - `mode="business"` → new business dictionaries assembled into structured output.
3. **ICS generator** already accepts `--interpretation-mode`; no further plumbing required once dictionaries exist.
4. **Legacy CSV workflows** can optionally consume the new dictionaries by importing the module directly (extend after the primary integration if needed).

## 5. Data Model Specification
| Component | Structure | Required Keys | Notes |
|-----------|-----------|---------------|-------|
| Aspect context | `{"major_aspects": {aspect: str}, "minor_aspects": {...}}` | Every aspect exported by `select_aspects()` | Macro/micro economic framing. |
| Aspect behavior | Same as context | Same aspects | Expected price/market response. |
| Aspect action | Same as context | Same aspects | Trade/strategy recommendation or caution. |
| Planet context | `{planet: str}` | Planets listed in `DEFAULT_PLANETS` (plus any extras used) | Corporate/sector associations. |
| Planet behavior | `{planet: str}` | Same | Operational tendencies and volatility cues. |
| Planet action | `{planet: str}` | Same | Strategic stance when the planet is prominent. |
| Planet pair interactions | `{planet1: {planet2: str}}` | Each ordered pair used in outputs | Highlight leadership conflicts, innovation vs. regulation, etc. |

## 6. Editorial Guidelines
- **Audience:** Portfolio managers, corporate strategists, macro/quant analysts.
- **Voice:** Confident, concise, data-driven tone. Avoid jargon unless widely understood (e.g., "liquidity", "volatility").
- **Focus Areas:**
  - Market drivers (momentum, sentiment, credit conditions).
  - Industry sectors (tech, energy, finance) when planets imply specific domains.
  - Decision making (invest, hold, hedge, review strategies).
- **Do/Don’t:**
  - Do mention risk levels and possible time horizons.
  - Do suggest follow-up actions ("review supply-chain KPIs", "tighten stop losses").
  - Don’t promise guaranteed outcomes or make compliance-sensitive claims.
  - Don’t conflict with standard interpretations; business mode reframes rather than contradicts.
- **Length Targets:**
  - Aspect summary (for daily lists): ≤ 120 characters when possible.
  - Detailed lines: 1–3 sentences per category with scannable keywords.

## 7. Authoring Workflow
1. **Inventory:** Export current aspects/planets in use via helper script to seed spreadsheet.
2. **Drafting:**
   - Use shared spreadsheet with columns matching dictionaries.
   - Write major aspects first, then minors, planets, and pairwise interactions.
3. **Review:**
   - Editorial review for tone and accuracy.
   - Compliance/legal pass if needed.
4. **Import:**
   - Convert spreadsheet to JSON/py dict using automated script (to be built if editors prefer spreadsheets) or manually copy into module.
5. **Verification:**
   - Run `python DailyTransitAspectCalendarGenerator.py ... --interpretation-mode business` for sample range.
   - Spot-check ICS entries for formatting, line folding, and clarity.
6. **Sign-off:**
   - Update progress tracker.
   - Merge once QA approves.

## 8. Tooling & Automation
- **Scripts to add (optional):**
  - `tools/export_aspect_keys.py` → prints required aspect/planet keys for copywriters.
  - `tools/validate_business_dicts.py` → ensures every key has non-empty content.
- **Linting:**
  - Extend CI to call the validation script and fail on missing keys or blank strings.

## 9. Testing & QA Checklist
- Unit tests for `generate_business_interpretation` (fixtures with sample dict entries).
- Regression test: ensure standard mode outputs remain unchanged (snapshot diff).
- Manual QA: verify ICS events display business interpretation block with blank-line separation.
- Optional: build doc tests verifying markdown tables and references remain intact.

### Current QA Artifacts
- Business-mode sample + checklist: `docs/businessInterpretations/qa-business-mode-sample.md`
- Standard-mode regression notes: `docs/businessInterpretations/qa-standard-mode-regression.md`
- Reference ICS exports live under `output/sample_business_2025w1.ics` and `output/sample_standard_2025w1.ics`.

## 10. Timeline (Suggested)
| Phase | Duration | Owner | Exit Criteria |
|-------|----------|-------|---------------|
| Requirements finalization | 0.5 day | Product/Content | Style guide complete, key list approved |
| Draft major aspects | 1.5 days | Content | All major aspects populated & reviewed |
| Draft minor aspects | 1 day | Content | Minor aspects populated & reviewed |
| Planet & pair narratives | 1.5 days | Content | Planet dictionaries & core pairs done |
| Integration & scripts | 1 day | Engineering | Module added, validation scripts ready |
| QA & polishing | 1 day | Engineering + Content | Tests green, sample ICS approved |

## 11. Dependencies & Risks
- **Dependencies:** Content team availability, compliance review, final decision on storage format.
- **Risks:**
  - Incomplete coverage causing empty ICS sections (mitigate with validation script).
  - Tone mismatch for enterprise audience (mitigate via editorial review).
  - Dictionary bloat affecting readability (consider splitting by category if file grows too large).

## 12. Next Actions
1. Finalize storage format decision (Python module vs JSON/YAML).
2. Bootstrap dictionary file with empty placeholders for every required key.
3. Build key-export helper for writers.
4. Begin content drafting and update the progress tracker (see `progress-tracker.md`).
