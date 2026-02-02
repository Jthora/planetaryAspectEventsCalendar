"""Rave-focused narratives for the raves interpretation mode.

This module mirrors the structure of business/space_force dictionaries to deliver
rave-ready copy without touching core logic. It includes planet themes, aspect
guidance template, pair overrides, and a per-sign genre/theme map placeholder.
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

# Optional extra fields (raves-only) are allowed in guidance entries:
# music_genre, music_subgenre, music_theme, music_style, music_speed,
# music_tone, music_vibe, outfit_cue, social_mode, friend_making_risk,
# chaos_order, safety_flag, conflict_risk, crowd_profile
_REQUIRED_GUIDANCE_KEYS = ("severity", "headline", "impact", "action", "watch", "summary")
_OPTIONAL_GUIDANCE_KEYS = (
    "music_genre",
    "music_subgenre",
    "music_theme",
    "music_style",
    "music_speed",
    "music_tone",
    "music_vibe",
    "outfit_cue",
    "social_mode",
    "friend_making_risk",
    "chaos_order",
    "safety_flag",
    "conflict_risk",
    "crowd_profile",
)

RAVES_PLANET_THEMES: Dict[str, str] = {
    "Sun": "headline energy",
    "Moon": "vibe and mood flux",
    "Mercury": "comms and meetups",
    "Venus": "aesthetic cohesion",
    "Mars": "mosh intensity and edge",
    "Jupiter": "scale and guest-list hype",
    "Saturn": "security and lines",
    "Uranus": "surprises and genre flips",
    "Neptune": "trance and dreamy flow",
    "Pluto": "deep intensity and bass weight",
    "North Node": "emerging scenes",
    "South Node": "nostalgia throwbacks",
    "Chiron": "safe healing spaces",
}


def all_raves_planets() -> Tuple[str, ...]:
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
    return {key: "" for key in _REQUIRED_GUIDANCE_KEYS}


def _build_guidance_template() -> Dict[str, Dict[str, Dict[str, str]]]:
    mapping: Dict[str, Dict[str, Dict[str, str]]] = {"major_aspects": {}, "minor_aspects": {}}
    for aspect in _all_aspect_names():
        mapping[_aspect_bucket(aspect)][aspect] = _blank_entry()
    return mapping


raves_aspect_guidance: Dict[str, Dict[str, Dict[str, str]]] = _build_guidance_template()

# Seed major aspects with initial rave-focused copy; minors remain blank until Phase 7.2 is completed.
raves_aspect_guidance["major_aspects"]["Conjunction"] = {
    "severity": "Opportunity",
    "headline": "Peak alignment — one crew, one drop",
    "impact": "Energies fuse; shared focus amplifies the main moment and crew cohesion.",
    "action": "Lock a meetup point, set a pacing plan, and aim the crew at a headline set.",
    "watch": "Overheating or overcommitting; schedule water runs and quick breathers.",
    "summary": "Unified surge with high cohesion if you pace the hype.",
    "music_genre": "Progressive house",
    "music_vibe": "Soaring, unified, hands-up",
    "outfit_cue": "Light layers with reflective pops",
    "social_mode": "Crew-first; welcome friendly add-ons",
    "chaos_order": "Order the rush with checkpoints",
    "safety_flag": "Hydrate and ventilate",
}

raves_aspect_guidance["major_aspects"]["Opposition"] = {
    "severity": "Watch",
    "headline": "Tug-of-war energies",
    "impact": "Competing moods or agendas can split the crew between stages or styles.",
    "action": "Agree on rotation times and a midpoint meet; share pins before wandering.",
    "watch": "Mood swings and friction; avoid digging in on preferences.",
    "summary": "Balance the split so no one fragments the night.",
    "music_genre": "Breaks + techno blend",
    "music_vibe": "Edgy but playful",
    "outfit_cue": "Layered fits that move from chill to peak",
    "social_mode": "Tradeoffs and swaps; keep chat open",
    "chaos_order": "Hold a simple default plan",
    "conflict_risk": "Medium if tired or hungry",
}

raves_aspect_guidance["major_aspects"]["Trine"] = {
    "severity": "Opportunity",
    "headline": "Glide path and easy rapport",
    "impact": "Supportive flow; social openings feel natural and logistics stay smooth.",
    "action": "Float between floors, follow light serendipity, and log quick check-ins.",
    "watch": "Drift without direction; add gentle anchors (meet every hour).",
    "summary": "Light, social glide with low resistance.",
    "music_genre": "Melodic house",
    "music_vibe": "Breezy and open",
    "outfit_cue": "Breathable, easy layers",
    "social_mode": "Friendly mingling; low-pressure invites",
    "chaos_order": "Loose order with soft anchors",
}

raves_aspect_guidance["major_aspects"]["Square"] = {
    "severity": "Watch",
    "headline": "Frictive spark",
    "impact": "Tension can fuel movement or spill into agitation under crowd pressure.",
    "action": "Channel the edge into dancing; set cool-off spots and avoid bottlenecks.",
    "watch": "Short fuses and crowd squeezes; step out before it spikes.",
    "summary": "Use the heat for momentum, not conflict.",
    "music_genre": "Driving techno",
    "music_vibe": "Gritty and kinetic",
    "outfit_cue": "Sturdy shoes, sweat-ready",
    "social_mode": "Stay with trusted crew",
    "chaos_order": "Structured routes between stages",
    "safety_flag": "Identify exits and cool zones",
    "conflict_risk": "Elevated if cramped",
}

raves_aspect_guidance["major_aspects"]["Sextile"] = {
    "severity": "Opportunity",
    "headline": "Chance openings",
    "impact": "Small alignments invite quick wins—new friends, surprise sets, smooth pivots.",
    "action": "Say yes to low-cost invites; bookmark alternates so pivots stay easy.",
    "watch": "Keep an eye on time so wandering stays intentional.",
    "summary": "Light lift—easy connects and flexible choices.",
    "music_genre": "House/garage crossover",
    "music_vibe": "Buoyant and curious",
    "outfit_cue": "Comfort-first with a playful accent",
    "social_mode": "Open to quick circles",
    "chaos_order": "Loose but time-aware",
}

# Wave 1 custom minor aspects (Quincunx, Semisextile, Semisquare)
raves_aspect_guidance["minor_aspects"]["Quincunx"] = {
    "severity": "Watch",
    "headline": "Clashing vibes need a reset",
    "impact": "Mismatched moods or genres pull the crew off sync and fragment the plan.",
    "action": "Call a quick regroup, pick a calmer stage, and set a short reset window before ramping again.",
    "watch": "If tension lingers, split briefly with pins shared and reconvene after one set.",
    "summary": "Watch — vibes collide; regroup, reset, and pace the night.",
    "music_vibe": "Contrast-heavy; move to a neutral floor",
    "social_mode": "Crew-first with soft boundaries",
    "safety_flag": "Hydrate and cool down",
}

raves_aspect_guidance["minor_aspects"]["Semisextile"] = {
    "severity": "Watch",
    "headline": "Tiny missteps are fixable",
    "impact": "Minor timing slips or crowd squeezes can dull momentum if ignored.",
    "action": "Adjust the route, trim the queue, and add a water/check-in pit stop before the next set.",
    "watch": "Nip irritants fast: footwear, heat, or line fatigue.",
    "summary": "Watch — small frictions; reroute, hydrate, and keep it light.",
    "music_vibe": "Easy groove to reset",
    "social_mode": "Low-pressure mingling",
    "safety_flag": "Ventilation and short rests",
}

raves_aspect_guidance["minor_aspects"]["Semisquare"] = {
    "severity": "Watch",
    "headline": "Edge creeping in",
    "impact": "Persistent little blocks—crowd jams, comms fails—can sap energy and spark snaps.",
    "action": "Step off the crush zone, reset signals, and agree on the next two moves before diving back in.",
    "watch": "If tempers spike, cool off for 10 minutes and reset expectations.",
    "summary": "Watch — subtle grind; clear jams, reset comms, then re-enter.",
    "music_vibe": "Groovy but grounded",
    "social_mode": "Stay with trusted crew",
    "conflict_risk": "Medium if overheated",
}

# Wave 2 creative/collaborative minor aspects (Quintile family)
raves_aspect_guidance["minor_aspects"]["Quintile"] = {
    "severity": "Opportunity",
    "headline": "Creative sparks sync the crew",
    "impact": "Unexpected transitions and genre blends land, lifting energy without forcing it.",
    "action": "Follow the inspired switch-up, film a clip, and share pins for the next surprise set.",
    "watch": "Don’t over-script; keep room to wander so the spark stays playful.",
    "summary": "Opportunity — inspiration hits; ride the blend and stay mobile.",
    "music_vibe": "Fusion-friendly; surprise blends",
    "social_mode": "Open circles; invite new friends",
    "outfit_cue": "Statement layer ready for photos",
}

raves_aspect_guidance["minor_aspects"]["Biquintile"] = {
    "severity": "Opportunity",
    "headline": "Showcase moment for core crew flair",
    "impact": "Skillful dancers/hosts can anchor the vibe and draw a following.",
    "action": "Pick one spotlight set, sync signals, and capture highlights for the recap.",
    "watch": "Protect stamina; rotate leaders so no one burns out.",
    "summary": "Opportunity — crew mastery pops; rotate the spotlight and archive the moment.",
    "music_vibe": "Peak-energy but polished",
    "social_mode": "Crew-led with welcoming edges",
    "outfit_cue": "Polished accent piece ready for camera",
}

raves_aspect_guidance["minor_aspects"]["Decile"] = {
    "severity": "Support",
    "headline": "Small tweaks smooth the dancefloor",
    "impact": "Micro-adjustments to spacing, hydration, or pacing keep flow steady.",
    "action": "Shift one meter to open space, set a hydration timer, and lighten the route plan.",
    "watch": "Keep tweaks reversible so you can bounce if the vibe shifts.",
    "summary": "Support — tiny tweaks, smoother flow; keep exits easy.",
    "music_vibe": "Groove-reset interlude",
    "social_mode": "Low-pressure, easy check-ins",
    "safety_flag": "Hydrate and map exits",
}

raves_aspect_guidance["minor_aspects"]["Tredecile"] = {
    "severity": "Opportunity",
    "headline": "Odd pairings spark a new path",
    "impact": "A left-field stage or unexpected collab revives the night’s storyline.",
    "action": "Try the quirky back-to-back set, regroup after one song, and decide if you lock in.",
    "watch": "Keep pins updated in case the experiment flops.",
    "summary": "Opportunity — serendipity knocks; test the detour with clear meetups.",
    "music_vibe": "Eclectic twist; playful",
    "social_mode": "Curious and flexible",
    "safety_flag": "Share location before wandering",
}

# Wave 3 harmonic minor aspects (Semi-/Sesqui-Octile, Septile family, Novile/Binovile)
raves_aspect_guidance["minor_aspects"]["Semi-Octile"] = {
    "severity": "Watch",
    "headline": "Small bumps test pacing",
    "impact": "Crowd knots or timing slips ripple through the plan and dent the vibe.",
    "action": "Pause for a quick reset, pick a clearer path, and agree on the next meetup pin.",
    "watch": "If bumps repeat, slow the tempo and stay closer to trusted spots.",
    "summary": "Watch — minor jolts; reset route and tighten regroup points.",
    "music_vibe": "Groove reset; keep it simple",
    "social_mode": "Crew-first, tighter spacing",
    "safety_flag": "Mind crowd squeezes and exits",
}

raves_aspect_guidance["minor_aspects"]["Sesqui-Octile"] = {
    "severity": "Watch",
    "headline": "Pent-up friction needs a vent",
    "impact": "Old annoyances resurface; patience drops and arguments can spark.",
    "action": "Step out for air, grab water, and set a short cool-off before rejoining.",
    "watch": "If the edge lingers, change rooms or switch crews for one set.",
    "summary": "Watch — tension backlogs; cool off, hydrate, and relink later.",
    "music_vibe": "Calmer interlude to downshift",
    "social_mode": "Low-conflict, soft boundaries",
    "safety_flag": "Hydrate and de-escalate",
}

raves_aspect_guidance["minor_aspects"]["Septile"] = {
    "severity": "Info",
    "headline": "Intuitive detour whispers",
    "impact": "A hunch to try a fringe stage or side quest feels oddly right.",
    "action": "Test the detour for one track, keep pins live, and bail if energy dips.",
    "watch": "Don’t overcommit; keep the main rendezvous intact.",
    "summary": "Info — follow the hunch lightly; keep exits easy.",
    "music_vibe": "Left-field, atmospheric",
    "social_mode": "Small pod exploring",
    "safety_flag": "Share location before wandering",
}

raves_aspect_guidance["minor_aspects"]["Biseptile"] = {
    "severity": "Info",
    "headline": "Old patterns resurface",
    "impact": "A familiar loop in the night returns—could be cozy or stale.",
    "action": "Lean in if it feels warm; if stale, pivot to a fresh room and reset the route.",
    "watch": "Check crew energy; split briefly if tastes diverge.",
    "summary": "Info — familiar loop; choose warmth or pivot quickly.",
    "music_vibe": "Nostalgic groove",
    "social_mode": "Crew vibe check",
    "safety_flag": "Keep meetups tight if splitting",
}

raves_aspect_guidance["minor_aspects"]["Triseptile"] = {
    "severity": "Opportunity",
    "headline": "Breakthrough set reshapes the night",
    "impact": "A standout performance flips the mood from drifting to electric.",
    "action": "Lock in for the set, capture a clip, and plan a celebratory cooldown after.",
    "watch": "Mind stamina; schedule a water break post-peak.",
    "summary": "Opportunity — breakthrough set; lock in, film a moment, then cool down.",
    "music_vibe": "Peak energy with sparkle",
    "social_mode": "Open and euphoric",
    "safety_flag": "Hydrate post-peak",
}

raves_aspect_guidance["minor_aspects"]["Quattuordecile"] = {
    "severity": "Watch",
    "headline": "Tiny timing drifts widen if ignored",
    "impact": "Missed messages or slight delays can scatter the crew.",
    "action": "Re-sync clocks, set shorter check-ins, and pick a clear fallback stage.",
    "watch": "If pings fail twice, regroup in a well-lit anchor spot.",
    "summary": "Watch — timing drift; tighten check-ins and anchor the meetup.",
    "music_vibe": "Steady groove to regroup",
    "social_mode": "Crew regroup focus",
    "safety_flag": "Use bright, central meetups",
}

raves_aspect_guidance["minor_aspects"]["Novile"] = {
    "severity": "Info",
    "headline": "Chapter close invites reflection",
    "impact": "Energy softens; it’s easy to wind down, swap highlights, and plan the after.",
    "action": "Walk-and-talk, share best moments, and set a gentle exit plan.",
    "watch": "Avoid late frictions by aligning on the next stop early.",
    "summary": "Info — soft landing; recap and choose the next move early.",
    "music_vibe": "Warm-down set",
    "social_mode": "Story-sharing stroll",
    "safety_flag": "Plan the exit route",
}

raves_aspect_guidance["minor_aspects"]["Binovile"] = {
    "severity": "Support",
    "headline": "Gentle refinements smooth the flow",
    "impact": "Small tweaks to pacing, spacing, or hydration keep the night comfortable.",
    "action": "Shift to a breezier floor, reset hydration, and lighten the plan for the next hour.",
    "watch": "Keep tweaks light so the vibe stays easy.",
    "summary": "Support — small refinements; stay breezy and hydrated.",
    "music_vibe": "Easy glide; low intensity",
    "social_mode": "Relaxed mingling",
    "safety_flag": "Hydration reminder",
}

raves_aspect_guidance["minor_aspects"]["Undecile"] = {
    "severity": "Info",
    "headline": "Oddball route might spark a niche win",
    "impact": "A quirky stage or micro-scene appears; it could be magic or just weird.",
    "action": "Try one track, keep pins live, and bail fast if the vibe stays off.",
    "watch": "Don’t chase the novelty if the crew energy dips; regroup at a known anchor.",
    "summary": "Info — niche detour; sample once, keep exits easy.",
    "music_vibe": "Leftfield curiosity",
    "social_mode": "Tiny pod scout",
    "safety_flag": "Stay visible; share location",
}

raves_aspect_guidance["minor_aspects"]["Tridecile"] = {
    "severity": "Support",
    "headline": "Precise alignment clicks the flow",
    "impact": "A clean handoff between rooms or genres keeps momentum without strain.",
    "action": "Lock one keystone meetup, rehearse the route, and stick to the simple plan.",
    "watch": "Avoid over-orchestrating; once it works, ride it and skip extra tweaks.",
    "summary": "Support — smooth handoff; keep the keystone route and skip over-planning.",
    "music_vibe": "Well-paced blend",
    "social_mode": "Crew sync with light invites",
    "safety_flag": "Clear pins; check battery",
}

raves_aspect_guidance["minor_aspects"]["Quadraundecile"] = {
    "severity": "Watch",
    "headline": "Edge-case friction needs containment",
    "impact": "A weird crowd pocket or sound clash can derail the mood if it spreads.",
    "action": "Quarantine the odd zone, shift one room over, and recheck everyone’s energy.",
    "watch": "If the weirdness follows, pause for water and reset comms before proceeding.",
    "summary": "Watch — isolate the odd pocket; reset, hydrate, and reroute.",
    "music_vibe": "Fallback groove while regrouping",
    "social_mode": "Stick with core crew",
    "safety_flag": "Hydrate and pick a visible meetup",
}


def _default_entry(aspect: str, bucket: str) -> Dict[str, str]:
    if bucket == "major_aspects":
        return {
            "severity": "Watch",
            "headline": f"{aspect} influence in play",
            "impact": "Energies need pacing and balance; keep the crew aligned.",
            "action": "Set checkpoints, hydrate, and stay flexible as plans shift.",
            "watch": "Overheating or drift; regroup before momentum drops.",
            "summary": f"{aspect}: steady the vibe and pace.",
        }
    return {
        "severity": "Watch",
        "headline": f"{aspect} adjustment window",
        "impact": "Subtle shifts add friction or tweaks; light steering keeps flow smooth.",
        "action": "Make small pivots, keep options open, and schedule short breathers.",
        "watch": "Notice energy dips and crowd squeeze; take breaks early.",
        "summary": "Small adjustment—flex plans and pace.",
    }


for _aspect in _all_aspect_names():
    _bucket = _aspect_bucket(_aspect)
    existing = raves_aspect_guidance.get(_bucket, {}).get(_aspect, {})
    needs_fill = not existing or any(not (existing.get(k, "").strip()) for k in _REQUIRED_GUIDANCE_KEYS)
    if needs_fill:
        raves_aspect_guidance[_bucket][_aspect] = _default_entry(_aspect, _bucket)


def _pair_key(planet_a: str, planet_b: str) -> Tuple[str, str]:
    return tuple(sorted((planet_a, planet_b)))


def _theme(planet: str) -> str:
    return RAVES_PLANET_THEMES.get(planet, planet.lower())


def default_pair_message(planet_a: str, planet_b: str) -> str:
    theme_a = _theme(planet_a)
    theme_b = _theme(planet_b)
    return f"Balance {theme_a} with {theme_b} to keep the night flowing."


raves_pair_overrides: Dict[Tuple[str, str], str] = {}
# Seed a few high-traffic pairs for future population
raves_pair_overrides[_pair_key("Sun", "Moon")] = "Sync headline energy with crowd mood; pace yourself between peaks."
raves_pair_overrides[_pair_key("Sun", "Mars")] = "Channel hype without tipping into chaos; hydrate and plan exits."
raves_pair_overrides[_pair_key("Moon", "Mars")] = "Emotions and edge run high; stay with your crew near the pit."
raves_pair_overrides[_pair_key("Sun", "Mercury")] = "Blend spotlight with comms; set clear meetup pins before splitting."
raves_pair_overrides[_pair_key("Sun", "Venus")] = "Match shine with aesthetic cohesion; avoid vanity delays when moving."
raves_pair_overrides[_pair_key("Moon", "Venus")] = "Comfort-first socializing; choose breathable spaces and kinder lighting."
raves_pair_overrides[_pair_key("Venus", "Mars")] = "Style meets edge—great for dancing; cool down before tempers spike."
raves_pair_overrides[_pair_key("Mercury", "Mars")] = "Fast chatter plus sharp energy; use simple signals to avoid snap arguments."
raves_pair_overrides[_pair_key("Venus", "Jupiter")] = "Social expansion and charm; don’t overcommit to every invite."


# Per-sign genre/theme hints (placeholder lists of ~7 entries each)
RAVES_SIGN_GENRE_MAP: Dict[str, Tuple[str, ...]] = {
    "Aries": (
        "peak-time techno",
        "hard dance",
        "drum and bass",
        "bass house",
        "industrial techno",
        "big-room",
        "trap/bass",
    ),
    "Taurus": (
        "deep house",
        "melodic techno",
        "nu-disco",
        "organic house",
        "downtempo",
        "chillhop",
        "lounge"
    ),
    "Gemini": (
        "tech house",
        "breaks",
        "garage",
        "multi-genre mashups",
        "bassline",
        "funky house",
        "electro"
    ),
    "Cancer": (
        "melodic house",
        "liquid drum and bass",
        "dreamy trance",
        "downtempo",
        "lofi",
        "ambient",
        "chillwave"
    ),
    "Leo": (
        "festival progressive house",
        "vocal trance",
        "electro house",
        "big-room",
        "disco/nu-disco",
        "future house",
        "mainstage pop-EDM"
    ),
    "Virgo": (
        "minimal techno",
        "microhouse",
        "progressive house",
        "deep tech",
        "uplifting trance",
        "breaks",
        "melodic techno"
    ),
    "Libra": (
        "classic house",
        "vocal house",
        "nu-disco",
        "melodic techno",
        "progressive house",
        "funk/disco",
        "soulful house"
    ),
    "Scorpio": (
        "dark techno",
        "industrial",
        "psytrance",
        "deep dubstep",
        "halftime",
        "dark drum and bass",
        "leftfield bass"
    ),
    "Sagittarius": (
        "psytrance",
        "goa",
        "progressive psy",
        "tribal house",
        "afro house",
        "world/bass fusion",
        "festival techno"
    ),
    "Capricorn": (
        "driving techno",
        "hardgroove",
        "classic progressive",
        "structured trance",
        "electro techno",
        "EBM",
        "warehouse house"
    ),
    "Aquarius": (
        "breakbeat",
        "leftfield bass",
        "future garage",
        "glitch hop",
        "experimental techno",
        "hyperpop",
        "idm-leaning sets"
    ),
    "Pisces": (
        "deep trance",
        "ambient",
        "liquid drum and bass",
        "downtempo",
        "organic house",
        "ethereal techno",
        "dreamy prog"
    ),
}


__all__ = [
    "RAVES_PLANET_THEMES",
    "all_raves_planets",
    "raves_aspect_guidance",
    "raves_pair_overrides",
    "default_pair_message",
    "RAVES_SIGN_GENRE_MAP",
]
