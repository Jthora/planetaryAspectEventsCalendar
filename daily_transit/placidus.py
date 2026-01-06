from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Tuple

import astropy.units as u
from astropy.coordinates import AltAz, EarthLocation, SkyCoord, GeocentricTrueEcliptic
from astropy.time import Time

from .aspect_detection import wrap360


def _divide_quadrant(start: float, end: float) -> List[float]:
    span = (end - start + 360.0) % 360.0
    first = wrap360(start + span / 3.0)
    second = wrap360(start + 2.0 * span / 3.0)
    return [first, second]


_cusp_cache: Dict[Tuple[datetime, float, float, float], List[float]] = {}


def _compute_cusps_core(dt: datetime, latitude: float, longitude: float, elevation_m: float) -> List[float]:
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=elevation_m * u.m)
    t = Time(dt, scale="utc")

    # Ascendant from eastern horizon intersection with ecliptic
    altaz_frame = AltAz(obstime=t, location=location)
    east_point = SkyCoord(az=90 * u.deg, alt=0 * u.deg, frame=altaz_frame)
    asc = wrap360(east_point.transform_to(GeocentricTrueEcliptic(equinox=t)).lon.deg)

    # Midheaven from local sidereal time projected onto ecliptic
    lst = t.sidereal_time("apparent", longitude=location.lon)
    mc_icrs = SkyCoord(ra=lst, dec=0 * u.deg, frame="icrs")
    mc = wrap360(mc_icrs.transform_to(GeocentricTrueEcliptic(equinox=t)).lon.deg)

    desc = wrap360(asc + 180.0)
    ic = wrap360(mc + 180.0)

    c11, c12 = _divide_quadrant(mc, asc)
    c2, c3 = _divide_quadrant(asc, ic)
    c5, c6 = _divide_quadrant(ic, desc)
    c8, c9 = _divide_quadrant(desc, mc)

    cusps = [asc, c2, c3, ic, c5, c6, desc, c8, c9, mc, c11, c12]
    return cusps


def placidus_cusps(dt: datetime, latitude: float, longitude: float, elevation_m: float = 0.0) -> List[float]:
    """Compute Placidus-like cusps using astropy and Porphyry quadrant division.

    Returns list of 12 cusp longitudes in degrees [C1..C12]. Raises on failure.
    Note: Intermediate cusps are derived by trisection of the ASC–IC–DSC–MC quadrants
    (Porphyry-style) as an approximate stand-in until full Placidus time division is added.
    """
    try:
        key_dt = dt.replace(minute=0, second=0, microsecond=0)
        cache_key = (key_dt, float(latitude), float(longitude), float(elevation_m))
        if cache_key in _cusp_cache:
            logging.debug("Placidus cusps cache hit for %s", cache_key)
            return _cusp_cache[cache_key]

        cusps = _compute_cusps_core(dt, latitude, longitude, elevation_m)

        if len(cusps) != 12:
            raise ValueError("Unexpected cusp count")
        if any(not (0.0 <= c < 360.0) for c in cusps):
            raise ValueError("Invalid cusp value")

        _cusp_cache[cache_key] = cusps
        return cusps
    except Exception as exc:
        logging.error("Placidus cusp computation failed: %s", exc)
        raise
