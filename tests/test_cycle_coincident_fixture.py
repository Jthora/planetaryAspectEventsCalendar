from datetime import datetime

import pytz

from daily_transit.config import GeneratorConfig
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent
import daily_transit.cycles.engine as engine_module


def _base_generator_config(cycle_config: CycleConfig) -> GeneratorConfig:
    return GeneratorConfig(
        start_date=datetime(2026, 1, 1, 0, 0),
        end_date=datetime(2026, 1, 2, 0, 0),
        timezone=pytz.UTC,
        orb=1.0,
        aspect_degrees={},
        planets=[("Mars", "")],
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


def test_coincident_ingress_and_station_both_emitted(monkeypatch):
    ts = datetime(2026, 1, 1, 12, 0)
    ingress = CycleEvent(event_type="ingress", body="Mars", sign="Aries", start_time_utc=ts, end_time_utc=ts)
    station = CycleEvent(
        event_type="station",
        body="Mars",
        station_direction="forward_to_retro",
        start_time_utc=ts,
        end_time_utc=ts,
    )

    def fake_ingresses(*_args, **_kwargs):
        return [ingress]

    def fake_synodic(*_args, **_kwargs):
        return []

    def fake_retro(*_args, **_kwargs):
        return [station]

    monkeypatch.setattr(engine_module, "detect_ingresses", fake_ingresses)
    monkeypatch.setattr(engine_module, "detect_synodic_phases", fake_synodic)
    monkeypatch.setattr(engine_module, "detect_retro_and_stations", fake_retro)

    cfg = CycleConfig(engine="helionext-cycles", cycle_types=["ingress", "station"], merge_window_hours=None)
    gen_cfg = _base_generator_config(cfg)

    events = engine_module.detect_cycles(None, None, ts, ts, gen_cfg)
    assert len(events) == 2
    assert events[0].event_type == "ingress"
    assert events[1].event_type == "station"
