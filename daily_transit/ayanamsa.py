from __future__ import annotations

import logging
from datetime import datetime, timezone

from .aspect_detection import wrap360

# Lahiri (Chitrapaksha) reference: ~23°51'11" on 2000-01-01 00:00 UTC.
# Drift uses mean precession ~50.29"/year (~0.013969°/year).
LAHIRI_BASE_EPOCH = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
LAHIRI_BASE_OFFSET_DEG = 23.8530555556
LAHIRI_DRIFT_DEG_PER_YEAR = 50.29 / 3600.0  # degrees per Julian year

# Galactic Core placeholder; replace when authoritative constants arrive.
GC_BASE_EPOCH = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
GC_BASE_OFFSET_DEG = 0.0
GC_DRIFT_DEG_PER_YEAR = 0.0


def _years_since(epoch: datetime, dt: datetime) -> float:
    delta_seconds = (dt.replace(tzinfo=timezone.utc) - epoch).total_seconds()
    return delta_seconds / (365.2425 * 86400.0)


def _lahiri_offset(dt: datetime) -> float:
    years = _years_since(LAHIRI_BASE_EPOCH, dt)
    offset = LAHIRI_BASE_OFFSET_DEG + (LAHIRI_DRIFT_DEG_PER_YEAR * years)
    return wrap360(offset)


def _galactic_core_offset(dt: datetime) -> float:
    years = _years_since(GC_BASE_EPOCH, dt)
    offset = GC_BASE_OFFSET_DEG + (GC_DRIFT_DEG_PER_YEAR * years)
    return wrap360(offset)


def get_ayanamsa_offset(dt: datetime, name: str) -> float:
    """Return ayanamsa offset in degrees for the given datetime.

    Tropical returns 0. Lahiri uses a base offset with precession drift.
    Galactic Core currently uses a placeholder until constants are provided.
    """
    key = (name or "tropical").lower()
    if key == "tropical":
        return 0.0
    if key == "lahiri":
        return _lahiri_offset(dt)
    if key == "galactic_core":
        return _galactic_core_offset(dt)
    raise SystemExit(f"Unsupported ayanamsa: {name}")
