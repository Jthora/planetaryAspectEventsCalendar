import pytest

from daily_transit.cycles.helpers import sign_after_ayanamsa


@pytest.mark.parametrize(
    "angle,expected",
    [
        (-0.01, "Pisces"),
        (0.0, "Aries"),
        (0.01, "Aries"),
        (29.9999, "Aries"),
        (30.0, "Taurus"),
        (359.99, "Pisces"),
        (360.0, "Aries"),
        (720.1, "Aries"),
    ],
)
def test_sign_after_ayanamsa_wraps(angle, expected):
    assert sign_after_ayanamsa(angle) == expected
