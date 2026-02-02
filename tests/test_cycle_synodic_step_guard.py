from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.synodic import detect_synodic_phases
from daily_transit.config import GeneratorConfig


def test_synodic_large_jump_triggers_midpoint(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(hours=3)

    def longitude(body, dt):
        progress = (dt - start).total_seconds() / (end - start).total_seconds()
        if body == "A":
            return 0.0
        return 10.0 + 190.0 * progress  # 10° -> 200° across window

    class FakePosition:
        def __init__(self, body, dt):
            self.body = body
            self.dt = dt

        def apparent(self):
            return self

        def ecliptic_latlon(self):
            class Ecl:
                def __init__(self, deg):
                    self.degrees = deg

            return None, Ecl(longitude(self.body, self.dt))

    class FakeEarth:
        def __init__(self):
            self.current_dt = start

        def at(self, _t):
            return self

        def observe(self, body):
            return FakePosition(body, self.current_dt)

    class FakeTimescale:
        def utc(self, y, m, d, h, minute, second):
            return datetime(y, m, d, h, minute, int(second))

    def fake_lon_at(_eph, _ts, earth_obj, body, dt, _pos_cache, _metrics):
        earth_obj.current_dt = dt
        return longitude(body, dt)

    from daily_transit.cycles import synodic as syn

    monkeypatch.setattr(syn, "_lon_at", fake_lon_at)

    eph = {"earth": FakeEarth(), "a": object(), "b": object()}
    ts = FakeTimescale()

    gen_config = GeneratorConfig(
        start_date=start,
        end_date=end,
        timezone=pytz.UTC,
        orb=1.5,
        aspect_degrees={},
        planets=[("A", "A"), ("B", "B")],
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

    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["synodic_phase"], phase_angles=[90.0])

    events = detect_synodic_phases(eph, ts, start, end, gen_config, cycle_config, metrics={})

    assert len(events) == 1
    event_time = events[0].start_time_utc
    assert abs((event_time - datetime(2025, 1, 1, 1, 30)).total_seconds()) < 1000
