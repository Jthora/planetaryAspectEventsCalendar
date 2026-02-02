from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.synodic import detect_synodic_phases
from daily_transit.cycles.ingress import detect_ingresses
from daily_transit.config import GeneratorConfig
from tests.fixtures.synthetic_linear import linear_lon_fn


def _seed_metrics():
    return {
        "refine_calls": 0,
        "refine_iterations": 0,
        "refine_failures": 0,
        "pos_cache_hits": 0,
        "pos_cache_misses": 0,
        "ephem_calls": 0,
        "sep_cache_hits": 0,
        "sep_cache_misses": 0,
    }


def _make_generator_config(planets):
    return GeneratorConfig(
        start_date=None,
        end_date=None,
        timezone=pytz.UTC,
        orb=1.5,
        aspect_degrees={},
        planets=planets,
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


def test_linear_ingress_finds_expected_time(monkeypatch):
    epoch = datetime(2025, 1, 1, 0, 0)
    end = epoch + timedelta(hours=1)
    lon_fn = linear_lon_fn({"Moon": 25.0}, {"Moon": 30.0})  # 30 deg/hour; crosses Taurus at ~10 minutes

    def fake_lon_at(eph, ts, earth, body, dt, pos_cache, metrics):
        return lon_fn(body, dt, epoch)

    monkeypatch.setattr("daily_transit.cycles.ingress._lon_at", fake_lon_at)

    gen_config = _make_generator_config([("Moon", "Mo")])
    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], merge_window_hours=None)

    class DummyEarth:
        pass

    eph = {"earth": DummyEarth()}

    events = detect_ingresses(eph, None, epoch, end, gen_config, cycle_config, metrics=_seed_metrics())

    assert any(ev.sign == "Taurus" for ev in events)
    times = [ev.start_time_utc for ev in events if ev.sign == "Taurus"]
    assert times
    for t in times:
        assert epoch <= t <= epoch + timedelta(minutes=20)


def test_linear_ingress_ayanamsa_shift(monkeypatch):
    epoch = datetime(2025, 1, 1, 0, 0)
    end = epoch + timedelta(hours=2)
    lon_fn = linear_lon_fn({"Moon": 25.0}, {"Moon": 30.0})

    def fake_lon_at(eph, ts, earth, body, dt, pos_cache, metrics):
        return lon_fn(body, dt, epoch)

    monkeypatch.setattr("daily_transit.cycles.ingress._lon_at", fake_lon_at)
    monkeypatch.setattr("daily_transit.ayanamsa.get_ayanamsa_offset", lambda dt, mode: 24.0)

    gen_config = _make_generator_config([("Moon", "Mo")])
    tropical_cycle = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], merge_window_hours=None)
    sidereal_cycle = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], merge_window_hours=None, ayanamsa="galactic_core")

    class DummyEarth:
        pass

    eph = {"earth": DummyEarth()}

    tropical_events = detect_ingresses(eph, None, epoch, end, gen_config, tropical_cycle, metrics=_seed_metrics())
    sidereal_events = detect_ingresses(eph, None, epoch, end, gen_config, sidereal_cycle, metrics=_seed_metrics())

    trop_times = sorted(ev.start_time_utc for ev in tropical_events if ev.sign == "Taurus")
    sidereal_times = sorted(ev.start_time_utc for ev in sidereal_events if ev.sign == "Taurus")
    assert trop_times and sidereal_times
    assert sidereal_times[0] > trop_times[0]  # offset delays Taurus ingress crossing


def test_linear_synodic_phase_time(monkeypatch):
    epoch = datetime(2025, 1, 1, 0, 0)
    end = epoch + timedelta(hours=3)
    lon_fn = linear_lon_fn({"Sun": 0.0, "Moon": 170.0}, {"Sun": 1.0, "Moon": 13.0})

    def fake_lon_at(eph, ts, earth, body, dt, pos_cache, metrics):
        return lon_fn(body, dt, epoch)

    monkeypatch.setattr("daily_transit.cycles.synodic._lon_at", fake_lon_at)

    gen_config = _make_generator_config([("Sun", "Su"), ("Moon", "Mo")])
    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["synodic_phase"], phase_angles=[180.0])

    class DummyEarth:
        pass

    eph = {"earth": DummyEarth()}

    events = detect_synodic_phases(eph, None, epoch, end, gen_config, cycle_config, metrics=_seed_metrics())

    assert any(ev.phase_angle == 180.0 for ev in events)
    times = [ev.start_time_utc for ev in events if ev.phase_angle == 180.0]
    assert times
    expected = epoch + timedelta(minutes=50)  # (180-170)/12 deg/hr = 50 minutes
    for t in times:
        assert abs((t - expected).total_seconds()) <= 10 * 60  # within 10 minutes tolerance
