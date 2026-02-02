import pytest

from daily_transit.cycles.cli import parse_phase_angles


def test_parse_phase_angles_sorts_and_dedupes():
    angles = parse_phase_angles("180,0,90,90,360,45")
    assert angles == [0.0, 45.0, 90.0, 180.0, 360.0]


def test_parse_phase_angles_rejects_out_of_range():
    with pytest.raises(SystemExit):
        parse_phase_angles("-1")
    with pytest.raises(SystemExit):
        parse_phase_angles("361")
