from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import List

import pytz
from ics import Event

from daily_transit.cycles.dto import CycleEvent

ALL_DAY_THRESHOLD_HOURS = 48.0
UID_NAMESPACE = "helionext-cycles"
SPAN_UID_NAMESPACE = "helionext-cycles-span"
UID_PREFIX = "cycles"


def _uid_namespace_hash(source: str, namespace: str) -> str:
    digest = hashlib.sha256(source.encode()).hexdigest()
    return f"{UID_PREFIX}-{digest[:20]}@{namespace}"


def _uid_for_cycle(ev: CycleEvent) -> str:
    """Stable UID distinct from aspect pipeline namespace.

    Components include engine, schema_version, event_type, bodies, sign/phase,
    and start time to avoid collisions when mixing calendars.
    """

    namespace = SPAN_UID_NAMESPACE if ev.event_type in {"ingress_span", "synodic_phase_span"} else UID_NAMESPACE
    parts = [
        ev.source_engine or UID_NAMESPACE,
        ev.schema_version or "v1",
        ev.event_type,
        ev.body or ev.body1 or "",
        ev.body2 or "",
        ev.sign or ev.start_sign or "",
        f"{ev.phase_angle:.6f}" if ev.phase_angle is not None else "",
        ev.start_time_utc.strftime("%Y%m%d%H%M%S"),
    ]
    if ev.event_type in {"ingress_span", "synodic_phase_span"}:
        parts.append(ev.end_time_utc.strftime("%Y%m%d%H%M%S") if ev.end_time_utc else "")
        parts.append(f"{ev.phase_start_deg:.6f}" if ev.phase_start_deg is not None else "")
        parts.append(f"{ev.phase_end_deg:.6f}" if ev.phase_end_deg is not None else "")
        parts.append(ev.end_sign or "")
    source = "|".join(parts)
    return _uid_namespace_hash(source, namespace)


def _maybe_set_status(event: Event, status: str):
    if not status:
        return
    try:
        event.status = status
    except Exception:
        pass


def _maybe_set_tb_fields(event: Event, thunderbird: bool):
    if not thunderbird:
        return
    now_utc = datetime.utcnow().replace(microsecond=0)
    try:
        event.created = now_utc
        event.last_modified = now_utc
    except Exception:
        pass


def _format_ingress(ev: CycleEvent, ascii_only: bool) -> str:
    body = ev.body or ""
    sign = ev.sign or ""
    arrow = "->" if ascii_only else "→"
    return f"{body} {arrow} {sign}".strip()


def _deg_symbol(ascii_only: bool) -> str:
    return "deg" if ascii_only else "°"


def _format_degree_sign(adjusted_longitude: float | None, sign: str | None, ascii_only: bool) -> str:
    if adjusted_longitude is None:
        return ""
    deg_sym = _deg_symbol(ascii_only)
    normalised = adjusted_longitude % 360.0
    deg_in_sign = normalised % 30.0
    if sign:
        return f"{deg_in_sign:05.2f}{deg_sym} {sign}"
    return f"{normalised:06.2f}{deg_sym}"


def _format_body_position(body: str | None, adjusted_longitude: float | None, sign: str | None, ascii_only: bool) -> str:
    pos = _format_degree_sign(adjusted_longitude, sign, ascii_only)
    if not pos:
        return ""
    return f"{body or ''} {pos}".strip()


def build_cycle_event(ev: CycleEvent, tz, status: str, thunderbird: bool, ascii_only: bool = False) -> Event:
    dt_local = pytz.UTC.localize(ev.start_time_utc).astimezone(tz)
    end_local = pytz.UTC.localize(ev.end_time_utc).astimezone(tz) if ev.end_time_utc else None
    event = Event()
    summary = ev.event_type
    if ev.event_type == "ingress":
        summary = _format_ingress(ev, ascii_only)
    elif ev.event_type == "ingress_span":
        summary = f"{_format_ingress(ev, ascii_only)} span"
    elif ev.event_type == "synodic_phase":
        body1 = ev.body1 or ""
        body2 = ev.body2 or ""
        phase = ev.phase_angle if ev.phase_angle is not None else 0.0
        deg_sym = _deg_symbol(ascii_only)
        pos1 = _format_degree_sign(ev.adjusted_longitude, ev.start_sign, ascii_only)
        pos2 = _format_degree_sign(ev.adjusted_longitude_body2, ev.end_sign, ascii_only)
        summary = f"{body1}/{body2} phase {phase:.0f}{deg_sym}"
        if pos1 and pos2:
            summary = f"{summary} ({pos1} | {pos2})"
    elif ev.event_type == "synodic_phase_span":
        body1 = ev.body1 or ""
        body2 = ev.body2 or ""
        start_phase = ev.phase_start_deg if ev.phase_start_deg is not None else (ev.phase_angle or 0.0)
        end_phase = ev.phase_end_deg if ev.phase_end_deg is not None else start_phase
        arrow = "->" if ascii_only else "→"
        deg_sym = _deg_symbol(ascii_only)
        summary = f"{body1}/{body2} phase {start_phase:.0f}{deg_sym}{arrow}{end_phase:.0f}{deg_sym} span"
    elif ev.event_type == "retro_interval":
        summary = f"{ev.body} retrograde interval"
    elif ev.event_type == "station":
        summary = f"{ev.body} station ({ev.station_direction})"
    elif ev.event_type in {"perihelion", "aphelion"}:
        summary = f"{ev.body} {ev.event_type}"

    event.name = summary
    event.begin = dt_local
    if end_local and end_local != dt_local:
        duration_hours = (end_local - dt_local).total_seconds() / 3600.0
        if ev.event_type in {"retro_interval", "ingress_span", "synodic_phase_span"} and duration_hours >= ALL_DAY_THRESHOLD_HOURS:
            start_date = dt_local.date()
            end_date = end_local.date()
            # For span-style events we want half-open intervals [start, end) in calendar views
            # to avoid day overlaps between consecutive spans. Subtract one day so the last
            # included day is end_date - 1. Retro intervals keep their full extent.
            if ev.event_type in {"ingress_span", "synodic_phase_span"}:
                end_date = max(start_date, end_date - timedelta(days=1))
            event.begin = start_date
            event.end = end_date
            try:
                event.make_all_day()
            except Exception:
                pass
        else:
            event.end = end_local
    description_lines = [f"Event type: {ev.event_type}"]
    if ev.sign:
        description_lines.append(f"Sign: {ev.sign}")
    if ev.event_type == "synodic_phase":
        pos1 = _format_degree_sign(ev.adjusted_longitude, ev.start_sign, ascii_only)
        pos2 = _format_degree_sign(ev.adjusted_longitude_body2, ev.end_sign, ascii_only)
        if ev.body1 and pos1:
            description_lines.append(f"{ev.body1} position: {pos1}")
        if ev.body2 and pos2:
            description_lines.append(f"{ev.body2} position: {pos2}")
    deg_sym = _deg_symbol(ascii_only)
    if ev.phase_angle is not None:
        description_lines.append(f"Phase angle: {ev.phase_angle:.2f}{deg_sym}")
    if ev.separation_deg is not None:
        description_lines.append(f"Separation: {ev.separation_deg:.2f}{deg_sym}")
    if ev.delta_deg is not None:
        description_lines.append(f"Δ to target: {ev.delta_deg:.4f}{deg_sym}")
    if ev.retrograde is not None:
        description_lines.append(f"Retrograde: {ev.retrograde}")
    if ev.station_direction:
        description_lines.append(f"Station direction: {ev.station_direction}")
    if ev.station_strength is not None:
        description_lines.append(f"Station strength: {ev.station_strength:.6f}")
    if ev.distance_au is not None:
        description_lines.append(f"Distance: {ev.distance_au:.6f} AU")
    if ev.event_type == "ingress_span":
        if ev.start_sign:
            description_lines.append(f"Start sign: {ev.start_sign}")
        if ev.end_sign:
            description_lines.append(f"End sign: {ev.end_sign}")
    if ev.event_type == "synodic_phase_span":
        if ev.phase_start_deg is not None and ev.phase_end_deg is not None:
            arrow = "->" if ascii_only else "→"
            description_lines.append(
                f"Phase range: {ev.phase_start_deg:.2f}{deg_sym} {arrow} {ev.phase_end_deg:.2f}{deg_sym}"
            )
    description_lines.append(f"Ayanamsa: {ev.ayanamsa_mode}")
    if ev.uncertainty_seconds is not None:
        description_lines.append(f"Uncertainty: {ev.uncertainty_seconds:.2f} s")
    if ev.computation_notes:
        description_lines.append(f"Notes: {ev.computation_notes}")
    description_lines.append(f"schema_version: {ev.schema_version}")
    event.description = "\n".join(description_lines)
    categories = ["Cycle", ev.event_type]
    if ev.event_type in {"ingress", "ingress_span"} and ev.body:
        categories.append(ev.body)
    if ev.sign:
        categories.append(ev.sign)
    if ev.event_type in {"synodic_phase", "synodic_phase_span"} and ev.body1 and ev.body2:
        categories.append(f"{ev.body1}|{ev.body2}")
    event.categories = categories
    event.uid = _uid_for_cycle(ev)

    _maybe_set_status(event, status)
    _maybe_set_tb_fields(event, thunderbird)
    return event


def build_cycle_events(events: List[CycleEvent], tz, status: str, thunderbird: bool, ascii_only: bool = False) -> List[Event]:
    return [build_cycle_event(ev, tz, status, thunderbird, ascii_only=ascii_only) for ev in events]
