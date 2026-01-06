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
        aspect_degrees={"Square": 90.0},
        planets=[("Sun", ""), ("Saturn", "")],
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


def test_diff_harness_station_flag(monkeypatch):
    config = _config()
    base_time = datetime(2025, 1, 1, 6, 0, 0)

    legacy_event = AspectEvent(
        time=base_time,
        planet1="Sun",
        planet2="Saturn",
        aspect="Square",
        exact_degrees=90.0,
        raw_separation=90.0,
        delta=0.002,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )
    helio_event = AspectEvent(
        time=base_time,
        planet1="Sun",
        planet2="Saturn",
        aspect="Square",
        exact_degrees=90.0,
        raw_separation=90.0,
        delta=0.002,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    def fake_legacy_detect(*args, **kwargs):
        return [legacy_event]

    class FakeEngine:
        def detect(self, eph, ts, cfg, detection_end):
            return [helio_event]

    # Force station disagreement between engines: return True for legacy call and False for helio call
    call_state = {"count": 0}

    def fake_station(eph, ts, planet, dt, window_hours=12.0, epsilon_deg_per_day=0.01):
        call_state["count"] += 1
        # First two calls belong to legacy_event planets, next two to helio_event planets
        return call_state["count"] in {1, 2}

    monkeypatch.setattr(diff_harness, "_is_station", fake_station)
    monkeypatch.setattr(diff_harness, "legacy_detect", fake_legacy_detect)
    monkeypatch.setattr(diff_harness, "get_detection_engine", lambda name: FakeEngine())

    report = diff_harness.run_dual(
        config=config,
        eph=None,
        ts=None,
        detection_end=config.end_date,
        time_tolerance_s=2.0,
        delta_tolerance_deg=0.005,
    )

    assert report["matches"] == []
    assert report["missing"] == []
    assert report["extra"] == []
    assert len(report["mismatches"]) == 1

    mismatch = report["mismatches"][0]
    assert mismatch["reason"] == "station_flag"
    assert mismatch["legacy_station"] == [True, True]
    assert mismatch["helionext_station"] == [False, False]
    assert report["reason_counts"] == {"station_flag": 1}
