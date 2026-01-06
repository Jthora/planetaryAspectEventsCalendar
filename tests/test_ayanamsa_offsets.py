import math
from datetime import datetime, timezone
from pathlib import Path
import json

import pytest

from daily_transit.ayanamsa import get_ayanamsa_offset, LAHIRI_BASE_OFFSET_DEG


@pytest.mark.parametrize(
    "name, dt, expected, tol",
    [
        # Tolerances target sub-arcsecond for base dates; drift case allows ~0.0001° (~0.36").
        ("tropical", datetime(2000, 1, 1, tzinfo=timezone.utc), 0.0, 1e-9),
        ("lahiri", datetime(2000, 1, 1, tzinfo=timezone.utc), LAHIRI_BASE_OFFSET_DEG, 1e-6),
        (
            "lahiri",
            datetime(2020, 1, 1, tzinfo=timezone.utc),
            LAHIRI_BASE_OFFSET_DEG + (50.29 / 3600.0) * 20.0,
            1e-4,
        ),
        ("galactic_core", datetime(2000, 1, 1, tzinfo=timezone.utc), 0.0, 1e-9),
    ],
)
def test_ayanamsa_offset_basics(name, dt, expected, tol):
    result = get_ayanamsa_offset(dt, name)
    assert math.isclose(result, expected % 360.0, rel_tol=0, abs_tol=tol)


def test_invalid_ayanamsa_raises():
    with pytest.raises(SystemExit):
        get_ayanamsa_offset(datetime(2000, 1, 1, tzinfo=timezone.utc), "invalid")


def test_ayanamsa_golden_fixtures():
    fixture_path = Path(__file__).parent / "fixtures" / "ayanamsa_golden.json"
    data = json.loads(fixture_path.read_text())

    for case in data:
        name = case["ayanamsa"]
        dt = datetime.fromisoformat(case["datetime"])
        expected = case["offset_deg"]
        tol = case.get("tolerance", 1e-4)

        result = get_ayanamsa_offset(dt, name)
        assert math.isclose(result, expected, rel_tol=0, abs_tol=tol)
