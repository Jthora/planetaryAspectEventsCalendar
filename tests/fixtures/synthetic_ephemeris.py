from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from daily_transit.aspect_detection import wrap360


@dataclass
class LinearMotionBody:
    base_degrees: float
    degrees_per_hour: float

    def longitude_at(self, dt: datetime, baseline: datetime) -> float:
        delta_hours = (dt - baseline).total_seconds() / 3600.0
        return wrap360(self.base_degrees + self.degrees_per_hour * delta_hours)


class SyntheticObservation:
    def __init__(self, dt: datetime, body: LinearMotionBody, baseline: datetime):
        self.dt = dt
        self.body = body
        self.baseline = baseline

    def apparent(self):
        return self

    def ecliptic_latlon(self):
        class _LatLon:
            def __init__(self, degrees: float):
                self.degrees = degrees

        return (None, _LatLon(self.body.longitude_at(self.dt, self.baseline)))


class SyntheticEarthAt:
    def __init__(self, dt: datetime, bodies: Dict[str, LinearMotionBody], baseline: datetime):
        self.dt = dt
        self.bodies = bodies
        self.baseline = baseline

    def observe(self, target):
        if isinstance(target, LinearMotionBody):
            body = target
        else:
            body = self.bodies[target]
        return SyntheticObservation(self.dt, body, self.baseline)


class SyntheticEarth:
    def __init__(self, bodies: Dict[str, LinearMotionBody], baseline: datetime):
        self.bodies = bodies
        self.baseline = baseline

    def at(self, dt: datetime):
        return SyntheticEarthAt(dt, self.bodies, self.baseline)


class SyntheticTimescale:
    def utc(self, year: int, month: int, day: int, hour: int, minute: int, second: int):
        return datetime(year, month, day, hour, minute, second)
