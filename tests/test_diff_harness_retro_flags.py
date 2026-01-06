from datetime import datetime

from daily_transit.aspect_detection import AspectEvent
from daily_transit.config import GeneratorConfig
from daily_transit.helionext import diff_harness


def _config():
    return GeneratorConfig(
        start_date=datetime(2025, 1, 1, 0, 0, 0),
        end_date=datetime(2025, 1, 1, 12, 0, 0),
        timezone=None,
        orb=1.0,
        aspect_degrees={"Opposition": 180.0},
        planets=[("Sun", ""), ("Mars", "")],
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


def test_diff_harness_flags_retro_mismatches(monkeypatch):
    config = _config()
    base_time = datetime(2025, 1, 1, 5, 0, 0)

    legacy_event = AspectEvent(
        time=base_time,
        planet1="Sun",
        planet2="Mars",
        aspect="Opposition",
        exact_degrees=180.0,
        raw_separation=180.0,
        delta=0.1,
        planet1_retrograde=True,
        planet2_retrograde=False,
    )
    helio_event = AspectEvent(
        time=base_time,
        planet1="Sun",
        planet2="Mars",
        aspect="Opposition",
        exact_degrees=180.0,
        raw_separation=180.0,
        delta=0.1,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    def fake_legacy_detect(*args, **kwargs):
        return [legacy_event]

    class FakeEngine:
        def detect(self, eph, ts, cfg, detection_end):
            return [helio_event]

    monkeypatch.setattr(diff_harness, "legacy_detect", fake_legacy_detect)
    monkeypatch.setattr(diff_harness, "get_detection_engine", lambda name: FakeEngine())

    report = diff_harness.run_dual(
        config=config,
        eph=None,
        ts=None,
        detection_end=config.end_date,
        time_tolerance_s=5.0,
    )

    assert report["matches"] == []
    assert report["missing"] == []
    assert report["extra"] == []
    assert len(report["mismatches"]) == 1

    mismatch = report["mismatches"][0]
    assert mismatch["reason"] == "retro_flag"
    assert mismatch["legacy_retro"] == [True, False]
    assert mismatch["helionext_retro"] == [False, False]
    assert mismatch["delta_time_s"] == 0.0
    assert report["reason_counts"] == {"retro_flag": 1}
