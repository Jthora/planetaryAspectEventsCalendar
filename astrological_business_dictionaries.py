"""Business-focused interpretation scaffolding for planetary aspect exports.

This module mirrors the structures consumed by ``daily_transit.interpretations`` and
ships with placeholder entries so content authors can fill them incrementally.

The goal is to keep the standard interpretations untouched while providing a
parallel data source for the ``business`` interpretation mode.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from astrological_dictionaries import astrological_aspects
from daily_transit.constants import DEFAULT_PLANETS

# Major aspects recognised by the generator when ``--aspects=major``
_MAJOR_ASPECT_NAMES = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

# Additional celestial entities frequently referenced in market analysis
_ADDITIONAL_ENTITIES = [
    "North Node",
    "South Node",
    "Chiron",
]

_PLACEHOLDER = ""

PLANET_THEMES: Dict[str, str] = {
    "Sun": "leadership alignment",
    "Moon": "sentiment management",
    "Mercury": "information velocity",
    "Venus": "capital relationships",
    "Mars": "execution pressure",
    "Jupiter": "growth appetite",
    "Saturn": "governance discipline",
    "Uranus": "innovation disruption",
    "Neptune": "visionary narratives",
    "Pluto": "structural transformation",
    "North Node": "strategic future bets",
    "South Node": "legacy dependencies",
    "Chiron": "healing of systemic gaps",
}


def _all_aspect_names() -> Iterable[str]:
    return astrological_aspects.get("aspect_degrees", {}).keys()


def _all_planet_names() -> List[str]:
    names = [name for name, _glyph in DEFAULT_PLANETS]
    for extra in _ADDITIONAL_ENTITIES:
        if extra not in names:
            names.append(extra)
    return names


def _build_aspect_mapping() -> Dict[str, Dict[str, str]]:
    mapping = {"major_aspects": {}, "minor_aspects": {}}
    for aspect_name in sorted(_all_aspect_names()):
        bucket = "major_aspects" if aspect_name in _MAJOR_ASPECT_NAMES else "minor_aspects"
        mapping[bucket][aspect_name] = _PLACEHOLDER
    return mapping


def _build_planet_mapping() -> Dict[str, str]:
    return {name: _PLACEHOLDER for name in _all_planet_names()}


def _build_planet_pair_mapping() -> Dict[str, Dict[str, str]]:
    names = _all_planet_names()
    pair_map: Dict[str, Dict[str, str]] = {name: {} for name in names}
    for i, primary in enumerate(names):
        for secondary in names[i + 1 :]:
            theme_primary = PLANET_THEMES.get(primary, "complementary influence")
            theme_secondary = PLANET_THEMES.get(secondary, "complementary influence")
            message = (
                f"Balance {theme_primary} with {theme_secondary} to keep strategic posture coherent."
            )
            pair_map[primary][secondary] = message
            pair_map[secondary][primary] = message
    return pair_map


business_aspect_context: Dict[str, Dict[str, str]] = _build_aspect_mapping()
business_aspect_behavior: Dict[str, Dict[str, str]] = _build_aspect_mapping()
business_aspect_action: Dict[str, Dict[str, str]] = _build_aspect_mapping()

business_planet_context: Dict[str, str] = _build_planet_mapping()
business_planet_behavior: Dict[str, str] = _build_planet_mapping()
business_planet_action: Dict[str, str] = _build_planet_mapping()

business_planet_interactions: Dict[str, Dict[str, str]] = _build_planet_pair_mapping()


# --- Curated business interpretations ---------------------------------------------------------

# Major aspect narratives
business_aspect_context["major_aspects"]["Conjunction"] = (
    "Leadership agendas and capital stewards align, creating unified messaging and faster budget approvals."
)
business_aspect_behavior["major_aspects"]["Conjunction"] = (
    "Expect decisive pivots or accelerated project launches as decision cycles compress."
)
business_aspect_action["major_aspects"]["Conjunction"] = (
    "Lock in approvals, formalize accountability, and document guardrails before momentum outruns controls."
)

business_aspect_context["major_aspects"]["Opposition"] = (
    "Strategic priorities polarize between stakeholders, revealing tension between growth and risk containment."
)
business_aspect_behavior["major_aspects"]["Opposition"] = (
    "Price action oscillates as competing narratives gain airtime, heightening headline-driven volatility."
)
business_aspect_action["major_aspects"]["Opposition"] = (
    "Facilitate alignment workshops, stress-test scenarios, and hedge asymmetric exposures."
)

business_aspect_context["major_aspects"]["Trine"] = (
    "Complementary teams exchange insights easily, supporting workflow efficiency and client confidence."
)
business_aspect_behavior["major_aspects"]["Trine"] = (
    "Steady momentum develops with low friction, favouring compounding gains in core franchises."
)
business_aspect_action["major_aspects"]["Trine"] = (
    "Scale proven initiatives, refresh success metrics, and capture incremental share while conditions remain smooth."
)

business_aspect_context["major_aspects"]["Square"] = (
    "Execution hurdles surface, forcing trade-offs between speed, quality, and resource allocation."
)
business_aspect_behavior["major_aspects"]["Square"] = (
    "Markets price in friction; volatility spikes around chokepoints or missed milestones."
)
business_aspect_action["major_aspects"]["Square"] = (
    "Reprioritize backlogs, mobilize contingency teams, and adjust risk buffers before pressure escalates."
)

business_aspect_context["major_aspects"]["Sextile"] = (
    "Opportunistic partnerships, supplier openings, or niche markets emerge with reasonable entry costs."
)
business_aspect_behavior["major_aspects"]["Sextile"] = (
    "Incremental upside appears for agile players; returns favour those who engage proactively."
)
business_aspect_action["major_aspects"]["Sextile"] = (
    "Pilot collaborations, allocate exploratory capital, and set clear success triggers for expansion."
)

# Minor aspect narratives
business_aspect_context["minor_aspects"]["Semisextile"] = (
    "Peripheral signals demand attention as adjacent functions surface latent synergies or frictions."
)
business_aspect_behavior["minor_aspects"]["Semisextile"] = (
    "Momentum drifts; slight misalignments create micro-volatility in niche segments."
)
business_aspect_action["minor_aspects"]["Semisextile"] = (
    "Host cross-functional stand-ups and recalibrate SLAs before irritants scale."
)

business_aspect_context["minor_aspects"]["Quincunx"] = (
    "Unrelated departments collide, forcing redesign of workflows or incentive models."
)
business_aspect_behavior["minor_aspects"]["Quincunx"] = (
    "Results look noisy as teams iterate; investors readjust expectations mid-cycle."
)
business_aspect_action["minor_aspects"]["Quincunx"] = (
    "Run alignment diagnostics, sunset redundant tasks, and reset success criteria."
)

business_aspect_context["minor_aspects"]["Semisquare"] = (
    "Hidden bottlenecks emerge, nudging project timelines and resource buffers."
)
business_aspect_behavior["minor_aspects"]["Semisquare"] = (
    "Pockets of volatility flare in operations tied to execution risk."
)
business_aspect_action["minor_aspects"]["Semisquare"] = (
    "Escalate blockers early, reinforce QA, and brief stakeholders on contingency thresholds."
)

business_aspect_context["minor_aspects"]["Sesquiquadrate"] = (
    "Scaled tension from prior decisions resurfaces, demanding methodical remediation."
)
business_aspect_behavior["minor_aspects"]["Sesquiquadrate"] = (
    "Lagging indicators worsen before improving; sentiment wavers."
)
business_aspect_action["minor_aspects"]["Sesquiquadrate"] = (
    "Stabilize processes, close feedback loops, and formalize corrective playbooks."
)

business_aspect_context["minor_aspects"]["Quintile"] = (
    "Creative breakthroughs deliver competitive differentiation and brand lift."
)
business_aspect_behavior["minor_aspects"]["Quintile"] = (
    "Innovation output spikes; markets reward unique IP and design thinking."
)
business_aspect_action["minor_aspects"]["Quintile"] = (
    "Fund prototypes, promote thought leadership, and capture first-mover advantages."
)

business_aspect_context["minor_aspects"]["Biquintile"] = (
    "Refined mastery turns niche expertise into premium offerings."
)
business_aspect_behavior["minor_aspects"]["Biquintile"] = (
    "Performance metrics show consistent outperformance in specialist segments."
)
business_aspect_action["minor_aspects"]["Biquintile"] = (
    "Scale high-margin services, protect IP, and codify best practices for replication."
)

business_aspect_context["minor_aspects"]["Septile"] = (
    "Intuitive insights challenge models; strategic luck factors into planning."
)
business_aspect_behavior["minor_aspects"]["Septile"] = (
    "Price action defies historical correlations; outliers emerge."
)
business_aspect_action["minor_aspects"]["Septile"] = (
    "Blend qualitative intel with quantitative guardrails and keep optionality open."
)

business_aspect_context["minor_aspects"]["Biseptile"] = (
    "Deep-cycle themes reappear, hinting at karmic business narratives or long-tail risks."
)
business_aspect_behavior["minor_aspects"]["Biseptile"] = (
    "Elusive drivers sway sentiment; long-duration trades recalibrate."
)
business_aspect_action["minor_aspects"]["Biseptile"] = (
    "Track macro story arcs, revisit decade-long portfolios, and document scenario plans."
)

business_aspect_context["minor_aspects"]["Triseptile"] = (
    "Transformative insight pushes organizations to transcend prior operating models."
)
business_aspect_behavior["minor_aspects"]["Triseptile"] = (
    "Markets price in destiny-level moves; volatility may precede breakthroughs."
)
business_aspect_action["minor_aspects"]["Triseptile"] = (
    "Invest in visionary leadership, safeguard cash, and nurture long-horizon bets."
)

business_aspect_context["minor_aspects"]["Novile"] = (
    "Cycle completion cues prompt closing chapters and harvest of learnings."
)
business_aspect_behavior["minor_aspects"]["Novile"] = (
    "Growth rates plateau; stakeholders seek clarity on next act."
)
business_aspect_action["minor_aspects"]["Novile"] = (
    "Prepare retrospective briefings, crystallize insights, and define successor initiatives."
)

business_aspect_context["minor_aspects"]["Binovile"] = (
    "Momentum doubles back for refinement, encouraging upgrade cycles."
)
business_aspect_behavior["minor_aspects"]["Binovile"] = (
    "Metrics oscillate as improvements bed in; variance narrows over time."
)
business_aspect_action["minor_aspects"]["Binovile"] = (
    "Iterate feature releases, capture user feedback, and recalibrate KPIs."
)

business_aspect_context["minor_aspects"]["Quadranovile"] = (
    "Late-stage cycle prompts consolidation and pre-exit positioning."
)
business_aspect_behavior["minor_aspects"]["Quadranovile"] = (
    "Valuations stabilize; stakeholders negotiate exit terms or renewal conditions."
)
business_aspect_action["minor_aspects"]["Quadranovile"] = (
    "Finalize succession plans, hedge residual risk, and archive institutional knowledge."
)

business_aspect_context["minor_aspects"]["Decile"] = (
    "Precision targeting of goals yields lean, high-focus operations."
)
business_aspect_behavior["minor_aspects"]["Decile"] = (
    "Teams show disciplined cadence; micro-optimizations enhance margins."
)
business_aspect_action["minor_aspects"]["Decile"] = (
    "Set crisp OKRs, monitor leading indicators weekly, and celebrate small wins."
)

business_aspect_context["minor_aspects"]["Tredecile"] = (
    "Ambitious creativity surfaces, blending artful branding with strategic storytelling."
)
business_aspect_behavior["minor_aspects"]["Tredecile"] = (
    "Customer engagement metrics rise on emotional resonance and novelty."
)
business_aspect_action["minor_aspects"]["Tredecile"] = (
    "Launch bold campaigns, partner with tastemakers, and quantify experiential ROI."
)

business_aspect_context["minor_aspects"]["Undecile"] = (
    "Non-linear opportunities test orthodox planning frameworks."
)
business_aspect_behavior["minor_aspects"]["Undecile"] = (
    "Performance zigzags; contrarian plays attract niche capital."
)
business_aspect_action["minor_aspects"]["Undecile"] = (
    "Prototype alternative strategies, run skunkworks, and keep risk budgets tight."
)

business_aspect_context["minor_aspects"]["Tridecile"] = (
    "Advanced experimentation integrates unique insights across business units."
)
business_aspect_behavior["minor_aspects"]["Tridecile"] = (
    "Cross-pollination yields asymmetric upside; watch adoption curves."
)
business_aspect_action["minor_aspects"]["Tridecile"] = (
    "Codify emergent playbooks, align incentives, and scale pilots thoughtfully."
)

business_aspect_context["minor_aspects"]["Quadraundecile"] = (
    "Complex systems demand synthesis of multi-dimensional data sets."
)
business_aspect_behavior["minor_aspects"]["Quadraundecile"] = (
    "Decision fatigue looms as information density escalates."
)
business_aspect_action["minor_aspects"]["Quadraundecile"] = (
    "Invest in analytics automation, streamline governance, and prioritize clarity."
)

business_aspect_context["minor_aspects"]["Duodecile"] = (
    "Fine-tuning operations delivers incremental efficiency gains."
)
business_aspect_behavior["minor_aspects"]["Duodecile"] = (
    "Variance shrinks; process control metrics improve."
)
business_aspect_action["minor_aspects"]["Duodecile"] = (
    "Apply lean audits, recalibrate SOPs, and lock in micro savings."
)

business_aspect_context["minor_aspects"]["Quattuordecile"] = (
    "Subtle rebalancing aligns resources with evolving demand signals."
)
business_aspect_behavior["minor_aspects"]["Quattuordecile"] = (
    "Portfolios experience mild rotations toward resilient assets."
)
business_aspect_action["minor_aspects"]["Quattuordecile"] = (
    "Cue tactical reallocations, adjust coverage ratios, and brief treasury teams."
)

business_aspect_context["minor_aspects"]["Vigintile"] = (
    "Micro-inflection points hint at seeds of future demand."
)
business_aspect_behavior["minor_aspects"]["Vigintile"] = (
    "Early adopters respond; volume remains low but directionally meaningful."
)
business_aspect_action["minor_aspects"]["Vigintile"] = (
    "Run low-cost experiments, gather signal intelligence, and pre-position optionality."
)

business_aspect_context["minor_aspects"]["Quinvigintile"] = (
    "Hyper-specific refinements unlock hidden profitability levers."
)
business_aspect_behavior["minor_aspects"]["Quinvigintile"] = (
    "Margins tick higher where precision execution is sustained."
)
business_aspect_action["minor_aspects"]["Quinvigintile"] = (
    "Deploy advanced analytics, reward craftsmanship, and maintain quality controls."
)

business_aspect_context["minor_aspects"]["Sesquiquintile"] = (
    "Creative mastery erupts, elevating premium offerings to iconic status."
)
business_aspect_behavior["minor_aspects"]["Sesquiquintile"] = (
    "Brand equity surges; waitlists and scarcity dynamics appear."
)
business_aspect_action["minor_aspects"]["Sesquiquintile"] = (
    "Protect exclusivity, calibrate pricing models, and expand concierge touchpoints."
)

business_aspect_context["minor_aspects"]["Semi-Octile"] = (
    "Minor frictions nudge tactical pivots, highlighting agility tests."
)
business_aspect_behavior["minor_aspects"]["Semi-Octile"] = (
    "Short-term noise increases; intraday ranges widen modestly."
)
business_aspect_action["minor_aspects"]["Semi-Octile"] = (
    "Tighten intraday risk limits, streamline approvals, and reduce turnaround times."
)

business_aspect_context["minor_aspects"]["Sesqui-Octile"] = (
    "Secondary tensions require mid-course corrections to avoid compounding drift."
)
business_aspect_behavior["minor_aspects"]["Sesqui-Octile"] = (
    "Persistent variance keeps stakeholders vigilant; patience thins."
)
business_aspect_action["minor_aspects"]["Sesqui-Octile"] = (
    "Deploy tiger teams, clarify escalation paths, and reaffirm accountability."
)

business_aspect_context["minor_aspects"]["Septdecile"] = (
    "Fractal patterns reveal repeating lessons within complex markets."
)
business_aspect_behavior["minor_aspects"]["Septdecile"] = (
    "Investors re-examine fractal signals; algorithms adapt weighting schemes."
)
business_aspect_action["minor_aspects"]["Septdecile"] = (
    "Audit datasets, refresh models, and monitor for self-similar stress points."
)

business_aspect_context["minor_aspects"]["Semiduodecile"] = (
    "Minor rebalancing primes systems for the next major wave."
)
business_aspect_behavior["minor_aspects"]["Semiduodecile"] = (
    "Quiet recalibration smooths volatility across operations."
)
business_aspect_action["minor_aspects"]["Semiduodecile"] = (
    "Tidy balance sheets, close low-value loops, and prep capital for redeployment."
)

business_aspect_context["minor_aspects"]["Septuagenary"] = (
    "Long-horizon cycles interlock, inviting advanced strategic choreography."
)
business_aspect_behavior["minor_aspects"]["Septuagenary"] = (
    "Macro signals mix; patient capital gains edge over short-term trades."
)
business_aspect_action["minor_aspects"]["Septuagenary"] = (
    "Align 5- to 7-year plans, steward institutional knowledge, and reinforce resilience."
)

# Planetary narratives (initial coverage for core bodies)
business_planet_context.update(
    {
        "Sun": "Executive vision, brand narrative, and flagship KPIs.",
        "Moon": "Stakeholder sentiment, workforce morale, and customer churn signals.",
        "Mercury": "Information flow, market data, and deal pipeline velocity.",
        "Venus": "Capital deployment, pricing power, and relationship equity.",
        "Mars": "Operational throughput, competitive drive, and crisis response speed.",
        "Jupiter": "Expansion capital, policy backdrop, and strategic partnerships.",
        "Saturn": "Governance, regulatory compliance, and structural constraints.",
    }
)

business_planet_behavior.update(
    {
        "Sun": "Narratives set from the top cascade quickly, influencing analyst guidance.",
        "Moon": "Sentiment swings faster than fundamentals, amplifying short-term volatility.",
        "Mercury": "Negotiations, filings, and announcements accelerate; miscommunication risk rises.",
        "Venus": "Valuation multiples flex as investors reassess perceived comfort and luxury demand.",
        "Mars": "Execution tempo rises; teams push capacity and accept higher short-term strain.",
        "Jupiter": "Optimism lifts growth sectors; leverage appetite increases across desks.",
        "Saturn": "Review cycles lengthen; watchdogs scrutinize assumptions and cost commitments.",
    }
)

business_planet_action.update(
    {
        "Sun": "Align leadership communications, refresh dashboards, and reaffirm mission-critical goals.",
        "Moon": "Survey sentiment, support retention initiatives, and recalibrate frontline messaging.",
        "Mercury": "Tighten disclosure protocols, double-check data integrity, and capture rapid feedback.",
        "Venus": "Negotiate supplier terms, refine loyalty programs, and audit cash-flow comfort.",
        "Mars": "Schedule downtime for critical assets, reinforce escalation paths, and monitor burnout.",
        "Jupiter": "Reevaluate expansion bets, structure smart leverage, and invest in scalable governance.",
        "Saturn": "Update compliance calendars, validate contingency reserves, and document risk overrides.",
        "Uranus": "Sponsor skunkworks, secure cybersecurity postures, and budget for surprise pivots.",
        "Neptune": "Clarify brand narratives, vet ESG claims, and align vision with deliverables.",
        "Pluto": "Prepare transformation offices, resource change management, and address power imbalances.",
        "North Node": "Incubate future bets, benchmark emerging sectors, and groom next-gen leaders.",
        "South Node": "Audit legacy portfolios, retire debt anchors, and upskill entrenched teams.",
        "Chiron": "Invest in coaching, repair stakeholder trust, and integrate lessons into policy.",
    }
)


business_planet_context.update(
    {
        "Uranus": "Disruption engines, R&D labs, and innovation capital.",
        "Neptune": "Vision, brand mythos, and intangible asset plays.",
        "Pluto": "Core restructuring, power consolidation, and deep due diligence.",
        "North Node": "Future strategy, market entry vectors, and aspirational KPIs.",
        "South Node": "Legacy systems, sunk cost narratives, and historical advantages.",
        "Chiron": "Organizational wounds, culture repair, and learning agendas.",
    }
)

business_planet_behavior.update(
    {
        "Uranus": "Volatility spikes around tech bets; new entrants unsettle incumbents.",
        "Neptune": "Narratives blur; diligence must filter speculation from signal.",
        "Pluto": "Intense power plays surface; restructures reshape sector maps.",
        "North Node": "Attention shifts to growth horizons; talent strategies evolve.",
        "South Node": "Legacy comfort invites complacency; competitive edges may erode.",
        "Chiron": "Old wounds trigger; productivity dips until remediation begins.",
    }
)


# Planet pair interaction highlights
business_planet_interactions["Sun"]["Moon"] = (
    "Synchronize executive messaging with real-time sentiment to prevent morale whiplash."
)
business_planet_interactions["Sun"]["Saturn"] = (
    "Leadership ambitions meet regulatory guardrails; communicate accountability and pacing."
)
business_planet_interactions["Mercury"]["Mars"] = (
    "Fast-moving negotiations demand disciplined playbooks to avoid operational misfires."
)
business_planet_interactions["Venus"]["Pluto"] = (
    "Value propositions undergo deep scrutiny; prepare for structural re-pricing or M&A overtures."
)
business_planet_interactions["Jupiter"]["Saturn"] = (
    "Balance expansion with governance; stress-test growth models against policy tightening."
)

__all__ = [
    "business_aspect_context",
    "business_aspect_behavior",
    "business_aspect_action",
    "business_planet_context",
    "business_planet_behavior",
    "business_planet_action",
    "business_planet_interactions",
]
