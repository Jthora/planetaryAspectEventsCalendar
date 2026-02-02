from __future__ import annotations

import argparse
from typing import List, Optional

from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.step_override_defaults import (
    DEFAULT_INGRESS_STEP_OVERRIDES,
    DEFAULT_SYNODIC_PAIR_STEP_OVERRIDES,
)
from daily_transit.cycles.step_tables import synodic_pair_key

ALLOWED_CYCLE_TYPES = {
    "ingress",
    "synodic_phase",
    "retro_interval",
    "station",
    "perihelion_aphelion",
    "lunar_node",
    "lunar_apogee",
    "lunar_perigee",
}

ALLOWED_SIGNS = (
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
)

DEFAULT_CYCLE_TYPES = (
    "ingress",
    "synodic_phase",
    "retro_interval",
    "station",
)

DEFAULT_PHASE_ANGLES = (0.0, 90.0, 180.0, 270.0)
CHUNK_SPAN_DEFAULT_DAYS = 180
POS_CACHE_MAX_DEFAULT = 150000
SEP_CACHE_MAX_DEFAULT = 80000
LONG_MODE_CHUNK_DAYS = 720
LONG_MODE_POS_CACHE = 500000
LONG_MODE_SEP_CACHE = 300000
LONG_MODE_PHASE_ANGLES = (0.0, 180.0)


def _parse_comma_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [token.strip() for token in raw.split(',') if token.strip()]


def parse_cycle_types(raw: Optional[str]) -> List[str]:
    tokens = _parse_comma_list(raw)
    if not tokens:
        return list(DEFAULT_CYCLE_TYPES)
    normalized: List[str] = []
    unknown: List[str] = []
    for token in tokens:
        key = token.lower()
        if key not in ALLOWED_CYCLE_TYPES:
            unknown.append(token)
            continue
        if key not in normalized:
            normalized.append(key)
    if unknown:
        allowed = ",".join(sorted(ALLOWED_CYCLE_TYPES))
        raise SystemExit(
            f"Unsupported cycle type(s): {', '.join(unknown)}. Allowed: {allowed}."
        )
    return normalized


def parse_phase_angles(raw: Optional[str]) -> List[float]:
    tokens = _parse_comma_list(raw)
    if not tokens:
        return list(DEFAULT_PHASE_ANGLES)
    angles: List[float] = []
    for token in tokens:
        try:
            value = float(token)
        except ValueError:
            raise SystemExit(f"Phase angle must be numeric: {token}")
        if not (0.0 <= value <= 360.0):
            raise SystemExit(f"Phase angle out of range [0,360]: {value}")
        rounded = round(value, 6)
        if rounded not in angles:
            angles.append(rounded)
    return sorted(angles)


def parse_ingress_signs(raw: Optional[str]) -> Optional[List[str]]:
    tokens = _parse_comma_list(raw)
    if not tokens:
        return None
    normalized: List[str] = []
    unknown: List[str] = []
    allowed = {s.lower(): s for s in ALLOWED_SIGNS}
    for token in tokens:
        key = token.strip().lower()
        if key not in allowed:
            unknown.append(token)
            continue
        value = allowed[key]
        if value not in normalized:
            normalized.append(value)
    if unknown:
        raise SystemExit(
            f"Unsupported ingress sign(s): {', '.join(unknown)}. Allowed: {', '.join(ALLOWED_SIGNS)}."
        )
    return normalized


def parse_cycle_planets(raw: Optional[str]) -> Optional[List[str]]:
    tokens = _parse_comma_list(raw)
    return tokens if tokens else None


def parse_synodic_pairs(raw: Optional[str]) -> Optional[List[str]]:
    tokens = _parse_comma_list(raw)
    if not tokens:
        return None
    normalized: List[str] = []
    for token in tokens:
        if "|" not in token:
            raise SystemExit("synodic pair must use 'Body|Body' format")
        a, b = [part.strip() for part in token.split("|", 1)]
        if not a or not b:
            raise SystemExit(f"Invalid synodic pair token: {token}")
        key = synodic_pair_key(a, b)
        if key not in normalized:
            normalized.append(key)
    return normalized


def build_cycle_config_from_args(args: argparse.Namespace) -> Optional[CycleConfig]:
    engine = getattr(args, "cycle_engine", "off")
    if engine == "off":
        return None
    cycle_types = parse_cycle_types(getattr(args, "cycle_types", None))
    raw_phase_angles = getattr(args, "cycle_phase_angles", None)
    long_span_mode = bool(getattr(args, "cycle_long_span_mode", False))
    if long_span_mode and not raw_phase_angles:
        phase_angles = list(LONG_MODE_PHASE_ANGLES)
    else:
        phase_angles = parse_phase_angles(raw_phase_angles)
    ingress_signs = parse_ingress_signs(getattr(args, "cycle_ingress_signs", None))
    retro_probe = (
        args.cycle_retro_probe_hours
        if getattr(args, "cycle_retro_probe_hours", None) is not None
        else getattr(args, "retrograde_probe_hours", None)
    )
    if retro_probe is not None and retro_probe <= 0:
        raise SystemExit("retro/probe hours must be > 0")
    if retro_probe is not None and retro_probe > 72:
        raise SystemExit("retro/probe hours must be <= 72 to avoid runaway scans")
    chunk_span = getattr(args, "cycle_chunk_span_days", None)
    if chunk_span is None:
        chunk_span = LONG_MODE_CHUNK_DAYS if long_span_mode else CHUNK_SPAN_DEFAULT_DAYS

    pos_cache_max = getattr(args, "cycle_pos_cache_max", None)
    if pos_cache_max is None:
        pos_cache_max = LONG_MODE_POS_CACHE if long_span_mode else POS_CACHE_MAX_DEFAULT
    sep_cache_max = getattr(args, "cycle_sep_cache_max", None)
    if sep_cache_max is None:
        sep_cache_max = LONG_MODE_SEP_CACHE if long_span_mode else SEP_CACHE_MAX_DEFAULT
    if pos_cache_max is not None and pos_cache_max <= 0:
        pos_cache_max = None
    if sep_cache_max is not None and sep_cache_max <= 0:
        sep_cache_max = None

    retro_padding_days = getattr(args, "cycle_retro_padding_days", 0.0) or 0.0
    if retro_padding_days < 0:
        raise SystemExit("cycle-retro-padding-days must be non-negative")
    clamp_intervals = bool(getattr(args, "cycle_clamp_intervals", False))
    derive_spans = bool(getattr(args, "cycle_derive_spans", False))
    cycle_planets = parse_cycle_planets(getattr(args, "cycle_planets", None))
    synodic_pairs = parse_synodic_pairs(getattr(args, "cycle_synodic_pairs", None))
    raw_step_scale = getattr(args, "cycle_synodic_step_scale", None)
    synodic_step_scale = float(raw_step_scale) if raw_step_scale is not None else (2.0 if long_span_mode else 1.0)
    if synodic_step_scale <= 0:
        raise SystemExit("cycle-synodic-step-scale must be > 0")
    synodic_mode = getattr(args, "cycle_synodic_mode", None) or ("conjunction_only" if long_span_mode else "phases")
    synodic_max_delta = float(getattr(args, "cycle_synodic_max_delta_deg", 3.0) or 3.0)
    if synodic_max_delta <= 0:
        raise SystemExit("cycle-synodic-max-delta-deg must be > 0")
    synodic_step_cap = int(getattr(args, "cycle_synodic_step_cap_minutes", 180) or 180)
    if synodic_step_cap <= 0:
        raise SystemExit("cycle-synodic-step-cap-minutes must be > 0")
    cycle_progress = not bool(getattr(args, "cycle_no_progress", False))

    return CycleConfig(
        engine=engine,
        cycle_types=cycle_types,
        phase_angles=phase_angles,
        ingress_signs=ingress_signs,
        merge_window_hours=getattr(args, "cycle_merge_window_hours", None),
        retro_probe_hours=retro_probe,
        chunk_span_days=chunk_span,
        pos_cache_max_entries=pos_cache_max,
        sep_cache_max_entries=sep_cache_max,
        missing_body_policy=getattr(args, "cycle_missing_body_policy", "fail"),
        ayanamsa=getattr(args, "ayanamsa", None),
        timing_debug=getattr(args, "cycle_timing_debug", False),
        metrics_path=getattr(args, "cycle_metrics_path", None),
        ingress_step_overrides=DEFAULT_INGRESS_STEP_OVERRIDES.copy(),
        synodic_pair_step_overrides=DEFAULT_SYNODIC_PAIR_STEP_OVERRIDES.copy(),
        retro_padding_days=retro_padding_days,
        clamp_intervals=clamp_intervals,
        derive_spans=derive_spans,
        cycle_planets=cycle_planets,
        synodic_pairs=synodic_pairs,
        synodic_step_scale=synodic_step_scale,
        long_span_mode=long_span_mode,
        cycle_progress=cycle_progress,
        synodic_mode=synodic_mode,
        synodic_max_delta_deg=synodic_max_delta,
        synodic_step_cap_minutes=synodic_step_cap,
    )
