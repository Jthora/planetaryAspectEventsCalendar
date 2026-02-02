from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CycleConfig:
    """Configuration for cycle detection and ICS rendering."""

    engine: str = "off"  # off, helionext-cycles (or other engines as added)
    cycle_types: Optional[List[str]] = None  # e.g., ["ingress", "synodic_phase", "retro_interval", "station"]
    phase_angles: Optional[List[float]] = None  # degrees, sorted and deduped
    ingress_signs: Optional[List[str]] = None  # subset of 12 signs; None means all
    merge_window_hours: Optional[float] = None  # per-event-type merge window; None uses defaults per type
    retro_probe_hours: Optional[float] = None  # fallback to aspect retro probe if None
    chunk_span_days: int = 180  # max span per processing chunk for long ranges (set 0 or <0 to disable chunking)
    ingress_step_overrides: Optional[Dict[str, int]] = None  # optional per-body ingress step minutes
    synodic_pair_step_overrides: Optional[Dict[str, int]] = None  # optional per-pair synodic step minutes keyed by sorted "Body|Body"
    pos_cache_max_entries: Optional[int] = None  # optional cap for position cache (None or <=0 means unbounded)
    sep_cache_max_entries: Optional[int] = None  # optional cap for separation cache (None or <=0 means unbounded)
    missing_body_policy: str = "fail"  # fail | skip
    ayanamsa: Optional[str] = None  # override for cycles; None uses global config
    timing_debug: bool = False
    metrics_path: Optional[str] = None  # optional JSON metrics output
    retro_padding_days: float = 0.0  # optional padding applied to retro detection window
    clamp_intervals: bool = False  # clamp overlapping retro intervals to window
    derive_spans: bool = False  # emit derived spans (ingress_span, synodic_phase_span)
    cycle_planets: Optional[List[str]] = None  # optional planets whitelist for cycles only
    synodic_pairs: Optional[List[str]] = None  # optional normalized synodic pair keys
    synodic_step_scale: float = 1.0  # multiplier applied to synodic scan step minutes
    long_span_mode: bool = False  # enable coarse defaults for century-scale runs
    cycle_progress: bool = True  # emit progress heartbeat by default
    synodic_mode: str = "phases"  # phases | conjunction_only
    synodic_max_delta_deg: float = 3.0  # drop synodic hits exceeding this delta
    synodic_step_cap_minutes: int = 180  # cap step size even when scaling
