from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.ingress import detect_ingresses
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent
from daily_transit.config import GeneratorConfig


class SyntheticAyanamsa:
    def __call__(self, dt: datetime) -> float:
        return 0.0


def test_moon_double_cross_midpoint_catches_ingress(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(hours=3)

    # Synthetic ephemeris: longitude jumps from 29° to 80° between samples (crossing Aries -> Taurus)
    samples = {
        datetime(2025, 1, 1, 0, 0): 29.0,
        datetime(2025, 1, 1, 3, 0): 80.0,
        datetime(2025, 1, 1, 1, 30): 40.0,  # midpoint guard should sample here
    }

    class FakePosition:
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
        def at(self, t):
            return self

        def observe(self, body):
            return FakePosition(body.lon)

    class FakeTimescale:
        def utc(self, y, m, d, h, minute, second):
            return datetime(y, m, d, h, minute, int(second))

    class FakeEphemeris(dict):
        def __getitem__(self, key):
            if key == "earth":
                return FakeEarth()
            if key == "moon":
                return FakePosition(self._current_lon)
            raise KeyError(key)

    eph = FakeEphemeris()
    ts = FakeTimescale()

    sorted_times = sorted(samples)

    def sample_lon(dt: datetime) -> float:
        if dt in samples:
            return samples[dt]
        earlier = [t for t in sorted_times if t <= dt]
        later = [t for t in sorted_times if t >= dt]
        prev_t = max(earlier) if earlier else later[0]
        next_t = min(later) if later else prev_t
        if next_t == prev_t:
            return samples[prev_t]
        span = (next_t - prev_t).total_seconds()
        weight = (dt - prev_t).total_seconds() / span
        return samples[prev_t] + weight * (samples[next_t] - samples[prev_t])

    def fake_lon_at(_, __, ___, body, dt, ____pos_cache, _____metrics):
        lon = sample_lon(dt)
        eph._current_lon = lon
        return lon

    monkeypatch.setattr("daily_transit.cycles.ingress._lon_at", fake_lon_at)

    gen_config = GeneratorConfig(
        start_date=start,
        end_date=end,
        timezone=pytz.UTC,
        orb=1.5,
        aspect_degrees={},
        planets=[("Moon", "Mo")],
        coarse_step_mins=180,
        refine_step_mins=5,
        merge_window_hours=4,
        inclusive_end=False,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//test//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=6.0,
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="standard",
        engine="helionext",
        engine_factory=None,
        mode="standard",
        ayanamsa="tropical",
        latitude=None,
        longitude=None,
        elevation_m=0.0,
        precision_deg="decimal",
        precision_time="seconds",
        cycle_config=None,
        aspect_meanings={},
        args=None,
        build_cycle_events=None,
        event_sort_key=None,
        compute_body_longitudes_fn=None,
        assign_houses_fn=None,
    )

    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], merge_window_hours=None)

    metrics = {
        "refine_calls": 0,
        "refine_iterations": 0,
        "refine_failures": 0,
        "pos_cache_hits": 0,
        "pos_cache_misses": 0,
        "ephem_calls": 0,
    }

    events = detect_ingresses(eph, ts, start, end, gen_config, cycle_config, metrics=metrics)
    taurus_events = [ev for ev in events if ev.sign == "Taurus"]
    assert taurus_events
    assert all(start <= ev.start_time_utc <= end for ev in taurus_events)
