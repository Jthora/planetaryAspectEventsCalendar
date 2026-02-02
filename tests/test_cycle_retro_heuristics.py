import pytest

from daily_transit.cycles import retro


def test_probe_hours_speed_classes():
    assert retro._probe_hours_for_body("Moon", None) == 2.0
    assert retro._probe_hours_for_body("Mercury", None) == 6.0
    assert retro._probe_hours_for_body("Mars", None) == 12.0
    assert retro._probe_hours_for_body("Jupiter", None) == 18.0
    assert retro._probe_hours_for_body("Pluto", None) == 24.0


def test_probe_hours_respects_override():
    assert retro._probe_hours_for_body("Moon", 5.5) == 5.5


def test_station_strength_formula():
    assert retro.station_strength_from_rates(0.2, -0.3) == pytest.approx(0.5)
    assert retro.station_strength_from_rates(0.0, 0.0) == 0.0
    assert retro.station_strength_from_rates(-0.1, -0.1) == pytest.approx(0.2)
