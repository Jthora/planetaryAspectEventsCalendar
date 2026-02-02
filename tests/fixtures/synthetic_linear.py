from datetime import datetime
from typing import Dict

from daily_transit.aspect_detection import wrap360


def linear_lon_fn(start_lons: Dict[str, float], rates_deg_per_hour: Dict[str, float]):
    """Create a synthetic longitude function with constant rates per body."""

    def lon_at(body: str, dt: datetime, epoch: datetime) -> float:
        if body not in start_lons or body not in rates_deg_per_hour:
            raise KeyError(f"Missing body {body} in synthetic ephemeris")
        hours = (dt - epoch).total_seconds() / 3600.0
        return wrap360(start_lons[body] + rates_deg_per_hour[body] * hours)

    return lon_at
