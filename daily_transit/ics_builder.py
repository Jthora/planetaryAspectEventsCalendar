from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple

import pytz
from ics import Event

from .aspect_detection import AspectEvent, wrap360
from .constants import (
    ASPECT_SYMBOLS,
    ASCII_ASPECT_SYMBOLS,
    ASCII_PLANET_LABELS,
    ASCII_ZODIAC_SIGNS,
    EPHEMERIS_NAME_MAP,
    ZODIAC_SIGNS,
)
from .lunar_phases import LunarPhaseEvent, format_phase_label, phase_meaning
from .interpretations import get_interpretation


def format_degree(angle: float, ascii_only: bool = False) -> str:
    angle = wrap360(angle)
    sign_index = int(angle // 30)
    deg_within = angle % 30
    deg_int = int(deg_within)
    minutes = int((deg_within - deg_int) * 60)
    sign_name, sign_glyph = ZODIAC_SIGNS[sign_index]
    if ascii_only:
        sign_label = ASCII_ZODIAC_SIGNS.get(sign_name, sign_name[:2])
        return f"{deg_int:02d}°{minutes:02d}' {sign_label}"
    return f"{deg_int:02d}°{minutes:02d}' {sign_name} {sign_glyph}"


def compute_body_longitudes(eph, ts, dt: datetime, planets: List[Tuple[str, str]]) -> Dict[str, float]:
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    earth = eph['earth']
    longitudes = {}
    for name, _glyph in planets:
        key = EPHEMERIS_NAME_MAP.get(name, name.lower())
        if key not in eph:
            continue
        astrometric = earth.at(t).observe(eph[key])
        lon = astrometric.apparent().ecliptic_latlon()[1].degrees
        longitudes[name] = wrap360(lon)
    return longitudes


def build_aspect_event(
    ev: AspectEvent,
    tz,
    status: str,
    thunderbird: bool,
    planets: List[Tuple[str, str]],
    aspect_meanings: Dict[str, str],
    interpretation_mode: str,
    ascii_only: bool,
) -> Event:
    dt_local = pytz.UTC.localize(ev.time).astimezone(tz)
    glyph_lookup = {name: glyph for name, glyph in planets}
    glyph1 = glyph_lookup.get(ev.planet1, '')
    glyph2 = glyph_lookup.get(ev.planet2, '')
    if ascii_only:
        glyph1 = ASCII_PLANET_LABELS.get(ev.planet1, ev.planet1[:2])
        glyph2 = ASCII_PLANET_LABELS.get(ev.planet2, ev.planet2[:2])
    aspect_symbol = (ASCII_ASPECT_SYMBOLS if ascii_only else ASPECT_SYMBOLS).get(ev.aspect, '')
    retro_marker = lambda flag: (" R" if ascii_only else " ℞") if flag else ""
    summary = f"{ev.planet1}{retro_marker(ev.planet1_retrograde)} {glyph1} {aspect_symbol} {ev.planet2}{retro_marker(ev.planet2_retrograde)} {glyph2} ({ev.aspect})"
    interpretation = get_interpretation(
        interpretation_mode,
        ev.aspect,
        ev.planet1,
        ev.planet2,
        aspect_meanings,
    )
    raw_sep_display = wrap360(ev.raw_separation)
    if raw_sep_display >= 360.0 - 1e-3:
        raw_sep_display = 0.0
    planet_line = (
        f"Planets: {ev.planet1}{retro_marker(ev.planet1_retrograde)} {glyph1} / "
        f"{ev.planet2}{retro_marker(ev.planet2_retrograde)} {glyph2}"
    )
    description_lines = [
        f"Aspect: {ev.aspect}",
        planet_line,
        f"Exact Time (UTC): {ev.time.strftime('%Y-%m-%d %H:%M')}",
        f"Separation Δ: {ev.delta:.2f}° (Target {ev.exact_degrees}°)",
        f"Raw Separation: {raw_sep_display:.2f}°",
    ]
    interpretation_lines = interpretation.detail_lines if interpretation.detail_lines else ["Interpretation: No data available."]
    description_lines.append("")
    description_lines.extend(interpretation_lines)
    event = Event()
    event.name = summary
    event.begin = dt_local
    event.description = "\n".join(description_lines)
    event.categories = [ev.aspect]
    uid_source = f"{ev.planet1}-{ev.planet2}-{ev.aspect}-{ev.time.strftime('%Y%m%d%H%M')}"
    uid_hash = hashlib.md5(uid_source.encode()).hexdigest()
    event.uid = f"{uid_hash}@transit-aspect"
    if status:
        try:
            event.status = status
        except Exception:
            pass
    if thunderbird:
        now_utc = datetime.utcnow().replace(microsecond=0)
        try:
            event.created = now_utc
            event.last_modified = now_utc
        except Exception:
            pass
    return event


def build_daily_summary(
    dt: datetime,
    tz,
    eph,
    ts,
    aspects_today: List[AspectEvent],
    status: str,
    thunderbird: bool,
    planets: List[Tuple[str, str]],
    aspect_meanings: Dict[str, str],
    interpretation_mode: str,
    ascii_only: bool,
) -> Event:
    local_midnight = tz.localize(datetime(dt.year, dt.month, dt.day, 0, 0, 0))
    utc_midnight = local_midnight.astimezone(pytz.UTC)
    longitudes = compute_body_longitudes(eph, ts, utc_midnight.replace(tzinfo=None), planets)

    lines = ["Daily Tropical Transit Chart", f"Date: {dt.strftime('%Y-%m-%d')} ({tz.zone})", "", "Positions:"]
    for name, glyph in planets:
        if name not in longitudes:
            continue
        label = ASCII_PLANET_LABELS.get(name, name[:2]) if ascii_only else glyph
        lines.append(f"  {name:<8} {label}  {format_degree(longitudes[name], ascii_only)}")

    if aspects_today:
        lines.append("")
        lines.append("Exact Aspects Today:")
        for ev in aspects_today:
            aspect_symbol = (ASCII_ASPECT_SYMBOLS if ascii_only else ASPECT_SYMBOLS).get(ev.aspect, '')
            interpretation = get_interpretation(
                interpretation_mode,
                ev.aspect,
                ev.planet1,
                ev.planet2,
                aspect_meanings,
            )
            meaning_short = interpretation.summary
            time_local = pytz.UTC.localize(ev.time).astimezone(tz)
            retro_marker = lambda flag: (" R" if ascii_only else " ℞") if flag else ""
            planet1_label = ASCII_PLANET_LABELS.get(ev.planet1, ev.planet1[:2]) if ascii_only else ev.planet1
            planet2_label = ASCII_PLANET_LABELS.get(ev.planet2, ev.planet2[:2]) if ascii_only else ev.planet2
            lines.append(
                f"  {time_local.strftime('%H:%M')}  {planet1_label}{retro_marker(ev.planet1_retrograde)} {aspect_symbol} "
                f"{planet2_label}{retro_marker(ev.planet2_retrograde)} - Δ{ev.delta:.2f}° - {meaning_short[:80]}"
            )
    else:
        lines.append("")
        lines.append("No exact major aspects detected today within orb criteria.")

    event = Event()
    event.name = f"Daily Transit Chart {dt.strftime('%Y-%m-%d')}"
    event.begin = local_midnight
    event.description = "\n".join(lines)
    event.categories = ["Daily Transit"]
    uid_source = f"daily-{dt.strftime('%Y-%m-%d')}"
    uid_hash = hashlib.sha1(uid_source.encode()).hexdigest()
    event.uid = f"{uid_hash}@transit-daily"
    if status:
        try:
            event.status = status
        except Exception:
            pass
    if thunderbird:
        now_utc = datetime.utcnow().replace(microsecond=0)
        try:
            event.created = now_utc
            event.last_modified = now_utc
        except Exception:
            pass
    return event


def build_lunar_phase_event(
    phase_event: LunarPhaseEvent,
    tz,
    status: str,
    thunderbird: bool,
    ascii_only: bool,
) -> Event:
    dt_local = pytz.UTC.localize(phase_event.time).astimezone(tz)
    phase_label = format_phase_label(phase_event, ascii_only)
    zodiac_label = (
        ASCII_ZODIAC_SIGNS.get(phase_event.zodiac_name, phase_event.zodiac_name[:2])
        if ascii_only
        else f"{phase_event.zodiac_name} {phase_event.zodiac_symbol}"
    )
    summary_suffix = f" ({phase_event.cultural_name} Moon)" if phase_event.cultural_name else ""
    summary = (
        f"{phase_label} in {phase_event.zodiac_name} {zodiac_label}" if ascii_only
        else f"{phase_label} in {phase_event.zodiac_name} {phase_event.zodiac_symbol}"
    ) + summary_suffix

    description_lines = [
        f"Phase: {phase_event.phase_name}",
        f"Exact Time (UTC): {phase_event.time.strftime('%Y-%m-%d %H:%M')}",
        f"Moon Ecliptic Longitude: {format_degree(phase_event.longitude, ascii_only)}",
        f"Zodiac: {phase_event.zodiac_name}",
        f"Meaning: {phase_meaning(phase_event)}",
    ]
    if phase_event.cultural_name:
        description_lines.append(f"Cultural Name: {phase_event.cultural_name} Moon")

    event = Event()
    event.name = summary
    event.begin = dt_local
    event.description = "\n".join(description_lines)
    event.categories = ["Lunar Phase", phase_event.phase_name]

    uid_source = f"lunar-phase-{phase_event.time.strftime('%Y%m%d%H%M')}-{phase_event.phase_code}"
    uid_hash = hashlib.md5(uid_source.encode()).hexdigest()
    event.uid = f"{uid_hash}@transit-lunar-phase"

    if status:
        try:
            event.status = status
        except Exception:
            pass
    if thunderbird:
        now_utc = datetime.utcnow().replace(microsecond=0)
        try:
            event.created = now_utc
            event.last_modified = now_utc
        except Exception:
            pass
    return event
