from datetime import datetime, timedelta
import logging

from daily_transit import aspect_detection as ad


def test_detect_aspects_warns_and_returns_empty_on_empty_map(caplog):
    start = datetime(2025, 1, 1)
    end = start + timedelta(hours=1)

    with caplog.at_level(logging.WARNING):
        aspects = ad.detect_aspects(
            {"earth": object()},
            None,
            start,
            end,
            orb=1.0,
            aspect_degrees={},
            planets=[("Sun", ""), ("Moon", "")],
            coarse_step_mins=60,
            refine_step_mins=5,
            merge_window_hours=4.0,
            retrograde_probe_hours=3.0,
        )

    assert aspects == []
    assert any("No aspect degrees provided" in rec.message for rec in caplog.records)
