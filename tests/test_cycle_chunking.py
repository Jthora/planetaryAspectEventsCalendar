from datetime import datetime, timedelta
from types import SimpleNamespace

from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.engine import detect_cycles


def test_chunking_dedupes_overlap(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(days=2)

    def fake_ingresses(eph, ts, start_dt, end_dt, config, cycle_config, metrics, pos_cache=None, sep_cache=None):
        return [
            CycleEvent(
                event_type="ingress",
                body="Moon",
                sign="Aries",
                start_time_utc=datetime(2025, 1, 1, 18, 0),
                end_time_utc=datetime(2025, 1, 1, 18, 0),
                ayanamsa_mode=cycle_config.ayanamsa or "tropical",
                source_engine=cycle_config.engine,
            )
        ]

    def empty_detector(*args, **kwargs):
        return []

    monkeypatch.setattr("daily_transit.cycles.engine.detect_ingresses", fake_ingresses)
    monkeypatch.setattr("daily_transit.cycles.engine.detect_synodic_phases", empty_detector)
    monkeypatch.setattr("daily_transit.cycles.engine.detect_retro_and_stations", empty_detector)
    monkeypatch.setattr("daily_transit.cycles.engine.detect_distance_extrema", empty_detector)

    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], chunk_span_days=1)
    config = SimpleNamespace(cycle_config=cycle_config)

    metrics: dict = {}
    events = detect_cycles(None, None, start, end, config, metrics_out=metrics)

    assert len(events) == 1
    assert events[0].start_time_utc == datetime(2025, 1, 1, 18, 0)
    assert metrics.get("ephem_calls", 0) == 0
