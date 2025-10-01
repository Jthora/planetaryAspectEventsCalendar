from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

from skyfield import almanac

from .aspect_detection import wrap360
from .constants import (
    ASCII_LUNAR_PHASE_LABELS,
    CULTURAL_FULL_MOON_NAMES,
    LUNAR_PHASE_MEANINGS,
    LUNAR_PHASES,
    ZODIAC_SIGNS,
)


@dataclass
class LunarPhaseEvent:
    time: datetime
    phase_code: int
    phase_name: str
    phase_symbol: str
    zodiac_name: str
    zodiac_symbol: str
    longitude: float
    cultural_name: Optional[str] = None


def _compute_zodiac(longitude: float) -> tuple[str, str]:
    if not ZODIAC_SIGNS:
        return ("Unknown", "")
    wrapped = wrap360(longitude)
    index = int(wrapped // 30) % len(ZODIAC_SIGNS)
    return ZODIAC_SIGNS[index]


def compute_lunar_phases(eph, ts, start_date: datetime, end_date: datetime) -> List[LunarPhaseEvent]:
    if 'earth' not in eph or 'moon' not in eph:
        return []

    search_start = ts.utc(start_date.year, start_date.month, start_date.day)
    end_buffer = end_date + timedelta(days=1)
    search_end = ts.utc(end_buffer.year, end_buffer.month, end_buffer.day)

    phase_function = almanac.moon_phases(eph)
    times, phases = almanac.find_discrete(search_start, search_end, phase_function)

    earth = eph['earth']
    moon = eph['moon']

    events: List[LunarPhaseEvent] = []
    for t, phase_code in zip(times, phases):
        phase_info = LUNAR_PHASES.get(int(phase_code), ("Unknown Phase", ""))
        phase_name, phase_symbol = phase_info
        phase_dt = t.utc_datetime().replace(tzinfo=None)
        if phase_dt < start_date or phase_dt > end_buffer:
            continue

        astrometric = earth.at(t).observe(moon)
        longitude = astrometric.apparent().ecliptic_latlon()[1].degrees
        zodiac_name, zodiac_symbol = _compute_zodiac(longitude)

        cultural_name: Optional[str] = None
        if int(phase_code) == 2:  # Full Moon
            cultural_name = CULTURAL_FULL_MOON_NAMES.get(phase_dt.month)

        events.append(
            LunarPhaseEvent(
                time=phase_dt,
                phase_code=int(phase_code),
                phase_name=phase_name,
                phase_symbol=phase_symbol,
                zodiac_name=zodiac_name,
                zodiac_symbol=zodiac_symbol,
                longitude=longitude,
                cultural_name=cultural_name,
            )
        )

    return events


def format_phase_label(phase_event: LunarPhaseEvent, ascii_only: bool) -> str:
    if ascii_only:
        return ASCII_LUNAR_PHASE_LABELS.get(phase_event.phase_code, phase_event.phase_name)
    if phase_event.phase_symbol:
        return f"{phase_event.phase_symbol} {phase_event.phase_name}"
    return phase_event.phase_name


def phase_meaning(phase_event: LunarPhaseEvent) -> str:
    return LUNAR_PHASE_MEANINGS.get(
        phase_event.phase_code,
        "Key moment within the lunar cycle.",
    )
