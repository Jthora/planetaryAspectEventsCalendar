from __future__ import annotations

from typing import Dict, Optional, Tuple

# Baseline step tables tuned for cycle detection spans
_INGRESS_STEP_MINUTES = {
    "Moon": 10,
    "Mercury": 30,
    "Venus": 30,
    "Sun": 60,
    "Mars": 60,
    "Jupiter": 120,
    "Saturn": 120,
    "Uranus": 240,
    "Neptune": 240,
    "Pluto": 240,
    "Chiron": 240,
}


def ingress_step_minutes(body: str) -> int:
    """Return coarse step minutes for ingress detection by body class."""

    return _INGRESS_STEP_MINUTES.get(body, 120)


def ingress_step_minutes_with_overrides(body: str, overrides: Optional[Dict[str, int]] = None) -> int:
    """Return ingress step minutes honoring optional per-body overrides."""

    if overrides and body in overrides:
        return overrides[body]
    return ingress_step_minutes(body)


def synodic_pair_step_minutes(body1: str, body2: str) -> int:
    """Return coarse step minutes for synodic separation sampling per pair class."""

    pair = {body1, body2}
    if "Moon" in pair:
        return 15
    if pair & {"Mercury", "Venus"}:
        return 45
    if pair <= {"Jupiter", "Saturn", "Uranus", "Neptune", "Pluto", "Chiron"}:
        return 240
    return 90


def synodic_pair_key(body1: str, body2: str) -> str:
    """Stable key for synodic pair overrides (sorted to ignore order)."""

    a, b = sorted([body1, body2])
    return f"{a}|{b}"


def synodic_pair_step_minutes_with_overrides(
    body1: str, body2: str, overrides: Optional[Dict[str, int]] = None
) -> int:
    """Return synodic step minutes honoring optional per-pair overrides."""

    if overrides:
        key = synodic_pair_key(body1, body2)
        if key in overrides:
            return overrides[key]
    return synodic_pair_step_minutes(body1, body2)
