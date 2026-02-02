from datetime import datetime

import pytz

from DailyTransitAspectCalendarGenerator import build_config_from_args, parse_args


def _base_params(extra_args=None):
    args = [
        "--start", "2026-01-01",
        "--end", "2026-01-02",
    ]
    if extra_args:
        args.extend(extra_args)
    return parse_args(args)


def test_cycles_off_keeps_aspect_config_and_no_cycle_config():
    parsed = _base_params(["--cycle-engine", "off"])
    cfg = build_config_from_args(
        parsed,
        aspect_degrees={"Conjunction": 0.0},
        planets=[("Sun", "Su")],
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )
    assert cfg.engine == "legacy"  # aspect engine default remains
    assert cfg.cycle_config is None
    assert cfg.merge_window_hours == 4.0  # aspect defaults untouched


def test_cycles_on_still_leave_aspect_engine_unchanged():
    parsed = _base_params(["--cycle-engine", "helionext-cycles"])
    cfg = build_config_from_args(
        parsed,
        aspect_degrees={"Conjunction": 0.0},
        planets=[("Sun", "Su")],
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )
    assert cfg.engine == "legacy"  # aspect engine still default
    assert cfg.cycle_config is not None
    assert cfg.cycle_config.engine == "helionext-cycles"


def test_cycles_on_does_not_mutate_aspect_fields():
    aspect_degrees = {"Conjunction": 0.0, "Square": 90.0}
    args_off = _base_params(["--cycle-engine", "off"])
    args_on = _base_params(["--cycle-engine", "helionext-cycles"])

    cfg_off = build_config_from_args(
        args_off,
        aspect_degrees=aspect_degrees,
        planets=[("Sun", "Su")],
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )
    cfg_on = build_config_from_args(
        args_on,
        aspect_degrees=aspect_degrees,
        planets=[("Sun", "Su")],
        timezone=pytz.UTC,
        start_date=datetime(2026, 1, 1),
        end_date=datetime(2026, 1, 2),
    )

    assert cfg_on.aspect_degrees == cfg_off.aspect_degrees
    assert cfg_on.merge_window_hours == cfg_off.merge_window_hours
    assert cfg_on.coarse_step_mins == cfg_off.coarse_step_mins
