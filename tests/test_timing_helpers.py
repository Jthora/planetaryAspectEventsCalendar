import pytest

from daily_transit import aspect_detection as ad


def test_adaptive_step_minutes_respects_minimum():
    step = ad._adaptive_step_minutes(base_minutes=60, max_relative_speed=10.0)
    assert step == 12


def test_adaptive_step_minutes_returns_base_when_slow():
    step = ad._adaptive_step_minutes(base_minutes=30, max_relative_speed=1.0)
    assert step == 30


def test_adaptive_step_minutes_handles_small_base():
    step = ad._adaptive_step_minutes(base_minutes=5, max_relative_speed=5.0)
    assert step == 5


def test_dynamic_probe_hours_clamps_to_minimum():
    probe = ad._dynamic_probe_hours(base_probe=6.0, approx_speed=None)
    assert probe == 3.0


def test_dynamic_probe_hours_scales_with_speed():
    probe = ad._dynamic_probe_hours(base_probe=6.0, approx_speed=4.0)
    assert probe < 6.0
    assert probe <= 3.0


def test_dynamic_probe_hours_caps_when_speed_small():
    probe = ad._dynamic_probe_hours(base_probe=1.0, approx_speed=0.05)
    assert probe >= ad.MIN_PROBE_HOURS


def test_pair_merge_window_hours_for_moon():
    hours = ad._pair_merge_window_hours(("Sun", "Moon"), base_merge_hours=4.0)
    assert hours == pytest.approx(3.5)


def test_pair_merge_window_hours_for_moon_with_small_base():
    hours = ad._pair_merge_window_hours(("Sun", "Moon"), base_merge_hours=2.0)
    assert hours == pytest.approx(2.0)


def test_pair_merge_window_hours_for_mercury():
    hours = ad._pair_merge_window_hours(("Mercury", "Venus"), base_merge_hours=4.0)
    assert hours == pytest.approx(1.0)


def test_pair_merge_window_hours_default_floor():
    hours = ad._pair_merge_window_hours(("Jupiter", "Saturn"), base_merge_hours=0.01)
    assert hours >= 0.0833