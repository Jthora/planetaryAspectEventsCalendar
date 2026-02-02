from datetime import datetime

import pytz
import pytest

from daily_transit.config import GeneratorConfig
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.engine import detect_cycles
import daily_transit.cycles.engine as engine_module


def _base_generator_config(cycle_config: CycleConfig) -> GeneratorConfig:
    return GeneratorConfig(
        start_date=datetime(2026, 1, 1, 0, 0),
        end_date=datetime(2026, 1, 2, 0, 0),
        timezone=pytz.UTC,
        orb=1.0,
        aspect_degrees={},
        planets=[("Missing", "")],
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


def test_missing_body_policy_fail_raises(monkeypatch):
    cycle_cfg = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], missing_body_policy="fail")

    def _missing(*_args, **_kwargs):
        raise KeyError("Ephemeris missing body Missing")

    monkeypatch.setattr(engine_module, "detect_ingresses", _missing)

    with pytest.raises(KeyError):
        detect_cycles(None, None, datetime(2026, 1, 1), datetime(2026, 1, 2), _base_generator_config(cycle_cfg))


def test_missing_body_policy_skip_swallowed(monkeypatch):
    cycle_cfg = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], missing_body_policy="skip")

    def _missing(*_args, **_kwargs):
        raise KeyError("Ephemeris missing body Missing")

    monkeypatch.setattr(engine_module, "detect_ingresses", _missing)

    events = detect_cycles(None, None, datetime(2026, 1, 1), datetime(2026, 1, 2), _base_generator_config(cycle_cfg))
    assert events == []
