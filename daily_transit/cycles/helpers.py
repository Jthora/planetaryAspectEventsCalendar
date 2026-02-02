from __future__ import annotations

from daily_transit.aspect_detection import wrap360
from daily_transit.zodiac_metadata import sign_from_longitude


def sign_after_ayanamsa(longitude_deg: float) -> str:
    """Return zodiac sign after normalising longitude to [0, 360).

    This is explicitly wrap-safe for values near 0/360, avoiding negative-angle
    surprises when an ayanamsa offset pushes longitudes below zero.
    """

    normalised = wrap360(longitude_deg)
    return sign_from_longitude(normalised)
