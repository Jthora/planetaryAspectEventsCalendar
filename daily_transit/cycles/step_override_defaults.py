from __future__ import annotations

from typing import Dict


def _pair_key(a: str, b: str) -> str:
    return "|".join(sorted((a, b)))


# Tuned overrides applied after perf measurements (4.2.1.2.b).
# These reduce ephemeris/separation churn for slow-moving bodies and outer synodic pairs
# without tightening fast-body thresholds.
DEFAULT_INGRESS_STEP_OVERRIDES: Dict[str, int] = {
    "Jupiter": 180,
    "Saturn": 180,
    "Uranus": 360,
    "Neptune": 360,
    "Pluto": 360,
    "Chiron": 360,
}

DEFAULT_SYNODIC_PAIR_STEP_OVERRIDES: Dict[str, int] = {
    # Sun with outers: slower relative motion allows coarser sampling.
    _pair_key("Sun", "Jupiter"): 180,
    _pair_key("Sun", "Saturn"): 180,
    _pair_key("Sun", "Uranus"): 240,
    _pair_key("Sun", "Neptune"): 240,
    _pair_key("Sun", "Pluto"): 240,
    _pair_key("Sun", "Chiron"): 240,
    # Mars with outers: modestly coarser to limit separation cache churn over long spans.
    _pair_key("Mars", "Jupiter"): 150,
    _pair_key("Mars", "Saturn"): 150,
    _pair_key("Mars", "Uranus"): 180,
    _pair_key("Mars", "Neptune"): 180,
    _pair_key("Mars", "Pluto"): 180,
    _pair_key("Mars", "Chiron"): 180,
    # Outer-outer pairs: align with slower drift, keep consistent for all outers/chiron.
    _pair_key("Jupiter", "Saturn"): 300,
    _pair_key("Jupiter", "Uranus"): 300,
    _pair_key("Jupiter", "Neptune"): 360,
    _pair_key("Jupiter", "Pluto"): 360,
    _pair_key("Jupiter", "Chiron"): 360,
    _pair_key("Saturn", "Uranus"): 300,
    _pair_key("Saturn", "Neptune"): 360,
    _pair_key("Saturn", "Pluto"): 360,
    _pair_key("Saturn", "Chiron"): 360,
    _pair_key("Uranus", "Neptune"): 420,
    _pair_key("Uranus", "Pluto"): 420,
    _pair_key("Uranus", "Chiron"): 420,
    _pair_key("Neptune", "Pluto"): 480,
    _pair_key("Neptune", "Chiron"): 480,
    _pair_key("Pluto", "Chiron"): 480,
}
