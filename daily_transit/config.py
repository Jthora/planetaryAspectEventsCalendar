from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pytz


@dataclass
class GeneratorConfig:
    """Runtime configuration for calendar generation."""
    start_date: datetime
    end_date: datetime
    timezone: pytz.BaseTzInfo
    orb: float
    aspect_degrees: Dict[str, float]
    planets: List[Tuple[str, str]]
    coarse_step_mins: int
    refine_step_mins: int
    merge_window_hours: float
    inclusive_end: bool
    status: str
    thunderbird_friendly: bool
    product_id: str
    verbose: bool
    ascii_only: bool
    retrograde_probe_hours: float
    include_lunar_phases: bool
    timing_debug: bool
    interpretation_mode: str
    engine: str = "legacy"
    mode: str = "standard"
    ayanamsa: str = "tropical"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_m: float = 0.0
    precision_deg: str = "decimal"
    precision_time: str = "seconds"

    @property
    def detection_start(self) -> datetime:
        return self.start_date

    @property
    def detection_end(self) -> datetime:
        return self.end_date
