from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
import math
from typing import Dict, List

from .aspect_detection import wrap360
from .placidus import placidus_cusps


@dataclass
class HouseResult:
    houses: Dict[str, int]
    cusps: List[float]
    system_used: str
    fallback: bool
    reason: str = ""


def _compute_placidus_cusps(_: datetime, __: float, ___: float, ____: float) -> List[float]:
    raise NotImplementedError


def _whole_sign_houses(longitudes: Dict[str, float]) -> Dict[str, int]:
    houses: Dict[str, int] = {}
    for planet, lon in longitudes.items():
        houses[planet] = int(wrap360(lon) // 30) + 1  # Aries=1 baseline
    return houses


def _assign_from_cusps(longitudes: Dict[str, float], cusps: List[float]) -> Dict[str, int]:
    houses: Dict[str, int] = {}
    # Ensure cusps sorted starting at C1
    ordered = [wrap360(c) for c in cusps]
    if len(ordered) != 12:
        raise ValueError("Expected 12 cusps for Placidus")
    for planet, lon in longitudes.items():
        angle = wrap360(lon)
        # Find the first cusp ahead of angle when walking C1..C12 cyclically
        house = 12
        for idx, cusp in enumerate(ordered):
            next_cusp = ordered[(idx + 1) % 12]
            if cusp <= angle < next_cusp if idx < 11 else angle >= cusp or angle < next_cusp:
                house = idx + 1
                break
        houses[planet] = house
    return houses


def assign_houses(
    dt: datetime,
    longitudes: Dict[str, float],
    *,
    latitude: float,
    longitude: float,
    elevation_m: float = 0.0,
    prefer_system: str = "placidus",
) -> HouseResult:
    # Attempt Placidus, then fallback to Whole Sign if unavailable.
    fallback_counter_incremented = False
    try:
        if prefer_system == "placidus":
            if not ENABLE_PLACIDUS:
                raise NotImplementedError("Placidus disabled until validated")
            cusps = placidus_cusps(dt, latitude, longitude, elevation_m)
            if any(math.isnan(c) for c in cusps):
                raise ValueError("Placidus cusp computation returned NaN")
            houses = _assign_from_cusps(longitudes, cusps)
            return HouseResult(houses=houses, cusps=cusps, system_used="placidus", fallback=False)
    except Exception as exc:
        logging.warning("Placidus houses unavailable, falling back to Whole Sign: %s", exc)
        fallback_counter_incremented = True

    houses = _whole_sign_houses(longitudes)
    if fallback_counter_incremented:
        increment_fallback_counter()
    return HouseResult(houses=houses, cusps=[], system_used="whole_sign", fallback=True, reason="placidus_unavailable")


_fallback_counter = 0


def increment_fallback_counter():
    global _fallback_counter
    _fallback_counter += 1


def fallback_count() -> int:
    return _fallback_counter


def reset_fallback_counter():
    global _fallback_counter
    _fallback_counter = 0


# Temporary gate to enable Placidus once validated
ENABLE_PLACIDUS = True
