"""Executive-focused narratives for the business interpretation mode.

This module exposes triad-style guidance for each supported aspect alongside curated
planet pair insights. The goal is to deliver calendar copy that a business or finance
leader can scan quickly while still acting on concrete next steps.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

from astrological_dictionaries import astrological_aspects
from daily_transit.constants import DEFAULT_PLANETS

_MAJOR_ASPECTS = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

_ADDITIONAL_ENTITIES = ["North Node", "South Node", "Chiron"]

_REQUIRED_GUIDANCE_KEYS = ("severity", "headline", "impact", "action", "summary")
_OPTIONAL_GUIDANCE_KEYS = ("watch",)

PLANET_THEMES: Dict[str, str] = {
    "Sun": "executive vision",
    "Moon": "stakeholder sentiment",
    "Mercury": "information velocity",
    "Venus": "capital relationships",
    "Mars": "execution pressure",
    "Jupiter": "growth appetite",
    "Saturn": "governance discipline",
    "Uranus": "innovation disruption",
    "Neptune": "visionary narratives",
    "Pluto": "structural transformation",
    "North Node": "future strategy",
    "South Node": "legacy dependencies",
    "Chiron": "healing systemic gaps",
}


def all_business_planets() -> Tuple[str, ...]:
    """Return the planet/entity names expected in business copy dictionaries."""
    names = [name for name, _glyph in DEFAULT_PLANETS]
    for extra in _ADDITIONAL_ENTITIES:
        if extra not in names:
            names.append(extra)
    return tuple(names)


def _all_aspect_names() -> Iterable[str]:
    return sorted(astrological_aspects.get("aspect_degrees", {}).keys())


def _aspect_bucket(aspect: str) -> str:
    return "major_aspects" if aspect in _MAJOR_ASPECTS else "minor_aspects"


def _blank_entry() -> Dict[str, str]:
    entry = {key: "" for key in _REQUIRED_GUIDANCE_KEYS}
    entry.update({key: "" for key in _OPTIONAL_GUIDANCE_KEYS})
    return entry


def _build_guidance_template() -> Dict[str, Dict[str, Dict[str, str]]]:
    mapping: Dict[str, Dict[str, Dict[str, str]]] = {"major_aspects": {}, "minor_aspects": {}}
    for aspect in _all_aspect_names():
        mapping[_aspect_bucket(aspect)][aspect] = _blank_entry()
    return mapping


business_aspect_guidance: Dict[str, Dict[str, Dict[str, str]]] = _build_guidance_template()


# --- Major aspects ---------------------------------------------------------------------------

business_aspect_guidance["major_aspects"]["Conjunction"] = {
    "severity": "Opportunity",
    "headline": "Unified leadership mandate accelerates capital deployment.",
    "impact": "Decision latency collapses, letting teams fast-track launches and signalling confidence to investors.",
    "action": "COO & CFO: finalise approvals within 48 hours and codify guardrails before execution kicks off.",
    "watch": "Track cash burn versus plan; escalate if variance exceeds 3% this week.",
    "summary": "Opportunity — leadership alignment speeds funding; close approvals within 48h.",
}

business_aspect_guidance["major_aspects"]["Opposition"] = {
    "severity": "High Risk",
    "headline": "Competing agendas split the strategy narrative.",
    "impact": "Stakeholders hear mixed guidance, spiking volatility in sentiment and policy commitments.",
    "action": "Strategy lead: convene an alignment war room, publish a reconciled brief, and hedge exposures immediately.",
    "watch": "Monitor media and analyst sentiment; flag if net score stays negative for two sessions.",
    "summary": "High Risk — duelling mandates unsettle markets; drive alignment fast.",
}

business_aspect_guidance["major_aspects"]["Trine"] = {
    "severity": "Opportunity",
    "headline": "Frictionless collaboration unlocks compounding wins.",
    "impact": "Critical workflows move effortlessly, improving margin leverage and client satisfaction.",
    "action": "BizOps: scale proven playbooks and expand share-of-wallet initiatives this cycle.",
    "watch": "Track throughput and NPS for sustained lift, reinvesting gains selectively.",
    "summary": "Opportunity — smooth collaboration boosts throughput; scale proven plays.",
}

business_aspect_guidance["major_aspects"]["Square"] = {
    "severity": "High Risk",
    "headline": "Operational friction exposes vulnerable choke points.",
    "impact": "Bottlenecks force trade-offs that invite delivery delays and cost overruns.",
    "action": "Program management: trigger the contingency squad, reprioritise backlog, and reset SLAs within 24 hours.",
    "watch": "Monitor incident volume and backlog burn; escalate if slippage tops 10%.",
    "summary": "High Risk — friction threatens delivery; mobilise contingencies now.",
}

business_aspect_guidance["major_aspects"]["Sextile"] = {
    "severity": "Opportunity",
    "headline": "Targeted partnerships offer quick upside.",
    "impact": "Agile teams can capture incremental revenue or sourcing advantages with contained risk.",
    "action": "Corp dev: launch the pilot, attach crisp metrics, and schedule a 10-day results review.",
    "watch": "Track lead conversion or supplier fill rates to confirm momentum.",
    "summary": "Opportunity — nimble partnership window; launch pilot with tight metrics.",
}


# --- Minor aspects ----------------------------------------------------------------------------

business_aspect_guidance["minor_aspects"]["Semisextile"] = {
    "severity": "Watch",
    "headline": "Peripheral teams surface weak signals that need coordination.",
    "impact": "Small disconnects can erode momentum and create customer friction if ignored.",
    "action": "Functional leads: host a 48-hour sync to rebalance ownership and expectations.",
    "watch": "Monitor SLA variance and frontline sentiment for emerging irritants.",
    "summary": "Watch — subtle misalignments emerging; schedule a fast cross-functional sync.",
}

business_aspect_guidance["minor_aspects"]["Quincunx"] = {
    "severity": "Watch",
    "headline": "Disconnected workflows collide and force redesign.",
    "impact": "Cross-department friction risks dragging schedules and confusing stakeholders.",
    "action": "Operating committee: map overlaps, retire redundancies, and enforce a new playbook this week.",
    "watch": "Track handoff errors and rework hours to verify alignment.",
    "summary": "Watch — clashing workflows demand process redesign now.",
}

business_aspect_guidance["minor_aspects"]["Semisquare"] = {
    "severity": "Watch",
    "headline": "Hidden bottlenecks hint at upcoming delays.",
    "impact": "Minor constraints compound quickly into schedule slips and client escalations.",
    "action": "PMO: escalate blockers, reinforce QA gates, and reset expectations within 24 hours.",
    "watch": "Inspect backlog ageing and defect counts daily.",
    "summary": "Watch — bottlenecks emerging; escalate blockers immediately.",
}

business_aspect_guidance["minor_aspects"]["Sesquiquadrate"] = {
    "severity": "High Risk",
    "headline": "Residual tension from old decisions resurfaces.",
    "impact": "Lagging indicators worsen before stabilising, shaking stakeholder confidence.",
    "action": "Steering group: deploy remediation, close feedback loops, and publish progress checkpoints.",
    "watch": "Monitor churn or attrition metrics for improvement inside two weeks.",
    "summary": "High Risk — legacy friction back on deck; execute the remediation plan.",
}

business_aspect_guidance["minor_aspects"]["Quintile"] = {
    "severity": "Opportunity",
    "headline": "Breakthrough creativity can differentiate the offering.",
    "impact": "Innovation spikes lift brand equity and enable premium pricing.",
    "action": "Product & marketing: fund prototypes, amplify thought leadership, and measure response.",
    "watch": "Track engagement and premium conversion metrics through the sprint.",
    "summary": "Opportunity — creative edge emerging; invest in standout concepts.",
}

business_aspect_guidance["minor_aspects"]["Biquintile"] = {
    "severity": "Opportunity",
    "headline": "Mastery in niche domains commands premium attention.",
    "impact": "Specialist segments outperform, driving sustainable margin expansion.",
    "action": "GM: scale high-margin services, protect IP, and document repeatable methods.",
    "watch": "Monitor utilisation and margin lift across expert lines.",
    "summary": "Opportunity — niche mastery gaining traction; codify and scale.",
}

business_aspect_guidance["minor_aspects"]["Septile"] = {
    "severity": "Watch",
    "headline": "Intuitive leaps challenge the data narrative.",
    "impact": "Markets defy models, increasing reliance on qualitative judgement.",
    "action": "Risk & research: blend qualitative intel with guardrails and keep optionality open.",
    "watch": "Track forecast-to-actual variance and adjust hedges swiftly.",
    "summary": "Watch — intuition outpaces models; balance gut calls with hedges.",
}

business_aspect_guidance["minor_aspects"]["Biseptile"] = {
    "severity": "Watch",
    "headline": "Long-cycle themes resurface, hinting at structural shifts.",
    "impact": "Sentiment sways on elusive drivers, pressuring long-duration holdings.",
    "action": "Portfolio leads: revisit decade-long theses and document revised scenarios.",
    "watch": "Monitor macro narrative trackers and long-term yields.",
    "summary": "Watch — deep-cycle narratives resurfacing; refresh strategic theses.",
}

business_aspect_guidance["minor_aspects"]["Triseptile"] = {
    "severity": "Opportunity",
    "headline": "Transformative insight pushes beyond the current model.",
    "impact": "Volatility may precede breakthroughs as teams chase destiny-level moves.",
    "action": "Executive sponsors: resource visionary bets, ring-fence cash, and pace communications.",
    "watch": "Track liquidity runway and change adoption sentiment weekly.",
    "summary": "Opportunity — transformative pivot forming; resource boldly and pace change.",
}

business_aspect_guidance["minor_aspects"]["Novile"] = {
    "severity": "Watch",
    "headline": "Closing chapters free capacity for the next play.",
    "impact": "Growth plateaus while stakeholders expect clarity on the sequel.",
    "action": "Leads: run retros, harvest learnings, and outline successor initiatives inside the fortnight.",
    "watch": "Monitor renewal and upsell signals during the transition.",
    "summary": "Watch — cycle closing; package lessons and brief the next initiative.",
}

business_aspect_guidance["minor_aspects"]["Binovile"] = {
    "severity": "Opportunity",
    "headline": "Refinement cycles unlock upgrade momentum.",
    "impact": "Iterative improvements tighten variance and boost user confidence.",
    "action": "Product ops: schedule rapid feedback loops, iterate features, and recalibrate KPIs.",
    "watch": "Track adoption and variance spread to confirm improvement.",
    "summary": "Opportunity — refinement loop boosting quality; run rapid feedback cycles.",
}

business_aspect_guidance["minor_aspects"]["Quadranovile"] = {
    "severity": "Watch",
    "headline": "Late-cycle consolidation requires exit prep.",
    "impact": "Valuations stabilise as stakeholders negotiate renewal or exit terms.",
    "action": "Finance & legal: finalise succession, hedge residual risk, and document transfer steps.",
    "watch": "Watch deal pipeline and covenant triggers through quarter-end.",
    "summary": "Watch — consolidation phase; prepare exits and hedge residual risk.",
}

business_aspect_guidance["minor_aspects"]["Decile"] = {
    "severity": "Opportunity",
    "headline": "Precision execution improves margins.",
    "impact": "Disciplined cadence enhances operating leverage while keeping teams focused.",
    "action": "Ops: lock crisp OKRs, review leading indicators weekly, and celebrate small wins.",
    "watch": "Monitor KPI dashboards for sustained micro gains.",
    "summary": "Opportunity — precision execution paying off; maintain tight cadence.",
}

business_aspect_guidance["minor_aspects"]["Tredecile"] = {
    "severity": "Opportunity",
    "headline": "Bold storytelling elevates market presence.",
    "impact": "Experiential campaigns drive engagement and premium demand.",
    "action": "Marketing: launch standout activations, partner with tastemakers, and measure experiential ROI.",
    "watch": "Track sentiment lift and premium conversion in the campaign window.",
    "summary": "Opportunity — bold brand narrative resonating; invest in experiences.",
}

business_aspect_guidance["minor_aspects"]["Undecile"] = {
    "severity": "Watch",
    "headline": "Non-linear opportunities test planning discipline.",
    "impact": "Performance zigzags, drawing attention to contrarian plays.",
    "action": "Strategy: prototype alternate approaches, run skunkworks, and guard risk budgets.",
    "watch": "Monitor drawdown limits and scenario stress tests.",
    "summary": "Watch — zigzag performance; experiment carefully with tight risk.",
}

business_aspect_guidance["minor_aspects"]["Tridecile"] = {
    "severity": "Opportunity",
    "headline": "Cross-pollination sparks asymmetric upside.",
    "impact": "Shared insight drives adoption curves and reframes competitive edge.",
    "action": "Program leads: codify emergent playbooks, align incentives, and scale pilots deliberately.",
    "watch": "Track adoption slopes and resource constraints closely.",
    "summary": "Opportunity — cross-pollination scaling; codify and align incentives.",
}

business_aspect_guidance["minor_aspects"]["Quadraundecile"] = {
    "severity": "Watch",
    "headline": "Complex systems demand clarity.",
    "impact": "Information density risks decision fatigue and slower governance.",
    "action": "Leadership: invest in analytics automation and streamline review cadences.",
    "watch": "Monitor decision cycle times and information backlog.",
    "summary": "Watch — complexity climbing; automate analytics and simplify decisions.",
}

business_aspect_guidance["minor_aspects"]["Duodecile"] = {
    "severity": "Opportunity",
    "headline": "Fine-tuning yields incremental efficiency gains.",
    "impact": "Process control improves, shrinking variance and lifting margins.",
    "action": "Ops excellence: run lean audits, refresh SOPs, and lock in micro savings.",
    "watch": "Track control charts to ensure improvements persist.",
    "summary": "Opportunity — micro-optimisations working; sustain lean audits.",
}

business_aspect_guidance["minor_aspects"]["Quattuordecile"] = {
    "severity": "Watch",
    "headline": "Subtle resource shifts realign with demand.",
    "impact": "Portfolios rotate gently toward resilient assets.",
    "action": "Treasury: cue tactical reallocations, adjust coverage ratios, and brief desks.",
    "watch": "Monitor allocation drift and coverage metrics weekly.",
    "summary": "Watch — gentle rotation underway; rebalance tactically.",
}

business_aspect_guidance["minor_aspects"]["Vigintile"] = {
    "severity": "Opportunity",
    "headline": "Seed-stage demand signals surface.",
    "impact": "Early adopters hint at future growth even with low current volume.",
    "action": "Growth team: run low-cost experiments, gather signal intelligence, and pre-position optionality.",
    "watch": "Track qualitative feedback and pilot attribution closely.",
    "summary": "Opportunity — early demand flickers; test with low-cost experiments.",
}

business_aspect_guidance["minor_aspects"]["Quinvigintile"] = {
    "severity": "Opportunity",
    "headline": "Precision refinements unlock hidden profitability.",
    "impact": "Craftsmanship and analytics lift margins in focused lines.",
    "action": "Ops: deploy advanced analytics, reward precision, and enforce quality gates.",
    "watch": "Monitor margin delta on refined offerings.",
    "summary": "Opportunity — precision gains margins; enforce quality analytics.",
}

business_aspect_guidance["minor_aspects"]["Sesquiquintile"] = {
    "severity": "Opportunity",
    "headline": "Creative mastery drives premium scarcity.",
    "impact": "Brand equity surges as waitlists form and pricing power expands.",
    "action": "CX & revenue: protect exclusivity, calibrate pricing, and expand concierge touchpoints.",
    "watch": "Track waitlist depth and VIP satisfaction.",
    "summary": "Opportunity — premium demand surging; guard exclusivity and service.",
}

business_aspect_guidance["minor_aspects"]["Semi-Octile"] = {
    "severity": "Watch",
    "headline": "Tactical friction tests organisational agility.",
    "impact": "Intraday noise widens ranges and stresses approval cycles.",
    "action": "Trading & ops: tighten intraday limits, streamline sign-offs, and shorten turnaround.",
    "watch": "Monitor intraday volatility and cycle-time metrics.",
    "summary": "Watch — agility test underway; tighten limits and approvals.",
}

business_aspect_guidance["minor_aspects"]["Sesqui-Octile"] = {
    "severity": "High Risk",
    "headline": "Persistent tension demands course correction.",
    "impact": "Variance stays elevated, stretching stakeholder patience.",
    "action": "Leadership: deploy a tiger team, clarify escalation paths, and reassert accountability.",
    "watch": "Track issue reopen rate and stakeholder sentiment.",
    "summary": "High Risk — systemic drift persists; activate the corrective squad.",
}

business_aspect_guidance["minor_aspects"]["Septdecile"] = {
    "severity": "Watch",
    "headline": "Fractal patterns spotlight repeating risks.",
    "impact": "Algorithms adapt as investors detect self-similar stress points.",
    "action": "Data science: audit datasets, refresh models, and monitor for recurrent anomalies.",
    "watch": "Keep bias monitors and anomaly alerts on high sensitivity.",
    "summary": "Watch — repeating patterns emerging; refresh models and watch anomalies.",
}

business_aspect_guidance["minor_aspects"]["Semiduodecile"] = {
    "severity": "Watch",
    "headline": "Quiet rebalancing primes the next wave.",
    "impact": "Volatility smooths as systems reset baseline allocations.",
    "action": "Finance: tidy balance sheets, close low-value loops, and ready dry powder.",
    "watch": "Review liquidity ratios and working capital weekly.",
    "summary": "Watch — calm reset underway; tidy balance sheet and prep capital.",
}

business_aspect_guidance["minor_aspects"]["Septuagenary"] = {
    "severity": "Opportunity",
    "headline": "Long-horizon cycles invite strategic choreography.",
    "impact": "Patient capital gains advantage as macro signals blend.",
    "action": "Strategy board: align five- to seven-year plans, reinforce institutional knowledge, and invest in resilience.",
    "watch": "Monitor long-duration indicators and talent retention.",
    "summary": "Opportunity — long-cycle alignment; refresh 5–7 year playbooks.",
}


# --- Planet pair insights --------------------------------------------------------------------

def _pair_key(planet_a: str, planet_b: str) -> Tuple[str, str]:
    return tuple(sorted((planet_a, planet_b)))


def _build_pair_overrides() -> Dict[Tuple[str, str], str]:
    overrides: Dict[Tuple[str, str], str] = {}

    def add(planet_a: str, planet_b: str, text: str) -> None:
        overrides[_pair_key(planet_a, planet_b)] = text

    add("Sun", "Moon", "Synchronise leadership narrative with frontline sentiment; issue a daily 09:00 brief to avoid whiplash.")
    add("Sun", "Mercury", "Ensure executive messaging matches data releases; run rapid fact checks before announcements.")
    add("Sun", "Venus", "Align brand promise with capital deployment so spending decisions reinforce reputation.")
    add("Sun", "Mars", "Balance bold vision with execution bandwidth; stage deliverables to prevent burnout.")
    add("Sun", "Jupiter", "Frame growth story with disciplined milestones to reassure investors and boards.")
    add("Sun", "Saturn", "Translate ambition into accountable governance checkpoints with clear owners.")
    add("Sun", "Uranus", "Wrap innovation pushes in clear comms so disruption reads as intentional, not chaotic.")
    add("Sun", "Neptune", "Anchor visionary storytelling to verifiable progress metrics to protect credibility.")
    add("Sun", "Pluto", "Prepare leaders to message restructures transparently and manage power realignments.")

    add("Moon", "Mercury", "Route sentiment intel into communications loops within 12 hours to keep tone aligned.")
    add("Moon", "Venus", "Use customer mood shifts to fine-tune pricing and loyalty perks in real time.")
    add("Moon", "Mars", "Temper emotional spikes with paced execution and rotate frontline leads to avoid fatigue.")
    add("Moon", "Jupiter", "Convert optimism into campaigns without overpromising capacity or service levels.")
    add("Moon", "Saturn", "Provide morale support when governance requirements tighten to prevent disengagement.")
    add("Moon", "Uranus", "Prep change-management touchpoints ahead of disruptive rollouts to protect sentiment.")
    add("Moon", "Neptune", "Ground aspirational messaging in authentic sentiment to avoid hype fatigue.")
    add("Moon", "Pluto", "Handle trust-sensitive communications with depth and transparency during restructures.")

    add("Mercury", "Venus", "Sync deal messaging with relationship capital so sellers and finance tell the same story.")
    add("Mercury", "Mars", "Move fast but route tasks cleanly; disciplined playbooks prevent dropped details under pressure.")
    add("Mercury", "Jupiter", "Translate big-picture strategy into crisp talking points for investors and partners.")
    add("Mercury", "Saturn", "Audit every message for compliance and finalise language before regulator briefings.")
    add("Mercury", "Uranus", "Promote innovation narratives while pre-wiring risk disclosures with stakeholders.")
    add("Mercury", "Neptune", "Filter visionary spin through rigorous fact-checks to keep trust high.")
    add("Mercury", "Pluto", "Coordinate sensitive disclosures with transformation milestones to manage impact.")

    add("Venus", "Mars", "Balance relationship nurturing with assertive sales pushes to protect margins and goodwill.")
    add("Venus", "Jupiter", "Leverage goodwill to expand partnerships but validate return profiles before scaling.")
    add("Venus", "Saturn", "Tighten deal structures to guard margins while maintaining rapport.")
    add("Venus", "Uranus", "Bring finance and innovation together to price new models responsibly.")
    add("Venus", "Pluto", "Stress-test valuations as deep restructuring or M&A overtures reshape value stories.")

    add("Mars", "Jupiter", "Channel surge energy into scalable bets without overextending leverage or headcount.")
    add("Mars", "Saturn", "Temper aggressive timelines with governance guardrails and staged approvals.")
    add("Mars", "Uranus", "Plan contingencies before launching volatile innovations to shield operations.")
    add("Mars", "Neptune", "Clarify objectives so passionate pushes stay on mission and avoid drift.")
    add("Mars", "Pluto", "Direct intense drive into transformation programs with clear ethical oversight.")

    add("Jupiter", "Saturn", "Balance expansion with policy compliance; pace investments to pass regulatory muster.")
    add("Jupiter", "Uranus", "Frame frontier bets with scenario analyses to calm cautious capital.")
    add("Jupiter", "Neptune", "Ensure growth narratives rest on auditable numbers, not aspiration alone.")
    add("Jupiter", "Pluto", "Use expansion efforts to finance deeper restructures deliberately and transparently.")

    add("Saturn", "Uranus", "Pair disciplined governance with sandboxed experimentation to keep innovation safe.")
    add("Saturn", "Neptune", "Ground visionary promises in compliance-ready roadmaps and documentation.")
    add("Saturn", "Pluto", "Run restructures with governance transparency to preserve trust and continuity.")

    add("Uranus", "Neptune", "Translate disruptive visions into inspiring yet accountable storyboards for stakeholders.")
    add("Uranus", "Pluto", "Prepare for systemic shifts; align crisis playbooks with bold innovation leaps.")
    add("Neptune", "Pluto", "Couple transformational narratives with rigorous proof points and diligence paths.")

    add("North Node", "South Node", "Balance future bets with legacy obligations so the story covers both runway and roots.")
    add("North Node", "Chiron", "Invest in growth while repairing cultural gaps that could derail execution.")
    add("South Node", "Chiron", "Retire stale practices compassionately to free capacity for healing and renewal.")

    return overrides


business_pair_overrides: Dict[Tuple[str, str], str] = _build_pair_overrides()


def default_pair_message(planet_a: str, planet_b: str) -> str:
    """Fallback interaction message when no curated insight exists."""
    theme_a = PLANET_THEMES.get(planet_a, planet_a.lower())
    theme_b = PLANET_THEMES.get(planet_b, planet_b.lower())
    return f"Balance {theme_a} with {theme_b} to keep the strategic posture coherent."


__all__ = [
    "PLANET_THEMES",
    "all_business_planets",
    "business_aspect_guidance",
    "business_pair_overrides",
    "default_pair_message",
]
