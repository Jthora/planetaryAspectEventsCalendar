# Business Interpretation Style Guide & Glossary

_Last updated: 2025-10-01_

## 1. Audience Snapshot
- **Primary readers:** Portfolio managers, corporate strategists, macro/quant analysts, risk officers.
- **Secondary readers:** Investor-relations teams, startup founders, industry analysts.

## 2. Voice & Tone
- Confident, insightful, and concise.
- Data-aware language (e.g., reference sentiment, liquidity, lead indicators).
- Neutral stance: acknowledge uncertainty, recommend monitoring rather than guaranteeing outcomes.
- Prefer active voice and decisive verbs: “anticipate,” “monitor,” “rebalance,” “tighten.”

## 3. Structure Expectations
Every interpretation assembled in business mode should fit the following pattern—each element is optional but recommended when relevant:

1. **Context** – Macro framing (market cycle, liquidity backdrop, credit conditions).
2. **Behavior** – Expected price action or volatility profile.
3. **Action** – Tactical suggestion (hedge, scale, rebalance, escalate due diligence).
4. **Planetary Context/Behavior/Action** – Sector associations or departmental themes per planet.
5. **Interaction Dynamics** – Pair-specific storyline (leadership conflict, innovation vs. regulation, etc.).

## 4. Writing Conventions
- Use present tense when describing energies; future tense only for forecasts.
- Avoid absolutes (never, always). Instead use “likely,” “potential,” “emerging.”
- Keep sentences under ~22 words when possible; make liberal use of commas for scan-ability.
- Capitalise astrological entities (Sun, Mars) and business nouns only when proper (Federal Reserve, PMI).
- Include time-horizon cues when possible ("near-term," "through the quarter," "over the next cycle").
- Highlight risk/reward with descriptors: "defensive," "risk-on," "liquidity drain," "capex-heavy." 

## 5. Glossary & Preferred Terms
| Term | Definition / Usage Notes |
|------|--------------------------|
| **Liquidity** | Depth and availability of cash/credit; mention when flows tighten/loosen. |
| **Risk posture** | Overall willingness to take on market or operational risk. |
| **Volatility** | Use for expected price variability; specify "intraday", "medium-term" when possible. |
| **Sentiment** | Market mood; refer to bullish/bearish/neutral. |
| **Leadership cadence** | The speed/clarity of executive decision making. |
| **Capital deployment** | Investment of cash reserves; good phrase for Venus/Jupiter aspects. |
| **Operational throughput** | Production/output capability; often tied to Mars/Saturn. |
| **Innovation runway** | Window for R&D or disruptive change; use with Uranus, Mercury. |
| **Regulatory focus** | Compliance pressures; tie to Saturn/Pluto interactions. |
| **Hedging** | Risk reduction (fiscal or market). Use verbs: “refresh hedges,” “scale hedges.” |

## 6. Compliance Considerations
- No promises of returns; keep language advisory ("consider," "monitor").
- No personalised financial advice; keep insights broad and sector/strategy oriented.
- Flag uncertainty or monitoring actions whenever volatility/ambiguity is high.

## 7. Examples
**Example Aspect (Conjunction - Sun & Jupiter):**
- Context: “Executive optimism aligns with expansionary policy cues; capital availability improves.”
- Behavior: “Momentum accelerates in growth sectors with a risk-on bias.”
- Action: “Reassess expansion budgets and ensure governance keeps pace with scaling.”
- Interaction: “Sun & Jupiter: Align leadership narrative with investor appetite for growth.”

**Example Planet Context (Saturn):**
- Context: “Highlights obligations, governance, and regulatory guardrails.”
- Behavior: “Decision cycles slow as diligence requirements tighten.”
- Action: “Schedule compliance reviews and confirm contingency budgets.”

## 8. Submission Workflow
1. Draft interpretations in the shared spreadsheet, using dedicated columns per dictionary (Context, Behavior, Action, Planet Context, etc.).
2. Run `python tools/export_aspect_keys.py --format json` to confirm coverage list.
3. Once a bulk batch is ready, convert into Python-friendly strings (double quotes, escaped apostrophes) and commit updates to `astrological_business_dictionaries.py`.
4. Before committing, run `python tools/validate_business_dicts.py --strict` to ensure no placeholders or "TODO" remain for touched sections.
5. Update the progress tracker (`progress-tracker.md`) with new status and notes.

## 9. Review Checklist
- [ ] Does each entry follow the context/behavior/action structure?
- [ ] Is the language free from absolutes and compliance risk?
- [ ] Are risk signals and time horizons clearly communicated?
- [ ] Are planet/sector associations consistent with the glossary?
- [ ] Have validation scripts been executed with clean output?

Maintaining consistency here ensures business users receive actionable, trustworthy insights that complement the existing interpretations.
