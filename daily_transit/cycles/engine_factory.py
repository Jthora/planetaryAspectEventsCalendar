from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List

from daily_transit.config import GeneratorConfig
from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.engine import detect_cycles


@dataclass
class CycleDetectionEngine:
    name: str
    detector: Callable[[object, object, datetime, datetime, GeneratorConfig], List[CycleEvent]]

    def detect(self, eph, ts, config: GeneratorConfig, detection_end: datetime) -> List[CycleEvent]:
        return self.detector(eph, ts, config.start_date, detection_end, config)


def _helionext_cycle_detector(eph, ts, start_dt: datetime, end_dt: datetime, config: GeneratorConfig) -> List[CycleEvent]:
    return detect_cycles(eph, ts, start_dt, end_dt, config)


_CYCLE_ENGINE_MAP = {
    "helionext-cycles": CycleDetectionEngine(name="helionext-cycles", detector=_helionext_cycle_detector),
}


def get_cycle_detection_engine(name: str) -> CycleDetectionEngine:
    key = (name or "off").lower()
    if key == "off":
        raise ValueError("Cycle engine is off; enable with --cycle-engine")
    if key not in _CYCLE_ENGINE_MAP:
        raise ValueError(f"Unsupported cycle engine '{name}'. Choose from: {', '.join(_CYCLE_ENGINE_MAP.keys())}")
    return _CYCLE_ENGINE_MAP[key]
