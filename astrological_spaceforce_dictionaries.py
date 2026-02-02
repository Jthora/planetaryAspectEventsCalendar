"""Space Force mission narratives for the dedicated interpretation mode.

This module mirrors the structure used by the business dictionaries so the
Daily Transit generator can deliver guardian-ready guidance without touching
core logic.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

from astrological_dictionaries import astrological_aspects
from daily_transit.constants import DEFAULT_PLANETS

_ALLOWED_SEVERITIES = {"Opportunity", "Watch", "High Risk", "Info"}
_MAJOR_ASPECTS = {
    "Conjunction",
    "Opposition",
    "Trine",
    "Square",
    "Sextile",
}

_ADDITIONAL_ENTITIES = ["North Node", "South Node", "Chiron"]

SPACEFORCE_PLANET_THEMES: Dict[str, str] = {
    "Sun": "command authority",
    "Moon": "crew morale telemetry",
    "Mercury": "intel routing",
    "Venus": "coalition harmony",
    "Mars": "tactical thrust",
    "Jupiter": "strategic reach",
    "Saturn": "doctrinal discipline",
    "Uranus": "autonomy experiments",
    "Neptune": "perception ops",
    "Pluto": "deep systems overhaul",
    "North Node": "future mission vector",
    "South Node": "legacy dependencies",
    "Chiron": "resilience rehab",
}


def all_spaceforce_planets() -> Tuple[str, ...]:
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
    return {
        "severity": "Info",
        "headline": "",
        "impact": "",
        "action": "",
        "watch": "",
        "summary": "",
    }


def _build_guidance_template() -> Dict[str, Dict[str, Dict[str, str]]]:
    mapping: Dict[str, Dict[str, Dict[str, str]]] = {"major_aspects": {}, "minor_aspects": {}}
    for aspect in _all_aspect_names():
        mapping[_aspect_bucket(aspect)][aspect] = _blank_entry()
    return mapping


spaceforce_aspect_guidance: Dict[str, Dict[str, Dict[str, str]]] = _build_guidance_template()


# --- Sample major aspect entries -------------------------------------------------------------

spaceforce_aspect_guidance["major_aspects"]["Conjunction"] = {
    "severity": "Opportunity",
    "headline": "Command vectors align and amplify mission beam.",
    "impact": "Unified leadership intent clears backlog and focuses every crew on the primary objective.",
    "action": "Issue a consolidated command brief within 12 hours and sync joint cells on priority sequencing.",
    "watch": "Monitor command-net latency; keep response time under 90 seconds.",
    "summary": "Opportunity — command unity boosts throughput; publish one mission brief.",
}

spaceforce_aspect_guidance["major_aspects"]["Opposition"] = {
    "severity": "High Risk",
    "headline": "Countervailing agendas split the ops floor.",
    "impact": "Mixed guidance threatens readiness and forces crews to guess intent, slowing sorties.",
    "action": "Stand up an alignment huddle this watch, assign adjudication authority, and freeze non-critical tasks.",
    "watch": "Track crew chatter and escalation volume for sustained turbulence.",
    "summary": "High Risk — intent split; convene adjudication huddle immediately.",
}

spaceforce_aspect_guidance["major_aspects"]["Trine"] = {
    "severity": "Opportunity",
    "headline": "Systems handshake cleanly and boost tempo.",
    "impact": "Comms, cyber, and orbital teams reinforce each other, enabling graceful surge capacity.",
    "action": "Exploit the window to clear deferred maintenance and authorize cross-mission drills.",
    "watch": "Verify telemetry health stays green as throughput ramps.",
    "summary": "Opportunity — seamless systems; schedule cross-mission drills.",
}

spaceforce_aspect_guidance["major_aspects"]["Square"] = {
    "severity": "High Risk",
    "headline": "Friction between crews exposes threat surface gaps.",
    "impact": "Conflicting tactics strain bandwidth and risk sensor blind spots.",
    "action": "Deploy a tiger team to map chokepoints, rebalance duties, and publish a revised battle rhythm within 24 hours.",
    "watch": "Watch for packet loss or telemetry drops around contested nodes.",
    "summary": "High Risk — chokepoints forming; deploy tiger team now.",
}

spaceforce_aspect_guidance["major_aspects"]["Sextile"] = {
    "severity": "Opportunity",
    "headline": "Targeted alliances unlock fast assists.",
    "impact": "Allied assets are willing to share bandwidth or ISR for limited windows.",
    "action": "Task liaison officers to broker a 72-hour support package and capture metrics for follow-on agreements.",
    "watch": "Monitor coalition comms windows for slippage.",
    "summary": "Opportunity — allies ready to assist; broker 72h support package.",
}


# --- Planet pair insights --------------------------------------------------------------------

spaceforce_aspect_guidance["minor_aspects"]["Quincunx"] = {
    "severity": "Watch",
    "headline": "Disconnected mission threads rub and demand recalibration.",
    "impact": "Cross-squad tactics collide, risking telemetry drift and operator confusion.",
    "action": "Stand up a cross-mission sync within the next watch to reassign ownership and retune SOPs.",
    "watch": "Track handoff faults and duplicate tasking in the ops log.",
    "summary": "Watch — clashing threads; host a cross-mission sync next watch.",
}

spaceforce_aspect_guidance["minor_aspects"]["Semisextile"] = {
    "severity": "Watch",
    "headline": "Peripheral signals hint at creeping drift.",
    "impact": "Small variances in crew rhythm or sensor calibration can snowball into readiness drag.",
    "action": "Assign a duty officer to triage low-level anomalies within 12 hours and issue corrective notes.",
    "watch": "Monitor shift turnovers and minor alarm frequency for upticks.",
    "summary": "Watch — subtle drift emerging; triage anomalies within 12h.",
}

spaceforce_aspect_guidance["minor_aspects"]["Semisquare"] = {
    "severity": "Watch",
    "headline": "Latent friction stresses the battle rhythm.",
    "impact": "Micro-delays stack up, threatening launch windows or intel delivery.",
    "action": "Deploy a tiger cell to clear blockers and publish a refreshed execution timeline before next duty cycle.",
    "watch": "Check backlog age and command-net lag every 6 hours.",
    "summary": "Watch — micro-delays stacking; clear blockers before next duty cycle.",
}

spaceforce_aspect_guidance["minor_aspects"]["Sesquiquadrate"] = {
    "severity": "High Risk",
    "headline": "Residual tension reignites dormant faults.",
    "impact": "Old scar tissue flares, reopening vulnerabilities in cyber shields or logistics chains.",
    "action": "Activate contingency squads, rehearse rollback plans, and require status pings each watch until metrics stabilise.",
    "watch": "Monitor incident reopen counts and mean time to mitigation.",
    "summary": "High Risk — legacy faults resurfacing; activate contingencies now.",
}

spaceforce_aspect_guidance["minor_aspects"]["Quintile"] = {
    "severity": "Opportunity",
    "headline": "Creative tradecraft unlocks precision moves.",
    "impact": "Niche ingenuity sharpens mission effects without increasing exposure.",
    "action": "Fund prototype tactics, document results, and schedule a review inside 48 hours.",
    "watch": "Track pilot KPIs and crew adoption sentiment.",
    "summary": "Opportunity — precise innovation window; run 48h prototype sprint.",
}

spaceforce_aspect_guidance["minor_aspects"]["Biquintile"] = {
    "severity": "Opportunity",
    "headline": "Master-level skills elevate specialized detachments.",
    "impact": "Elite teams can secure premium orbital lanes or cyber corridors with minimal resistance.",
    "action": "Authorize surge missions for the expert cell and capture best practices for doctrine updates this week.",
    "watch": "Monitor utilisation and fatigue metrics for the specialist squad.",
    "summary": "Opportunity — elite cell hot; authorize surge missions and log lessons.",
}

spaceforce_aspect_guidance["minor_aspects"]["Novile"] = {
    "severity": "Watch",
    "headline": "Cycles close and crews prep for the next theater.",
    "impact": "Momentum plateaus while stakeholders expect the follow-on brief.",
    "action": "Run a retrospection huddle within 24 hours, capture lessons, and outline the successor plan.",
    "watch": "Track renewal signals and morale notes during the handoff.",
    "summary": "Watch — mission chapter closing; run retro and brief next play.",
}

spaceforce_aspect_guidance["minor_aspects"]["Binovile"] = {
    "severity": "Opportunity",
    "headline": "Iterative refinements tighten mission variance.",
    "impact": "Small upgrades stabilize telemetry and increase crew trust.",
    "action": "Schedule rapid feedback loops and recalibrate SOPs over the next two duty cycles.",
    "watch": "Monitor adoption metrics and variance spread.",
    "summary": "Opportunity — refinement loop active; run rapid feedback cycles.",
}

spaceforce_aspect_guidance["minor_aspects"]["Quadranovile"] = {
    "severity": "Watch",
    "headline": "Late-cycle consolidation requires exit prep.",
    "impact": "Value settles as teams negotiate redeployments and relief windows.",
    "action": "Task finance/logistics to stage succession packets and hedge residual risk this week.",
    "watch": "Watch contract renewals and sustainment triggers.",
    "summary": "Watch — consolidation phase; prep exit packets and hedges.",
}

spaceforce_aspect_guidance["minor_aspects"]["Quadraundecile"] = {
    "severity": "Watch",
    "headline": "Edge-case tension tests mission flexibility.",
    "impact": "Niche constraints or unexpected cross-talk threaten to distract the primary flight plan.",
    "action": "Isolate the anomaly, deploy a small patch team, and revalidate the main checklist before resuming tempo.",
    "watch": "If the edge case spreads, sandbox it and protect core cadence.",
    "summary": "Watch — edge-case friction; patch locally and guard the core cadence.",
}

spaceforce_aspect_guidance["minor_aspects"]["Quattuordecile"] = {
    "severity": "Watch",
    "headline": "Resource shifts realign with emerging demand.",
    "impact": "Portfolios rotate toward resilient outposts, needing precise comms.",
    "action": "Cue treasury to rebalance coverage ratios and brief crews on the new posture this watch.",
    "watch": "Monitor allocation drift and coverage telemetry daily.",
    "summary": "Watch — gentle rotation; rebalance coverage this watch.",
}

spaceforce_aspect_guidance["minor_aspects"]["Quinvigintile"] = {
    "severity": "Opportunity",
    "headline": "Precision refinements unlock hidden readiness gains.",
    "impact": "Analytics + craftsmanship elevate specific lines without extra cost.",
    "action": "Deploy advanced diagnostics, reward precision teams, and hold a metrics review in 72 hours.",
    "watch": "Track margin delta and defect rate on refined ops.",
    "summary": "Opportunity — precision lift; deploy analytics and review in 72h.",
}

spaceforce_aspect_guidance["minor_aspects"]["Semi-Octile"] = {
    "severity": "Watch",
    "headline": "Tactical friction tests agility.",
    "impact": "Intraday noise widens ranges and slows approvals.",
    "action": "Tighten intraday limits, streamline signatures, and rebrief watch standers immediately.",
    "watch": "Monitor intraday volatility and approval cycle time.",
    "summary": "Watch — agility test; tighten limits and signatures now.",
}

spaceforce_aspect_guidance["minor_aspects"]["Semiduodecile"] = {
    "severity": "Watch",
    "headline": "Quiet rebalancing primes the next surge.",
    "impact": "Systems shed noise to reset baseline allocations.",
    "action": "Have finance tidy balance sheets, retire low-value loops, and stage ready reserves this week.",
    "watch": "Review liquidity ratios and working capital.",
    "summary": "Watch — calm reset; tidy balance sheet and prep reserves.",
}

spaceforce_aspect_guidance["minor_aspects"]["Septile"] = {
    "severity": "Watch",
    "headline": "Intuitive leaps challenge the data picture.",
    "impact": "Markets defy models, requiring blended judgement.",
    "action": "Pair qualitative intel with guardrails and keep optionality open this duty cycle.",
    "watch": "Track forecast-to-actual variance and hedge posture.",
    "summary": "Watch — intuition vs. models; blend intel and guardrails.",
}

spaceforce_aspect_guidance["minor_aspects"]["Biseptile"] = {
    "severity": "Watch",
    "headline": "Long cycles resurface and hint at structural pivots.",
    "impact": "Sentiment sways on elusive drivers, stressing long-duration bets.",
    "action": "Task strategy cells to revisit decade-long theses and publish revised scenarios within 72 hours.",
    "watch": "Monitor macro narrative trackers and long-horizon yields.",
    "summary": "Watch — deep-cycle narratives; refresh long-horizon scenarios.",
}

spaceforce_aspect_guidance["minor_aspects"]["Decile"] = {
    "severity": "Opportunity",
    "headline": "Precision execution sharpens mission cadence.",
    "impact": "Disciplined rhythms squeeze extra performance without more burn.",
    "action": "Lock crisp OKRs, run micro-inspections, and celebrate wins this duty cycle.",
    "watch": "Monitor KPI dashboards for steady upticks.",
    "summary": "Opportunity — precision cadence; lock OKRs and monitor KPIs.",
}

spaceforce_aspect_guidance["minor_aspects"]["Duodecile"] = {
    "severity": "Opportunity",
    "headline": "Fine tuning unlocks incremental efficiency gains.",
    "impact": "Process control improves, shrinking variance and lifting readiness.",
    "action": "Run lean audits, refresh SOPs, and enforce micro-savings within 72 hours.",
    "watch": "Track control charts for persistent gains.",
    "summary": "Opportunity — micro-optimisation; run lean audits now.",
}

spaceforce_aspect_guidance["minor_aspects"]["Septdecile"] = {
    "severity": "Watch",
    "headline": "Fractal patterns highlight repeating risks.",
    "impact": "Algorithms adapt while operators battle déjà vu anomalies.",
    "action": "Launch a data audit and refresh detection models before next week.",
    "watch": "Keep anomaly alerts and bias monitors on high sensitivity.",
    "summary": "Watch — repeating risk signature; audit data and refresh models.",
}

spaceforce_aspect_guidance["minor_aspects"]["Septuagenary"] = {
    "severity": "Opportunity",
    "headline": "Long-horizon cycles invite strategic choreography.",
    "impact": "Patient capital can reposition assets for resilience.",
    "action": "Align five-to-seven-year plans and reinforce institutional knowledge this quarter.",
    "watch": "Monitor long-duration indicators and talent retention.",
    "summary": "Opportunity — long-cycle alignment; refresh 5–7 year plans.",
}

spaceforce_aspect_guidance["minor_aspects"]["Sesqui-Octile"] = {
    "severity": "Watch",
    "headline": "Persistent friction stresses agility.",
    "impact": "Variance stays elevated, stretching tolerance for delays.",
    "action": "Deploy a corrective squad, clarify escalation paths, and reassert accountability.",
    "watch": "Track issue reopen rate and stakeholder sentiment.",
    "summary": "Watch — systemic drift; activate corrective squad.",
}

spaceforce_aspect_guidance["minor_aspects"]["Sesquiquintile"] = {
    "severity": "Opportunity",
    "headline": "Creative mastery drives premium readiness.",
    "impact": "Elite craftsmanship wins trust and pricing power.",
    "action": "Guard exclusivity, calibrate incentives, and expand concierge touchpoints this week.",
    "watch": "Track waitlist depth and VIP satisfaction.",
    "summary": "Opportunity — premium demand; protect exclusivity and service.",
}

spaceforce_aspect_guidance["minor_aspects"]["Tredecile"] = {
    "severity": "Opportunity",
    "headline": "Bold storytelling elevates posture.",
    "impact": "Experiential comms drive engagement and alliance morale.",
    "action": "Launch standout activations, partner with coalition voices, and review ROI in ten days.",
    "watch": "Track sentiment lift and premium conversion.",
    "summary": "Opportunity — bold narrative; launch activations and measure in 10d.",
}

spaceforce_aspect_guidance["minor_aspects"]["Tridecile"] = {
    "severity": "Opportunity",
    "headline": "Precision alignment rewards disciplined crews.",
    "impact": "Tight coordination makes a refined tactic land cleanly with minimal drag on comms or fuel.",
    "action": "Select one keystone procedure to perfect this watch, drill it twice, and brief doctrine owners for rollout.",
    "watch": "Avoid over-polish; freeze scope once the keystone piece is stable.",
    "summary": "Opportunity — refined alignment; perfect one keystone move and freeze scope.",
}

spaceforce_aspect_guidance["minor_aspects"]["Triseptile"] = {
    "severity": "Opportunity",
    "headline": "Destiny-level insight pushes beyond the current model.",
    "impact": "Volatility precedes breakthroughs as crews chase bold pivots.",
    "action": "Resource visionary bets, ring-fence cash, and pace communications this month.",
    "watch": "Monitor liquidity runway and change adoption sentiment.",
    "summary": "Opportunity — transformative pivot; resource boldly and pace change.",
}

spaceforce_aspect_guidance["minor_aspects"]["Undecile"] = {
    "severity": "Watch",
    "headline": "Off-nominal vectors surface niche advantages.",
    "impact": "Unusual mission pairings appear; they can open specialist corridors if handled deliberately.",
    "action": "Prototype the unconventional play with a single squad, log telemetry tightly, and cap exposure windows.",
    "watch": "Hold contingency fuel and abort criteria so curiosity does not erode readiness.",
    "summary": "Watch — niche vector; pilot once, log hard, and keep aborts ready.",
}

spaceforce_aspect_guidance["minor_aspects"]["Vigintile"] = {
    "severity": "Opportunity",
    "headline": "Seed signals forecast emerging demand.",
    "impact": "Early adopters hint at future growth trajectories.",
    "action": "Run low-cost experiments, gather signal intel, and pre-position optionality.",
    "watch": "Track qualitative feedback and pilot attribution closely.",
    "summary": "Opportunity — early demand flickers; run low-cost experiments.",
}


def _pair_key(planet_a: str, planet_b: str) -> Tuple[str, str]:
    return tuple(sorted((planet_a, planet_b)))


def _theme(planet: str) -> str:
    return SPACEFORCE_PLANET_THEMES.get(planet, planet.lower())


def default_pair_message(planet_a: str, planet_b: str) -> str:
    theme_a = _theme(planet_a)
    theme_b = _theme(planet_b)
    return f"Balance {theme_a} with {theme_b} to keep the mission rhythm steady."


spaceforce_pair_overrides: Dict[Tuple[str, str], str] = {}
spaceforce_pair_overrides[_pair_key("Sun", "Moon")] = (
    "Align command intent with crew morale reports; publish dawn and dusk briefs to hold cohesion."
)
spaceforce_pair_overrides[_pair_key("Sun", "Mars")] = (
    "Ensure decisive orders respect security bandwidth so tactical thrust does not outrun defenses."
)
spaceforce_pair_overrides[_pair_key("Moon", "Mars")] = (
    "Rotate squads proactively when tempo spikes to prevent fatigue from undermining sortie precision."
)
spaceforce_pair_overrides[_pair_key("Mercury", "Saturn")] = (
    "Lock comms discipline so intel speed does not bypass doctrinal safeguards."
)
spaceforce_pair_overrides[_pair_key("Venus", "Jupiter")] = (
    "Capitalize on coalition goodwill to extend strategic reach without overextending sustainment."
)
spaceforce_pair_overrides[_pair_key("Uranus", "Neptune")] = (
    "Pair experimental autonomy pushes with narrative guidance to avoid perception whiplash."
)
