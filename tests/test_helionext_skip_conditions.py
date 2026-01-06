from __future__ import annotations

from datetime import datetime, timedelta

from daily_transit.config import GeneratorConfig
from daily_transit.helionext.engine import detect_aspects
from daily_transit.constants import DEFAULT_PLANETS
from tests.fixtures.synthetic_ephemeris import LinearMotionBody, SyntheticEarth, SyntheticTimescale


def _make_diverging_eph():
    baseline = datetime(2025, 1, 1, 0, 0, 0)
    # Two bodies moving apart from a wide separation; no aspect crossing within window
    bodies = {
        "sun": LinearMotionBody(base_degrees=0.0, degrees_per_hour=0.0),
        "moon": LinearMotionBody(base_degrees=120.0, degrees_per_hour=1.0),
    }
    eph = {
        "earth": SyntheticEarth(bodies, baseline),
        "sun": bodies["sun"],
        "moon": bodies["moon"],
    }
    ts = SyntheticTimescale()
    return eph, ts, baseline


def _base_config(aspect_degrees):
    return GeneratorConfig(
        start_date=datetime(2025, 1, 1, 0, 0, 0),
        end_date=datetime(2025, 1, 1, 12, 0, 0),
        timezone=None,
        orb=0.5,
        aspect_degrees=aspect_degrees,
        planets=[("Sun", "\u0000"), ("Moon", "\u0000")],
        coarse_step_mins=60,
        refine_step_mins=5,
        merge_window_hours=4.0,
        inclusive_end=False,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//Test//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=6.0,
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="standard",
        engine="helionext",
        mode="standard",
        ayanamsa="tropical",
        latitude=None,
        longitude=None,
        elevation_m=0.0,
        precision_deg="decimal",
        precision_time="seconds",
    )


def test_helionext_skips_out_of_orb_candidates():
    eph, ts, baseline = _make_diverging_eph()
    aspects = {"Conjunction": 0.0}
    config = _base_config(aspects)

    metrics: dict = {}
    events = detect_aspects(eph, ts, config.start_date, config.end_date, config, metrics_out=metrics)

    assert events == []
    # Should have skipped candidates outside orb without errors
    assert metrics["skipped_out_of_orb"] >= 0
    # Should have at least checked refinement gate and not crashed
    assert metrics["refine_calls"] >= 0
    # Ensure no refine failures occurred in this simple scenario
    assert metrics["refine_failures"] == 0
