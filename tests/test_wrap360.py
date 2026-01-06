import math

import pytest

from daily_transit.aspect_detection import wrap360


def test_wrap360_negative_angle_returns_positive_range():
    assert wrap360(-1.0) == pytest.approx(359.0, rel=0, abs=1e-9)
    assert wrap360(-721.25) == pytest.approx(360.0 - 1.25, rel=0, abs=1e-9)


def test_wrap360_near_upper_boundary_preserves_precision():
    val = wrap360(359.999999)
    assert 359.999 < val < 360.0
    assert math.isclose(val, 359.999999, rel_tol=0, abs_tol=1e-9)


def test_wrap360_is_idempotent():
    original = wrap360(-30.5)
    assert wrap360(original) == pytest.approx(original, rel=0, abs=1e-12)
