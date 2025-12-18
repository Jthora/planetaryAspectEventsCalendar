# Executive-Focused Calendar Copy Improvements

## 1. Audience Context
- **Who:** Portfolio managers, CFOs, operations strategists, and trading leads.
- **Need:** Quickly scan daily calendar alerts to gauge opportunity vs. risk, align teams, and trigger timely actions.
- **Pain Points Noted:** Lengthy entries, repeated boilerplate, unclear priority, and minimal sector/metric guidance.

## 2. Observed Issues in Current Business Mode Output
- **Overly Dense Entries:** Calendar descriptions span 8–10 sentences with multiple sections.
- **Repetition Fatigue:** Identical planet context/behavior/action blurbs appear in every event.
- **Action Ambiguity:** Recommendations lack priority cues, owners, and time horizons.
- **Daily Summary Overload:** "Exact Aspects Today" uses full sentences, reducing glanceability.
- **Generic Pair Dynamics:** Interaction lines feel templated instead of situationally precise.

## 3. Improvement Principles
1. **Brevity with Impact:** Lead with a concise headline (<140 chars) that captures opportunity or risk.
2. **Executive Triad Template:** Structure each event as:
   - `Headline:` One sentence, tagged with opportunity/risk level.
   - `Why it matters:` One sentence referencing business impact or KPI.
   - `Action:` One sentence naming owner/timeframe.
   Optional: `Watch:` bullet with key indicators.
3. **Unique Pair Insights:** Craft bespoke interaction notes per major planet pair groupings.
4. **Daily Summary Summary:** Provide short, distinct blurbs (≤100 chars) for the "Exact Aspects Today" list.
5. **Sector & Metric Hooks:** Mention relevant industries, capital flows, or KPIs.
6. **Priority Signals:** Use badges (e.g., `[High Risk]`, `[Opportunity]`) for instant triage.

## 4. Workstreams & Deliverables
- **Template Revision:** Update ICS builder to render the triad format with severity badges.
- **Dictionary Refresh:** Split planet context into reusable background docs and unique interaction snippets.
- **Summary Formatter:** Introduce a compact sentence generator for daily summaries.
- **Metrics Glossary:** Map planets/aspects to suggested KPIs or sector tags for quick inserts.
- **QA Loop:** Pilot rewritten copy for a representative week; gather executive feedback.

## 5. Measurement of Success
- Calendar alerts readable inside mobile notification previews.
- Distinct action items for each event with explicit time horizon.
- Reduced copy-paste perception (≥80% of interaction notes unique).
- Stakeholder satisfaction captured via post-launch survey or qualitative interviews.

## 6. Next Steps Snapshot
1. Approve triad template and severity tagging conventions.
2. Prioritize top 20 aspect+planet pairs for bespoke rewrites.
3. Prototype concise summary strings and validate formatting in ICS clients.
4. Update validation tooling to enforce non-empty `headline`, `impact`, `action`, and `watch` fields.
