from datetime import datetime, timedelta
from types import SimpleNamespace

from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.engine import _filter_events_to_window, detect_cycles


def test_filter_events_to_window_counts_drops():
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(days=1)

    events = [
        CycleEvent(
            event_type="ingress",
            body="Moon",
            sign="Aries",
            start_time_utc=start - timedelta(hours=1),
            end_time_utc=start - timedelta(hours=1),
        ),
        CycleEvent(
            event_type="ingress",
            body="Moon",
            sign="Taurus",
            start_time_utc=start + timedelta(hours=2),
            end_time_utc=start + timedelta(hours=2),
        ),
    ]

    metrics = {"boundary_drops": 0}
    kept = _filter_events_to_window(events, start, end, metrics)

    assert len(kept) == 1
    assert kept[0].sign == "Taurus"
    assert metrics["boundary_drops"] == 1


def test_detect_cycles_filters_out_of_window_events(monkeypatch):
    start = datetime(2025, 1, 1, 0, 0)
    end = start + timedelta(days=1)

    in_window = CycleEvent(
        event_type="ingress",
        body="Moon",
        sign="Aries",
        start_time_utc=start + timedelta(hours=3),
        end_time_utc=start + timedelta(hours=3),
        source_engine="helionext-cycles",
    )
    out_of_window = CycleEvent(
        event_type="ingress",
        body="Moon",
        sign="Pisces",
        start_time_utc=end + timedelta(hours=5),
        end_time_utc=end + timedelta(hours=5),
        source_engine="helionext-cycles",
    )

    def fake_detector(*args, **kwargs):
        return [in_window, out_of_window]

    monkeypatch.setattr("daily_transit.cycles.engine._run_cycle_detectors", fake_detector)

    cycle_config = CycleConfig(engine="helionext-cycles", cycle_types=["ingress"], chunk_span_days=0)
    config = SimpleNamespace(
        cycle_config=cycle_config,
        planets=[("Moon", "☾")],
        ayanamsa="tropical",
        retrograde_probe_hours=12,
    )

    metrics: dict = {}
    events = detect_cycles(None, None, start, end, config, metrics_out=metrics)

    assert events == [in_window]
    assert metrics.get("boundary_drops", 0) == 1
