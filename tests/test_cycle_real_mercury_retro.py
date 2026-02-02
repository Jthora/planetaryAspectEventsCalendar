from datetime import datetime
import json
from pathlib import Path

import pytz
import pytest
from skyfield.api import load as skyfield_load

from DailyTransitAspectCalendarGenerator import load_ephemeris
from daily_transit.cycles.config import CycleConfig
from daily_transit.cycles.dto import cycle_sort_key
from daily_transit.cycles.engine import detect_cycles
from daily_transit.config import GeneratorConfig


FIXTURE = Path(__file__).resolve().parent / "fixtures" / "real_cycles" / "mercury_retro_202408_1m.json"
EPHEMERIS_PATH = Path(__file__).resolve().parents[1] / "de440s.bsp"


def _expected_sort_key(entry: dict):
    order = {
        "ingress": 1,
        "synodic_phase": 2,
        "retro_interval": 3,
        "station": 4,
    }
    start = datetime.fromisoformat(entry["start"])
    event_rank = order.get(entry["event_type"], 999)
    return (
        start,
        event_rank,
        entry.get("body") or entry.get("body1") or "",
        entry.get("body2") or "",
        entry.get("phase_angle", -1.0) if entry.get("phase_angle") is not None else -1.0,
    )


@pytest.mark.skipif(not FIXTURE.exists(), reason="real cycle fixture missing")
@pytest.mark.require_ephemeris
def test_mercury_retro_window_matches_fixture():
    if not EPHEMERIS_PATH.exists():
        pytest.skip("de440s.bsp missing")

    payload = json.loads(FIXTURE.read_text())
    meta = payload["metadata"]
    expected = payload["events"]

    start = datetime.fromisoformat(meta["start"])
    end = datetime.fromisoformat(meta["end"])
    planets = [(name, name[:2]) for name in meta["planets"]]

    cycle_config = CycleConfig(
        engine="helionext-cycles",
        cycle_types=meta["cycle_types"],
        ayanamsa=meta["ayanamsa"],
        retro_probe_hours=meta["retro_probe_hours"],
    )

    gen_config = GeneratorConfig(
        start_date=start,
        end_date=end,
        timezone=pytz.UTC,
        orb=1.5,
        aspect_degrees={},
        planets=planets,
        coarse_step_mins=60,
        refine_step_mins=5,
        merge_window_hours=4.0,
        inclusive_end=True,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//Test//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=meta["retro_probe_hours"],
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="standard",
        engine="helionext-cycles",
        cycle_config=cycle_config,
    )

    eph = load_ephemeris(str(EPHEMERIS_PATH))
    ts = skyfield_load.timescale()

    metrics: dict = {}
    events = detect_cycles(eph, ts, start, end, gen_config, metrics_out=metrics)

    events_sorted = sorted(events, key=cycle_sort_key)
    expected_sorted = sorted(expected, key=_expected_sort_key)

    assert len(events_sorted) == len(expected_sorted)

    tolerance_seconds = 2
    for ev, exp in zip(events_sorted, expected_sorted):
        assert ev.event_type == exp["event_type"]
        assert ev.body == exp["body"]
        assert ev.sign == exp["sign"]
        assert ev.station_direction == exp["station_direction"]
        assert ev.ayanamsa_mode == exp["ayanamsa_mode"]

        exp_start = datetime.fromisoformat(exp["start"])
        assert abs((ev.start_time_utc - exp_start).total_seconds()) <= tolerance_seconds

        if exp["end"] and ev.end_time_utc:
            exp_end = datetime.fromisoformat(exp["end"])
            assert abs((ev.end_time_utc - exp_end).total_seconds()) <= tolerance_seconds
