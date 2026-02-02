from datetime import datetime, timedelta

import pytz

from daily_transit.cycles.dto import CycleEvent
from daily_transit.cycles.engine import _derive_span_events, _filter_events_to_window, _merge_retro_intervals
from daily_transit.cycles.ics_builder import build_cycle_event


def test_retro_interval_clamped_and_counted():
    window_start = datetime(2026, 1, 1)
    window_end = datetime(2026, 1, 10)
    interval = CycleEvent(
        event_type="retro_interval",
        body="Mars",
        start_time_utc=window_start - timedelta(days=2),
        end_time_utc=window_end + timedelta(days=2),
    )
    metrics = {"boundary_drops": 0, "boundary_clamped": 0}

    filtered = _filter_events_to_window(
        [interval], window_start, window_end, metrics, clamp_intervals=True, timing_debug=False
    )

    assert len(filtered) == 1
    clamped = filtered[0]
    assert clamped.start_time_utc == window_start
    assert clamped.end_time_utc == window_end
    assert metrics["boundary_clamped"] == 1
    assert metrics["boundary_drops"] == 0


def test_span_derivation_ingress_and_synodic():
    window_start = datetime(2026, 1, 1)
    window_end = datetime(2026, 1, 10)

    ingress_events = [
        CycleEvent(event_type="ingress", body="Sun", sign="Aries", start_time_utc=window_start),
        CycleEvent(event_type="ingress", body="Sun", sign="Taurus", start_time_utc=datetime(2026, 1, 5)),
    ]

    synodic_events = [
        CycleEvent(
            event_type="synodic_phase",
            body1="Mercury",
            body2="Venus",
            phase_angle=0.0,
            start_time_utc=datetime(2026, 1, 1),
            end_time_utc=datetime(2026, 1, 1),
        ),
        CycleEvent(
            event_type="synodic_phase",
            body1="Mercury",
            body2="Venus",
            phase_angle=90.0,
            start_time_utc=datetime(2026, 1, 3),
            end_time_utc=datetime(2026, 1, 3),
        ),
        CycleEvent(
            event_type="synodic_phase",
            body1="Mercury",
            body2="Venus",
            phase_angle=180.0,
            start_time_utc=datetime(2026, 1, 6),
            end_time_utc=datetime(2026, 1, 6),
        ),
    ]

    spans = _derive_span_events(ingress_events + synodic_events, window_start, window_end)

    ingress_spans = [ev for ev in spans if ev.event_type == "ingress_span"]
    synodic_spans = [ev for ev in spans if ev.event_type == "synodic_phase_span"]

    assert len(ingress_spans) == 2
    assert ingress_spans[0].start_time_utc == window_start
    assert ingress_spans[0].end_time_utc == datetime(2026, 1, 5)
    assert ingress_spans[1].start_time_utc == datetime(2026, 1, 5)
    assert ingress_spans[1].end_time_utc == window_end

    assert len(synodic_spans) == 3
    # Last span wraps to window_end when no next phase
    assert synodic_spans[-1].end_time_utc == window_end
    assert synodic_spans[0].phase_start_deg == 0.0
    assert synodic_spans[0].phase_end_deg == 90.0


def test_synodic_span_wrap_and_uid_uniqueness():
    window_start = datetime(2026, 1, 1)
    window_end = datetime(2026, 1, 4)
    phases = [
        CycleEvent(
            event_type="synodic_phase",
            body1="Mercury",
            body2="Venus",
            phase_angle=270.0,
            start_time_utc=datetime(2026, 1, 1),
            end_time_utc=datetime(2026, 1, 1),
        ),
        CycleEvent(
            event_type="synodic_phase",
            body1="Mercury",
            body2="Venus",
            phase_angle=0.0,
            start_time_utc=datetime(2026, 1, 3),
            end_time_utc=datetime(2026, 1, 3),
        ),
    ]

    spans = _derive_span_events(phases, window_start, window_end)
    wrap_span = [ev for ev in spans if ev.event_type == "synodic_phase_span"][-1]
    assert wrap_span.phase_start_deg == 0.0 or wrap_span.phase_start_deg == 270.0
    assert wrap_span.phase_end_deg in (0.0, 270.0)
    assert wrap_span.end_time_utc == window_end

    # UID namespace separation between instant and span
    instant = phases[0]
    span_event = wrap_span
    instant_uid = build_cycle_event(instant, pytz.UTC, status="CONFIRMED", thunderbird=False).uid
    span_uid = build_cycle_event(span_event, pytz.UTC, status="CONFIRMED", thunderbird=False).uid
    assert instant_uid != span_uid


def test_chunk_seam_retro_merge_after_clamp():
    base_start = datetime(2026, 1, 1)
    base_end = datetime(2026, 1, 10)
    chunk1 = CycleEvent(
        event_type="retro_interval",
        body="Mercury",
        start_time_utc=base_start,
        end_time_utc=datetime(2026, 1, 6),
    )
    chunk2 = CycleEvent(
        event_type="retro_interval",
        body="Mercury",
        start_time_utc=datetime(2026, 1, 5),
        end_time_utc=base_end,
    )
    merged = _merge_retro_intervals([chunk1, chunk2])
    assert len(merged) == 1
    assert merged[0].start_time_utc == base_start
    assert merged[0].end_time_utc == base_end
