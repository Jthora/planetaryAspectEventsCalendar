from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
import logging
from time import perf_counter
from typing import Dict, List, Optional, Tuple

import pytz
from ics import Event

from .aspect_detection import AspectEvent, wrap360
from .compact_formatter import format_compact_aspect
from .constants import (
    ASPECT_SYMBOLS,
    ASCII_ASPECT_SYMBOLS,
    ASCII_PLANET_LABELS,
    ASCII_ZODIAC_SIGNS,
    EPHEMERIS_NAME_MAP,
    ZODIAC_SIGNS,
)
from .interpretations import get_interpretation, planet_themes_for_mode
from .lunar_phases import LunarPhaseEvent, format_phase_label, phase_meaning
from .zodiac_metadata import (
    PlanetZodiacInfo,
    ascii_modality_shape,
    build_context_from_longitudes,
    element_business_tone,
    modality_business_tone,
    sign_business_tone,
    element_raves_tone,
    modality_raves_tone,
    sign_raves_tone,
)


logger = logging.getLogger(__name__)


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


def compute_body_longitudes(
    eph,
    ts,
    dt: datetime,
    planets: List[Tuple[str, str]],
    *,
    ayanamsa_offset: float = 0.0,
) -> Dict[str, float]:
    log_timing = logger.isEnabledFor(logging.DEBUG)
    start = perf_counter() if log_timing else None

    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    earth = eph["earth"]
    longitudes: Dict[str, float] = {}
    for name, _glyph in planets:
        key = EPHEMERIS_NAME_MAP.get(name, name.lower())
        if key not in eph:
            continue
        astrometric = earth.at(t).observe(eph[key])
        lon = astrometric.apparent().ecliptic_latlon()[1].degrees
        adjusted = wrap360(lon - ayanamsa_offset) if ayanamsa_offset else wrap360(lon)
        longitudes[name] = adjusted

    if start is not None:
        elapsed_ms = (perf_counter() - start) * 1000.0
        if ayanamsa_offset:
            logger.debug(
                "Ayanamsa-adjusted longitude calculation for %d bodies took %.2f ms (offset=%.5f)",
                len(longitudes),
                elapsed_ms,
                ayanamsa_offset,
            )
        else:
            logger.debug(
                "Tropical longitude calculation for %d bodies took %.2f ms",
                len(longitudes),
                elapsed_ms,
            )

    return longitudes


def _planet_symbol(planet: str, planets: List[Tuple[str, str]], ascii_only: bool) -> str:
    glyph_lookup = {name: glyph for name, glyph in planets}
    if ascii_only:
        return ASCII_PLANET_LABELS.get(planet, planet[:2])
    return glyph_lookup.get(planet, planet[:2])


def _aspect_symbol(aspect_name: str, ascii_only: bool) -> str:
    if ascii_only:
        raw = ASCII_ASPECT_SYMBOLS.get(aspect_name, aspect_name.upper())
        return f"[{raw}]"
    return ASPECT_SYMBOLS.get(aspect_name, aspect_name)


def _summary_with_zodiac(
    planet1: str,
    planet2: str,
    aspect_name: str,
    planets: List[Tuple[str, str]],
    context: Dict[str, PlanetZodiacInfo],
    ascii_only: bool,
) -> str:
    info1 = context.get(planet1)
    info2 = context.get(planet2)
    symbol1 = _planet_symbol(planet1, planets, ascii_only)
    symbol2 = _planet_symbol(planet2, planets, ascii_only)
    aspect_symbol = _aspect_symbol(aspect_name, ascii_only)

    left = info1.metadata.left_framing if info1 else ""
    right = info2.metadata.right_framing if info2 else ""

    summary = f"{left} {symbol1} {aspect_symbol} {symbol2} {right}".strip()
    return " ".join(summary.split())


def _tone_functions_for_mode(interpretation_mode: str):
    if interpretation_mode == "raves":
        return element_raves_tone, modality_raves_tone, sign_raves_tone
    return element_business_tone, modality_business_tone, sign_business_tone


def _planet_profile_lines(
    planet: str,
    context: Optional[PlanetZodiacInfo],
    ascii_only: bool,
    planet_themes: Dict[str, str],
    element_tone_fn,
    modality_tone_fn,
    sign_tone_fn,
) -> List[str]:
    if not context:
        return []

    meta = context.metadata
    theme = planet_themes.get(planet, planet.lower())
    bullet = "-" if ascii_only else "•"
    separator = "--" if ascii_only else "—"

    if ascii_only:
        heading = f"{meta.left_framing} {planet} {meta.right_framing} -- {meta.name}"
    else:
        emoji = meta.emoji or ""
        heading = f"{meta.left_framing} {planet} {emoji} {meta.right_framing} — {meta.name}".strip()

    lines: List[str] = [heading]

    if ascii_only:
        sign_label = ASCII_ZODIAC_SIGNS.get(meta.name, meta.name[:2])
        lines.append(f"{bullet} Sign: {meta.name} ({sign_label}) {separator} {meta.modality_name} {meta.element_name}")
        lines.append(
            f"{bullet} Element: {meta.element_name} ({meta.element_color_name}) {separator} {element_tone_fn(meta.element_name)}"
        )
        lines.append(
            f"{bullet} Modality: {meta.modality_name} ({ascii_modality_shape(meta.modality_name)}) {separator} {modality_tone_fn(meta.modality_name)}"
        )
    else:
        emoji = meta.emoji or ""
        lines.append(f"{bullet} Sign: {meta.name} {emoji} {separator} {meta.modality_name} {meta.element_name}")
        color = meta.element_color_emoji or ""
        element_part = f"{meta.element_name} {meta.element_glyph}"
        if color:
            element_part = f"{element_part} {color}"
        if meta.element_color_name:
            element_part = f"{element_part} ({meta.element_color_name})"
        lines.append(f"{bullet} Element: {element_part} {separator} {element_tone_fn(meta.element_name)}")
        modality_part = f"{meta.modality_name} {meta.modality_symbol}".strip()
        lines.append(f"{bullet} Modality: {modality_part} {separator} {modality_tone_fn(meta.modality_name)}")

    lines.append(
        f"{bullet} Profile: The {planet} ({theme}) in {meta.name} {separator} {sign_tone_fn(meta.name)}"
    )
    lines.append(f"{bullet} Element focus: {element_tone_fn(meta.element_name)}")
    lines.append(f"{bullet} Modality focus: {modality_tone_fn(meta.modality_name)}")
    return lines


def build_aspect_event(
    ev: AspectEvent,
    tz,
    status: str,
    thunderbird: bool,
    planets: List[Tuple[str, str]],
    aspect_meanings: Dict[str, str],
    interpretation_mode: str = "business",
    ascii_only: bool = False,
    *,
    eph=None,
    ts=None,
    zodiac_context: Optional[Dict[str, PlanetZodiacInfo]] = None,
    ayanamsa_offset: float = 0.0,
    show_debug_ayanamsa: bool = False,
) -> Event:
    dt_local = pytz.UTC.localize(ev.time).astimezone(tz)
    retro_marker = lambda flag: (" R" if ascii_only else " ℞") if flag else ""

    if zodiac_context is None:
        if eph is None or ts is None:
            zodiac_context = {}
        else:
            longitudes = compute_body_longitudes(
                eph,
                ts,
                ev.time,
                planets,
                ayanamsa_offset=ayanamsa_offset,
            )
            zodiac_context = build_context_from_longitudes(longitudes)

    summary = _summary_with_zodiac(
        ev.planet1,
        ev.planet2,
        ev.aspect,
        planets,
        zodiac_context,
        ascii_only,
    )

    interpretation = get_interpretation(
        interpretation_mode,
        ev.aspect,
        ev.planet1,
        ev.planet2,
        aspect_meanings,
    )
    planet_theme_map = planet_themes_for_mode(interpretation_mode)
    element_tone_fn, modality_tone_fn, sign_tone_fn = _tone_functions_for_mode(interpretation_mode)

    raw_sep_display = wrap360(ev.raw_separation)
    if raw_sep_display >= 360.0 - 1e-3:
        raw_sep_display = 0.0

    planet_line = (
        f"Planets: {ev.planet1}{retro_marker(ev.planet1_retrograde)} {_planet_symbol(ev.planet1, planets, ascii_only)} / "
        f"{ev.planet2}{retro_marker(ev.planet2_retrograde)} {_planet_symbol(ev.planet2, planets, ascii_only)}"
    )

    description_lines = [
        f"Aspect: {ev.aspect}",
        planet_line,
        f"Exact Time (UTC): {ev.time.strftime('%Y-%m-%d %H:%M')}",
        f"Separation Δ: {ev.delta:.2f}° (Target {ev.exact_degrees}°)",
        f"Raw Separation: {raw_sep_display:.2f}°",
    ]

    interpretation_lines = (
        interpretation.detail_lines
        if interpretation.detail_lines
        else ["Interpretation: No data available."]
    )
    description_lines.append("")
    description_lines.extend(interpretation_lines)

    if show_debug_ayanamsa and zodiac_context:
        ayanamsa_label: Optional[str] = None
        for info in zodiac_context.values():
            if info.ayanamsa_name:
                ayanamsa_label = info.ayanamsa_name
                break
        if ayanamsa_label:
            description_lines.append("")
            description_lines.append(f"Ayanamsa: {ayanamsa_label}")

    if interpretation_mode == "raves" and getattr(interpretation, "extras", {}):
        extras = interpretation.extras or {}
        label_map = {
            "music_genre": "Music genre",
            "music_subgenre": "Subgenre",
            "music_theme": "Theme",
            "music_style": "Style",
            "music_speed": "Speed",
            "music_tone": "Tone",
            "music_vibe": "Vibe",
            "outfit_cue": "Outfit",
            "social_mode": "Social mode",
            "friend_making_risk": "Friend-making",
            "chaos_order": "Chaos/Order",
            "safety_flag": "Safety",
            "conflict_risk": "Conflict risk",
            "crowd_profile": "Crowd",
        }
        field_order = [
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
        ]
        bullet = "-" if ascii_only else "•"
        description_lines.append("")
        description_lines.append("Rave Extras:")
        for key in field_order:
            val = extras.get(key)
            if not val:
                continue
            label = label_map.get(key, key.replace("_", " ").title())
            description_lines.append(f"{bullet} {label}: {val}")

    profiles: List[str] = []
    info1 = zodiac_context.get(ev.planet1)
    info2 = zodiac_context.get(ev.planet2)
    lines1 = _planet_profile_lines(
        ev.planet1,
        info1,
        ascii_only,
        planet_theme_map,
        element_tone_fn,
        modality_tone_fn,
        sign_tone_fn,
    )
    lines2 = _planet_profile_lines(
        ev.planet2,
        info2,
        ascii_only,
        planet_theme_map,
        element_tone_fn,
        modality_tone_fn,
        sign_tone_fn,
    )
    if lines1 or lines2:
        profiles.append("")
        profiles.append("Planet Profiles:")
        if lines1:
            profiles.extend(lines1)
        if lines1 and lines2:
            profiles.append("")
        if lines2:
            profiles.extend(lines2)

    description_lines.extend(profiles)

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


def build_compact_aspect_event(
    ev: AspectEvent,
    tz,
    planets: List[Tuple[str, str]],
    zodiac_context: Dict[str, PlanetZodiacInfo],
    *,
    precision_deg: str = "decimal",
    precision_time: str = "seconds",
    ascii_only: bool = False,
) -> Event:
    """Build a compact ICS event line with houses, retro markers, and Δ only."""

    summary_line = format_compact_aspect(
        ev,
        zodiac_context,
        planets=planets,
        precision_deg=precision_deg,
        precision_time=precision_time,
        ascii_only=ascii_only,
    )

    dt_local = pytz.UTC.localize(ev.time).astimezone(tz)
    delta_str = summary_line.split("Δ=")[-1] if "Δ=" in summary_line else ""

    def planet_block(name: str, retro: bool) -> str:
        info = zodiac_context.get(name)
        if not info:
            return name
        house_part = f" H:{info.house}" if info.house else ""
        angle = format_degree(info.longitude, ascii_only)
        label = _planet_symbol(name, planets, ascii_only)
        retro_mark = " R" if (ascii_only and retro) else (" ℞" if retro else "")
        return f"{label}{retro_mark} Z:{info.sign}{house_part} {angle}"

    description_lines = [
        f"UTC: {dt_local.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Δ: {delta_str}",
        f"P1: {planet_block(ev.planet1, ev.planet1_retrograde)}",
        f"P2: {planet_block(ev.planet2, ev.planet2_retrograde)}",
    ]

    event = Event()
    event.name = summary_line
    event.begin = dt_local
    event.description = "\n".join(description_lines)
    event.categories = [ev.aspect]
    uid_source = f"compact-{ev.planet1}-{ev.planet2}-{ev.aspect}-{ev.time.strftime('%Y%m%d%H%M%S')}"
    uid_hash = hashlib.md5(uid_source.encode()).hexdigest()
    event.uid = f"{uid_hash}@transit-aspect"
    return event


def build_daily_transit_event(
    dt: datetime,
    tz,
    eph,
    ts,
    aspects_today: List[AspectEvent],
    status: str,
    thunderbird: bool,
    planets: List[Tuple[str, str]],
    aspect_meanings: Dict[str, str],
    interpretation_mode: str = "business",
    ascii_only: bool = False,
    *,
    ayanamsa_offset: float = 0.0,
) -> Event:
    # Compute positional context at the day's midnight, but serialize the event as all-day
    local_midnight = tz.localize(datetime(dt.year, dt.month, dt.day, 0, 0, 0))
    utc_midnight = local_midnight.astimezone(pytz.UTC)
    longitudes = compute_body_longitudes(
        eph,
        ts,
        utc_midnight.replace(tzinfo=None),
        planets,
        ayanamsa_offset=ayanamsa_offset,
    )

    lines = [
        "Daily Tropical Transit Chart",
        f"Date: {dt.strftime('%Y-%m-%d')} ({tz.zone})",
        "",
        "Positions:",
    ]

    for name, glyph in planets:
        if name not in longitudes:
            continue
        label = ASCII_PLANET_LABELS.get(name, name[:2]) if ascii_only else glyph
        lines.append(f"  {name:<8} {label}  {format_degree(longitudes[name], ascii_only)}")

    if aspects_today:
        lines.append("")
        lines.append("Exact Aspects Today:")
        for ev in aspects_today:
            aspect_symbol = (
                (ASCII_ASPECT_SYMBOLS if ascii_only else ASPECT_SYMBOLS).get(ev.aspect, ev.aspect)
            )
            interpretation = get_interpretation(
                interpretation_mode,
                ev.aspect,
                ev.planet1,
                ev.planet2,
                aspect_meanings,
            )
            meaning_short = interpretation.summary
            if len(meaning_short) > 96:
                meaning_short = meaning_short[:93].rstrip() + "..."
            time_local = pytz.UTC.localize(ev.time).astimezone(tz)
            retro_marker = lambda flag: (" R" if ascii_only else " ℞") if flag else ""
            planet1_label = (
                ASCII_PLANET_LABELS.get(ev.planet1, ev.planet1[:2]) if ascii_only else ev.planet1
            )
            planet2_label = (
                ASCII_PLANET_LABELS.get(ev.planet2, ev.planet2[:2]) if ascii_only else ev.planet2
            )
            lines.append(
                f"  {time_local.strftime('%H:%M')}  {planet1_label}{retro_marker(ev.planet1_retrograde)} {aspect_symbol} "
                f"{planet2_label}{retro_marker(ev.planet2_retrograde)} - Δ{ev.delta:.2f}° - {meaning_short}"
            )
    else:
        lines.append("")
        lines.append("No exact major aspects detected today within orb criteria.")

    event = Event()
    event.name = f"Daily Transit Chart {dt.strftime('%Y-%m-%d')}"
    event.begin = dt.date()
    try:
        event.make_all_day()
    except Exception:
        pass
    try:
        event.end = event.begin + timedelta(days=1)
    except Exception:
        event.end = dt.date() + timedelta(days=1)
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
    interpretation_mode: str = "business",
    ascii_only: bool = False,
    *,
    ayanamsa_offset: float = 0.0,
) -> Event:
    """Backward compatible wrapper for existing call sites/tests."""

    return build_daily_transit_event(
        dt,
        tz,
        eph,
        ts,
        aspects_today,
        status,
        thunderbird,
        planets,
        aspect_meanings,
        interpretation_mode=interpretation_mode,
        ascii_only=ascii_only,
        ayanamsa_offset=ayanamsa_offset,
    )


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
        f"{phase_label} in {phase_event.zodiac_name} {zodiac_label}"
        if ascii_only
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
