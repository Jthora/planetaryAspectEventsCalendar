import pytest

from daily_transit.aspect_catalog import COMPLETE_ASPECTS, MAJOR_ASPECTS, select_scope
from DailyTransitAspectCalendarGenerator import select_aspects


def test_complete_catalog_contains_expected_entries():
    assert len(COMPLETE_ASPECTS) == 18
    assert COMPLETE_ASPECTS["Trebiquintile"] == 108.0
    assert COMPLETE_ASPECTS["Semi-Septile"] == 25.714285714285715
    assert COMPLETE_ASPECTS["Triseptile"] == 154.28571428571428


def test_select_scope_major_and_complete():
    assert select_scope("major") == MAJOR_ASPECTS
    assert select_scope("complete") == COMPLETE_ASPECTS
    assert select_scope("unknown") is None


def test_select_aspects_complete_uses_catalog():
    selected = select_aspects("complete")
    assert selected == COMPLETE_ASPECTS
    assert len(selected) > len(MAJOR_ASPECTS)


def test_select_aspects_major_vs_complete_differs():
    complete = select_aspects("complete")
    major = select_aspects("major")
    assert len(complete) > len(major)
    assert "Trebiquintile" in complete
    assert "Trebiquintile" not in major


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Conjunction", 0.0),
        ("Semi-Septile", 25.714285714285715),
        ("Semi-Sextile", 30.0),
        ("Semiquintile", 36.0),
        ("Novile", 40.0),
        ("SemiSquare", 45.0),
        ("Septile", 51.42857142857143),
        ("Sextile", 60.0),
        ("Quintile", 72.0),
        ("Binovile", 80.0),
        ("Square", 90.0),
        ("Biseptile", 102.85714285714286),
        ("Trebiquintile", 108.0),
        ("Trine", 120.0),
        ("Biquintile", 144.0),
        ("Quincunx", 150.0),
        ("Triseptile", 154.28571428571428),
        ("Opposition", 180.0),
    ],
)
def test_complete_catalog_values_within_tolerance(name, expected):
    assert name in COMPLETE_ASPECTS
    assert abs(COMPLETE_ASPECTS[name] - expected) < 1e-6


def test_complete_catalog_omits_216_variant():
    assert "Biquintile-216" not in COMPLETE_ASPECTS
