# Enhancement Proposal: Zodiac-Rich Aspect Copy

## Goal
Elevate business-mode aspect events by weaving in zodiac symbology, elemental colors, and modality framing so the calendars communicate both the narrative and the astrological fabric at a glance.

## Motivation
- **Executive readability:** Summaries like `SUMMARY:<|☉ □ ♆]` immediately convey sign context without scrolling into the description. (this example shows Libra Sun square Neptune in Leo)
- **Astro depth:** Planet sub-sections extend the story with how each body behaves under its current sign, element, and modality.
- **Consistency:** Aligns iCal output with the existing symbol taxonomy that already appears in legacy generators and documentation.

## Scope
- Reuse the canonical glyph metadata (emoji, element glyph, modality brackets/shape, color cue) for all 12 signs.
- Update `daily_transit/ics_builder.py` to:
  - Render summaries using left/right zodiac framing characters and compact aspect symbols.
  - Append per-planet sub-descriptions covering sign, element, modality, and business-theme modulation.
- Ensure ASCII fallbacks remain legible for text-first calendar clients.
- Extend unit tests to exercise the enhanced summary and description output.
- Regenerate pilot ICS samples (2025 focus) for QA before scaling to full-year exports.

### Zodiac framing reference
All metadata originates from `GalacticCenterAyanamsa.ZODIAC_SIGNS_EMOJI_AND_SYMBOLS` and will be surfaced through a dedicated helper in `daily_transit/zodiac_metadata.py`.

| Sign | Emoji | Element Glyph | Color Cue | Modality Shape | Left Framing | Right Framing |
|------|-------|---------------|-----------|----------------|--------------|---------------|
| Aries | ♈ | 🜂 (Fire) | 🟥 | ▲ (Cardinal) | `<` | `>` |
| Taurus | ♉ | 🜃 (Earth) | 🟩 | ■ (Fixed) | `]|` | `|[` |
| Gemini | ♊ | 🜁 (Air) | 🟨 | ● (Mutable) | `(|` | `|)` |
| Cancer | ♋ | 🜄 (Water) | 🟦 | ▲ (Cardinal) | `>` | `<` |
| Leo | ♌ | 🜂 (Fire) | 🟥 | ■ (Fixed) | `[` | `]` |
| Virgo | ♍ | 🜃 (Earth) | 🟩 | ● (Mutable) | `)|` | `|(` |
| Libra | ♎ | 🜁 (Air) | 🟨 | ▲ (Cardinal) | `<|` | `|>` |
| Scorpio | ♏ | 🜄 (Water) | 🟦 | ■ (Fixed) | `]` | `[` |
| Sagittarius | ♐ | 🜂 (Fire) | 🟥 | ● (Mutable) | `(` | `)` |
| Capricorn | ♑ | 🜃 (Earth) | 🟩 | ▲ (Cardinal) | `>|` | `|<` |
| Aquarius | ♒ | 🜁 (Air) | 🟨 | ■ (Fixed) | `[|` | `|]` |
| Pisces | ♓ | 🜄 (Water) | 🟦 | ● (Mutable) | `)` | `(` |

**ASCII fallback:** when `--ascii-only` is enabled, summaries replace planet glyphs with two-letter labels and omit color emojis, e.g. `<| Sun [SQR] Nep ]`. Descriptions should preserve bracket framing while substituting the element glyph with its text label (e.g. `Fire`), and map modality shapes to words (`Triangle`, `Square`, `Circle`).

## Deliverables
1. `daily_transit/zodiac_metadata.py` (or equivalent module) exposing reusable glyph + description helpers.
2. Updated ICS builder and interpretation utilities leveraging the new helpers.
3. Expanded business-mode QA assets demonstrating the richer copy.
4. Documentation updates (this doc + progress tracker) to socialize the change with the team.

### Planet sub-description template
Each aspect event description appends a section per planet using the following structure:

1. **Heading:** `<FramingLeft> PlanetName PlanetEmoji <FramingRight>` (include sign name).
2. **Sign line:** `Sign • Emoji`.
3. **Element line:** `Element • Glyph • Color` with a short clause on how the element modulates the planet.
4. **Modality line:** `Modality • Shape` plus a modulation clause.
5. **Planet-in-sign synthesis:** One sentence referencing the planet’s business theme (from `PLANET_THEMES`) and how the current sign shapes it.
6. **Element modulation:** One sentence describing how the element influences operations or sentiment.
7. **Modality modulation:** One sentence explaining cadence/tempo effects driven by the modality.

Bulleted formatting will aid readability, e.g.

```
• Sign: Libra ♎ — Cardinal Air
• Element: Air 🜁 (Yellow) — accelerates information-sharing and alignment.
• Modality: Cardinal ▲ — primes rapid decision cycles.
• Business impact: The Sun (executive vision) in Libra sponsors consensus-building leadership.
• Element focus: Air emphasizes narrative clarity and multi-channel messaging.
• Modality focus: Cardinal energy demands a 72-hour action window to keep momentum.
```

## Acceptance Criteria
- Summaries follow the pattern `<|☉ □ ♆]` (sign framing + compact aspect notation) with ASCII equivalent `<| Sun □ Nep ]` when `--ascii-only` is active.
- Descriptions retain triad guidance and include planet subsections with: sign emoji, elemental glyph/color, modality shape/bracket, and three tailored bullet points.
- Validator passes without modification or with minimal schema tweaks if new fields are introduced.
- Pilot ICS renders cleanly in Apple Calendar, Google Calendar, and Outlook (manual QA checklist item).

## Implementation touchpoints
- `daily_transit/zodiac_metadata.py`: expose Unicode + ASCII glyph lookups, color labels, and modulation snippets for reuse across builders.
- `daily_transit/ics_builder.py`: adopt compact summary format, inject planet subsections, and respect ASCII-only mode.
- `daily_transit/interpretations.py`: ensure interpretation results carry any new summary/description fragments needed by the builder.
- `tools/validate_business_dicts.py`: update schema if additional description fields require validation.
- Tests under `tests/test_ics_builder.py`: expand assertions for the new summary format and appended detail blocks.

## Open Questions
- Do we need localization toggles for color emojis in clients that render monochrome? (Assumed out of scope for this pass.)
- Should elemental color cues be optional via CLI flag? (Deferred until stakeholder feedback.)

## Implementation Notes (2025-10-03)
- `daily_transit/zodiac_metadata.py` centralises sign metadata, framing glyphs, and business-tone snippets for reuse.
- `daily_transit/ics_builder.py` now renders framed summaries (e.g. `< ☉ ☌ ♆ >`) and appends planet profile bullet blocks with ASCII-aware fallbacks.
- Aspect event builders accept precomputed zodiac context, enabling upstream caching while keeping legacy call sites compatible.
- `DailyTransitAspectCalendarGenerator.py` caches zodiac context per event timestamp to avoid redundant Skyfield longitude lookups during ICS assembly.
- Pilot calendar generated: `output/zodiac_week_2025-10-03_to_2025-10-09.ics` (business mode, with lunar phases) for cross-client smoke checks.
- Full-year deliverables: `output/zodiac_year_2025.ics` and `output/zodiac_year_2026.ics` exported with zodiac-rich formatting for stakeholder rollout.
- Validation suite: `tests/test_ics_builder.py`, `python tools/validate_business_dicts.py`, and `python -m compileall daily_transit` all pass as of 2025-10-03.

## Performance Snapshot
- Benchmark: 2025-10-03 → 2025-10-09 run (business mode, daily summaries + lunar phases) completed in **818.70 s real** on project workstation (Linux, zsh). Peak RSS ~52 KB reported by shell.
- Primary cost driver remains `daily_transit/aspect_detection.detect_aspects` due to per-pair Skyfield sampling and second-level refinement; ICS formatting overhead is negligible after caching.
- Potential follow-ups:
  - Vectorise Skyfield observations or reuse detection-phase longitude data.
  - Replace one-second brute force in `refine_exact_time` with a root-finding step to cut evaluations.
  - Expose CLI knobs for coarser sampling or reduced planet/aspect sets when rapid previews are acceptable.
