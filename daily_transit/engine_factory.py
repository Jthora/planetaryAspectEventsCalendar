from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, List

from .aspect_detection import AspectEvent, detect_aspects as legacy_detect
from .config import GeneratorConfig
from .helionext.engine import detect_aspects as helionext_detect


@dataclass
class DetectionEngine:
    name: str
    detector: Callable[[object, object, datetime, datetime, GeneratorConfig], List[AspectEvent]]

    def detect(self, eph, ts, config: GeneratorConfig, detection_end: datetime) -> List[AspectEvent]:
        return self.detector(eph, ts, config.start_date, detection_end, config)


def _legacy_detector(eph, ts, start_dt: datetime, end_dt: datetime, config: GeneratorConfig) -> List[AspectEvent]:
    return legacy_detect(
        eph,
        ts,
        start_dt,
        end_dt,
        config.orb,
        config.aspect_degrees,
        config.planets,
        config.coarse_step_mins,
        config.refine_step_mins,
        config.merge_window_hours,
        config.retrograde_probe_hours,
        timing_debug=config.timing_debug,
    )


def _helionext_detector(eph, ts, start_dt: datetime, end_dt: datetime, config: GeneratorConfig) -> List[AspectEvent]:
    return helionext_detect(eph, ts, start_dt, end_dt, config)


_ENGINE_MAP = {
    "legacy": DetectionEngine(name="legacy", detector=_legacy_detector),
    "helionext": DetectionEngine(name="helionext", detector=_helionext_detector),
}


def get_detection_engine(name: str) -> DetectionEngine:
    key = (name or "legacy").lower()
    if key not in _ENGINE_MAP:
        raise ValueError(f"Unsupported engine '{name}'. Choose from: {', '.join(_ENGINE_MAP.keys())}")
    return _ENGINE_MAP[key]
