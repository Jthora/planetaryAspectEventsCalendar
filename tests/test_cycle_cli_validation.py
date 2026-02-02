import pytest

from DailyTransitAspectCalendarGenerator import parse_args
from daily_transit.cycles.cli import build_cycle_config_from_args
from daily_transit.cycles.engine import detect_cycles
from daily_transit.config import GeneratorConfig
import pytz
from datetime import datetime


def test_cycle_invalid_type_exits():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-types", "ingress,unknown",
        ])


def test_cycle_invalid_phase_angle_exits():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-phase-angles", "0,400",
        ])


def test_cycle_valid_defaults_parse():
    args = parse_args([
        "--start", "2026-01-01",
        "--end", "2026-01-02",
        "--cycle-engine", "helionext-cycles",
    ])
    assert args.cycle_engine == "helionext-cycles"
    assert args.cycle_types is None  # defaults handled downstream


def test_cycle_invalid_ingress_sign_exits():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-ingress-signs", "Aries,InvalidSign",
        ])


def test_cycle_custom_phase_angles_sorted_and_deduped():
    raw_args = parse_args([
        "--start", "2026-01-01",
        "--end", "2026-01-02",
        "--cycle-engine", "helionext-cycles",
        "--cycle-phase-angles", "180,0,90,90",
    ])
    cfg = build_cycle_config_from_args(raw_args)
    assert cfg.phase_angles == [0.0, 90.0, 180.0]


def test_cycle_negative_padding_rejected():
    with pytest.raises(SystemExit):
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
            "--cycle-retro-padding-days", "-1",
        ])


def test_cycle_padding_clamp_span_flags_defaults_off():
    raw_args = parse_args([
        "--start", "2026-01-01",
        "--end", "2026-01-02",
        "--cycle-engine", "helionext-cycles",
    ])
    cfg = build_cycle_config_from_args(raw_args)
    assert cfg.retro_padding_days == 0.0
    assert cfg.clamp_intervals is False
    assert cfg.derive_spans is False


def test_cycle_padding_clamp_span_flags_parse():
    raw_args = parse_args([
        "--start", "2026-01-01",
        "--end", "2026-01-02",
        "--cycle-engine", "helionext-cycles",
        "--cycle-retro-padding-days", "2.5",
        "--cycle-clamp-intervals",
        "--cycle-derive-spans",
    ])
    cfg = build_cycle_config_from_args(raw_args)
    assert cfg.retro_padding_days == 2.5
    assert cfg.clamp_intervals is True
    assert cfg.derive_spans is True


def test_cycle_defaults_do_not_change_outputs_when_off():
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 2)
    cycle_cfg = build_cycle_config_from_args(
        parse_args([
            "--start", "2026-01-01",
            "--end", "2026-01-02",
            "--cycle-engine", "helionext-cycles",
        ])
    )
    # Disable cycle types to avoid ephemeris usage; ensures config snapshot still produced.
    cycle_cfg.cycle_types = []

    gen_cfg = GeneratorConfig(
        start_date=start,
        end_date=end,
        timezone=pytz.UTC,
        orb=1.0,
        aspect_degrees={},
        planets=[("Sun", "Su")],
        coarse_step_mins=60,
        refine_step_mins=30,
        merge_window_hours=1.0,
        inclusive_end=False,
        status="CONFIRMED",
        thunderbird_friendly=False,
        product_id="-//test//EN",
        verbose=False,
        ascii_only=True,
        retrograde_probe_hours=24.0,
        include_lunar_phases=False,
        timing_debug=False,
        interpretation_mode="none",
        cycle_config=cycle_cfg,
    )

    metrics = {}
    events = detect_cycles({}, None, start, end, gen_cfg, metrics_out=metrics)

    assert events == []
    snapshot = metrics["config_snapshot"]
    assert snapshot["retro_padding_days"] == 0.0
    assert snapshot["clamp_intervals"] is False
    assert snapshot["derive_spans"] is False
    assert snapshot["cycle_types"] == []
    assert snapshot["retro_probe_hours"] == cycle_cfg.retro_probe_hours
    assert snapshot["start_utc"] == start.isoformat()
    assert snapshot["end_utc"] == end.isoformat()
