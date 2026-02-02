from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict

from .aspect_detection import wrap360


@dataclass(frozen=True)
class AyanamsaConstants:
    base_epoch: datetime
    base_offset_deg: float
    drift_deg_per_year: float


# Lahiri (Chitrapaksha) reference: 23°51'11" at 2000-01-01 00:00 UTC.
# Drift uses mean precession ~50.29"/year (~0.013969°/year).
LAHIRI = AyanamsaConstants(
    base_epoch=datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    base_offset_deg=23.8530555556,
    drift_deg_per_year=50.29 / 3600.0,
)

# Galactic Core placeholder; keep drift zero until authoritative constants arrive.
GALACTIC_CORE = AyanamsaConstants(
    base_epoch=datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    base_offset_deg=0.0,
    drift_deg_per_year=0.0,
)

AYANAMSA_TABLE: Dict[str, AyanamsaConstants] = {
    "lahiri": LAHIRI,
    "galactic_core": GALACTIC_CORE,
}

_warned_galactic_core = False


def _years_since(epoch: datetime, dt: datetime) -> float:
    delta_seconds = (dt.replace(tzinfo=timezone.utc) - epoch).total_seconds()
    return delta_seconds / (365.2425 * 86400.0)


def _offset_from_constants(dt: datetime, constants: AyanamsaConstants) -> float:
    years = _years_since(constants.base_epoch, dt)
    offset = constants.base_offset_deg + (constants.drift_deg_per_year * years)
    return wrap360(offset)


def get_ayanamsa_offset(dt: datetime, name: str) -> float:
    """Return ayanamsa offset in degrees for the given datetime.

    Tropical returns 0. Lahiri uses a base offset with precession drift.
    Galactic Core currently uses a placeholder until constants are provided.
    """
    key = (name or "tropical").lower()
    if key == "tropical":
        return 0.0
    if key not in AYANAMSA_TABLE:
        raise SystemExit(f"Unsupported ayanamsa: {name}")

    if key == "galactic_core":
        global _warned_galactic_core
        if not _warned_galactic_core:
            logging.warning(
                "galactic_core ayanamsa uses placeholder constants; supply authoritative values when available."
            )
            _warned_galactic_core = True

    return _offset_from_constants(dt, AYANAMSA_TABLE[key])
