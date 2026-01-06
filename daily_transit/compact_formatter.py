from __future__ import annotations

from datetime import datetime
import unicodedata
from typing import Dict, List, Optional, Tuple

from .aspect_detection import AspectEvent
from .zodiac_metadata import PlanetZodiacInfo


def _retro_marker(flag: bool, ascii_only: bool) -> str:
    return " R" if (ascii_only and flag) else (" ℞" if flag else "")


def _format_angle(value: float, precision: str, ascii_only: bool) -> str:
    if precision == "dms":
        deg = int(value)
        minutes_full = (value - deg) * 60
        minutes = int(minutes_full)
        seconds = (minutes_full - minutes) * 60
        deg_symbol = "°" if not ascii_only else " deg"
        return f"{deg:02d}{deg_symbol}{minutes:02d}'{seconds:02.0f}\""
    return f"{value:06.2f}°" if not ascii_only else f"{value:06.2f} deg"


def _short_sign(name: str) -> str:
    return name[:3] if name else ""


def _planet_label(name: str, planets: List[Tuple[str, str]], ascii_only: bool) -> str:
    glyph_lookup = {p: g for p, g in planets}
    if ascii_only:
        return name
    label = glyph_lookup.get(name, name)
    return unicodedata.normalize("NFC", label)


def format_compact_aspect(
    ev: AspectEvent,
    context: Dict[str, PlanetZodiacInfo],
    *,
    planets: Optional[List[Tuple[str, str]]] = None,
    precision_deg: str = "decimal",
    precision_time: str = "seconds",
    ascii_only: bool = False,
) -> str:
    """Render a compact single-line summary for an aspect event.

    Layout: UTC | P1(Z,H,R) aspect P2(Z,H,R) | Δ
    Z = sign, H = house (if available), R = retro marker.
    """

    dt_str = ev.time.strftime("%Y-%m-%dT%H:%M:%SZ" if precision_time == "seconds" else "%Y-%m-%dT%H:%MZ")

    def planet_block(name: str, retro: bool) -> str:
        info = context.get(name)
        sign = _short_sign(info.sign if info else "")
        house = info.house if info and info.house else None
        house_part = f" H:{house}" if house else ""
        angle_part = _format_angle(info.longitude if info else 0.0, precision_deg, ascii_only) if info else ""
        label = _planet_label(name, planets or [], ascii_only)
        return f"{label}{_retro_marker(retro, ascii_only)} Z:{sign}{house_part} {angle_part}".strip()

    left = planet_block(ev.planet1, ev.planet1_retrograde)
    right = planet_block(ev.planet2, ev.planet2_retrograde)
    delta_str = _format_angle(ev.delta, precision_deg, ascii_only)

    output = f"{dt_str} | {left} {ev.aspect} {right} | Δ={delta_str}"
    return output if ascii_only else unicodedata.normalize("NFC", output)
