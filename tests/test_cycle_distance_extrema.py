import math
from datetime import datetime, timedelta

import pytest
import pytz

from daily_transit.config import GeneratorConfig
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.distance import DistanceUnavailable, detect_distance_extrema
from daily_transit.cycles.engine import detect_cycles


def _base_generator_config(cycle_config: CycleConfig, planets):
    return GeneratorConfig(
        start_date=datetime(2026, 1, 1, 0, 0),
        end_date=datetime(2026, 1, 5, 0, 0),
        timezone=pytz.UTC,
        orb=1.0,
        aspect_degrees={},
        planets=planets,
        coarse_step_mins=60,
        refine_step_mins=10,
        merge_window_hours=1.0,
        inclusive_end=True,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//Test//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=6.0,
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="standard",
        engine="helionext-cycles",
        cycle_config=cycle_config,
    )


def test_distance_extrema_detects_min_and_max(monkeypatch):
    start = datetime(2026, 1, 1, 0, 0)
    end = start + timedelta(days=3)
    cycle_cfg = CycleConfig(engine="helionext-cycles", cycle_types=["perihelion_aphelion"], merge_window_hours=None)
    gen_config = _base_generator_config(cycle_cfg, planets=[("Mars", "Ma")])

    def fake_distance(_eph, _ts, _earth, _body, dt):
        days = (dt - start).total_seconds() / 86400.0
        return 1.0 + 0.2 * math.cos(math.pi * days)

    monkeypatch.setattr("daily_transit.cycles.distance._distance_au", fake_distance)

    eph = {"earth": object(), "mars": object()}
    metrics: dict = {}
    events = detect_distance_extrema(eph, object(), start, end, gen_config, cycle_cfg, metrics)

    assert [ev.event_type for ev in events] == ["perihelion", "aphelion"]
    assert events[0].body == "Mars"
    assert abs((events[0].start_time_utc - (start + timedelta(days=1))).total_seconds()) < 60
    assert metrics["refine_calls"] == 2
    assert metrics["refine_iterations"] > 0
    assert all(ev.uncertainty_seconds is None for ev in events)


def test_distance_extrema_respects_missing_body_policy(monkeypatch):
    start = datetime(2026, 1, 1, 0, 0)
    end = start + timedelta(days=3)

    def always_missing(*_args, **_kwargs):
        raise DistanceUnavailable("missing")

    monkeypatch.setattr("daily_transit.cycles.distance._distance_au", always_missing)

    fail_cfg = CycleConfig(engine="helionext-cycles", cycle_types=["perihelion_aphelion"], missing_body_policy="fail")
    fail_config = _base_generator_config(fail_cfg, planets=[("Missing", "")])
    eph = {"earth": object()}

    with pytest.raises(KeyError):
        detect_cycles(eph, object(), start, end, fail_config)

    skip_cfg = CycleConfig(engine="helionext-cycles", cycle_types=["perihelion_aphelion"], missing_body_policy="skip")
    skip_config = _base_generator_config(skip_cfg, planets=[("Missing", "")])
    metrics_out: dict = {}
    events = detect_cycles(eph, object(), start, end, skip_config, metrics_out)

    assert events == []
    assert metrics_out.get("distance_skipped_missing", 0) == 1
