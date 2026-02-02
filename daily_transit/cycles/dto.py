from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

EVENT_TYPE_ORDER = {
    "ingress": 1,
    "ingress_span": 2,
    "synodic_phase": 3,
    "synodic_phase_span": 4,
    "retro_interval": 5,
    "station": 6,
    "perihelion": 7,
    "aphelion": 8,
    "node": 9,
    "apogee": 10,
    "perigee": 11,
}


@dataclass
class CycleEvent:
    """DTO for cycle events produced by the cycle engine."""

    event_type: str
    start_time_utc: datetime
    end_time_utc: Optional[datetime] = None
    body: Optional[str] = None
    body1: Optional[str] = None
    body2: Optional[str] = None
    sign: Optional[str] = None
    start_sign: Optional[str] = None
    end_sign: Optional[str] = None
    phase_angle: Optional[float] = None
    phase_start_deg: Optional[float] = None
    phase_end_deg: Optional[float] = None
    retrograde: Optional[bool] = None
    station_direction: Optional[str] = None
    station_strength: Optional[float] = None
    distance_au: Optional[float] = None
    ayanamsa_mode: str = "tropical"
    retro_probe_hours: Optional[float] = None
    uncertainty_seconds: Optional[float] = None
    convergence_status: Optional[str] = None
    separation_deg: Optional[float] = None
    delta_deg: Optional[float] = None
    source_engine: str = "helionext-cycles"
    schema_version: str = "v1"
    merge_window_seconds: Optional[float] = None
    computation_notes: Optional[str] = None
    raw_longitude: Optional[float] = None
    adjusted_longitude: Optional[float] = None
    raw_longitude_body2: Optional[float] = None
    adjusted_longitude_body2: Optional[float] = None


def cycle_sort_key(ev: CycleEvent):
    event_rank = EVENT_TYPE_ORDER.get(ev.event_type, 999)
    return (
        ev.start_time_utc,
        event_rank,
        ev.body or ev.body1 or "",
        ev.body2 or "",
        ev.phase_angle if ev.phase_angle is not None else -1.0,
    )


def validate_cycle_event(ev: CycleEvent):
    if not ev.event_type:
        raise ValueError("CycleEvent missing event_type")
    if ev.start_time_utc is None:
        raise ValueError("CycleEvent missing start_time_utc")

    et = ev.event_type
    if et == "ingress":
        if not ev.body or not ev.sign:
            raise ValueError("Ingress event requires body and sign")
    elif et == "ingress_span":
        if not ev.body or not ev.sign or ev.end_time_utc is None:
            raise ValueError("Ingress span requires body, sign, and end_time_utc")
        if ev.end_time_utc <= ev.start_time_utc:
            raise ValueError("Ingress span must have end_time_utc after start_time_utc")
    elif et == "synodic_phase":
        if not ev.body1 or not ev.body2 or ev.phase_angle is None:
            raise ValueError("Synodic phase requires body1, body2, and phase_angle")
        # Attach separation fields for transparency
        if ev.separation_deg is None:
            raise ValueError("Synodic phase missing separation_deg")
    elif et == "synodic_phase_span":
        if not ev.body1 or not ev.body2 or ev.phase_start_deg is None or ev.phase_end_deg is None:
            raise ValueError("Synodic phase span requires body1, body2, phase_start_deg, phase_end_deg")
        if ev.end_time_utc is None or ev.end_time_utc <= ev.start_time_utc:
            raise ValueError("Synodic phase span must have end_time_utc after start_time_utc")
    elif et == "retro_interval":
        if not ev.body or ev.end_time_utc is None:
            raise ValueError("Retro interval requires body and end_time_utc")
    elif et == "station":
        if not ev.body or not ev.station_direction:
            raise ValueError("Station requires body and station_direction")
    elif et in {"perihelion", "aphelion"}:
        if not ev.body:
            raise ValueError("Perihelion/aphelion require body")
    elif et in {"node", "apogee", "perigee"}:
        if not ev.body:
            raise ValueError(f"{et} event requires body")
    # Optional: add additional validations as new types arrive
