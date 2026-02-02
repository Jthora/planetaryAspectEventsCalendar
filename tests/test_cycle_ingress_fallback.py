from datetime import datetime

import pytz
import pytest

from daily_transit.cycles.ingress import _refine_ingress, _adjusted_longitude
from daily_transit.cycles.ingress import TIME_TOLERANCE_SECONDS


class FakeSegment:
    def __init__(self, lon):
        self.lon = lon

    def apparent(self):
        return self

    def ecliptic_latlon(self):
        class Ecl:
            def __init__(self, deg):
                self.degrees = deg
        return None, Ecl(self.lon)


class FakeEarth:
    def __init__(self, lon_map):
        self.lon_map = lon_map

    def at(self, t):
        return self

    def observe(self, body):
        # body is expected to have .lon set by caller
        return FakeSegment(body.lon)


class FakeTimescale:
    def utc(self, y, m, d, h, minute, second):
        return datetime(y, m, d, h, minute, int(second))


class FakeEphemeris(dict):
    def __getitem__(self, key):
        if key == "earth":
            return self["_earth"]
        return self["_body"]


class FakeBody:
    def __init__(self, lon_map):
        self.lon_map = lon_map
        self.lon = None

    def value_at(self, dt):
        if dt in self.lon_map:
            return self.lon_map[dt]
        times = sorted(self.lon_map)
        prev_t, next_t = times[0], times[-1]
        if dt <= prev_t:
            return self.lon_map[prev_t]
        if dt >= next_t:
            return self.lon_map[next_t]
        span = (next_t - prev_t).total_seconds()
        weight = (dt - prev_t).total_seconds() / span
        return self.lon_map[prev_t] + weight * (self.lon_map[next_t] - self.lon_map[prev_t])

    def set_time(self, dt):
        self.lon = self.value_at(dt)


def test_refine_ingress_fallback_sets_uncertainty(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = datetime(2025, 1, 1, 2, 0)
    lon_map = {
        start: 10.0,
        end: 20.0,
    }
    earth = FakeEarth(lon_map)
    body = FakeBody(lon_map)
    eph = FakeEphemeris({"_earth": earth, "_body": body})
    ts = FakeTimescale()

    metrics = {"refine_failures": 0, "pos_cache_hits": 0, "pos_cache_misses": 0, "ephem_calls": 0}

    def fake_lon_at(eph_obj, ts_obj, earth_obj, body_name, dt, pos_cache, metrics_dict):
        body.set_time(dt)
        return body.lon

    # Force signed_min_diff to never cross zero by setting target far away
    monkeypatch.setattr("daily_transit.cycles.ingress._lon_at", fake_lon_at)

    refined_time, refined_adj, delta_seconds, iter_count = _refine_ingress(
        eph,
        ts,
        earth,
        "moon",
        ayanamsa_offset=0.0,
        left=start,
        right=end,
        target_deg=250.0,
        pos_cache={},
        metrics=metrics,
    )

    # Fallback expected: refined time stays within bracket; delta_seconds > tolerance
    assert start <= refined_time <= end
    assert delta_seconds >= TIME_TOLERANCE_SECONDS
    assert metrics["refine_failures"] == 0  # refine_failure increments happen outside wrapper
    assert iter_count <= 14
    assert _adjusted_longitude(lon_map[start], 0.0) <= refined_adj <= _adjusted_longitude(lon_map[end], 0.0)
