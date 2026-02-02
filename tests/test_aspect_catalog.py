import pytest

from daily_transit.aspect_catalog import COMPLETE_ASPECTS, MAJOR_ASPECTS, select_scope
from DailyTransitAspectCalendarGenerator import select_aspects


def test_complete_catalog_contains_expected_entries():
    assert len(COMPLETE_ASPECTS) == 30
    for name in [
        "Semisextile",
        "Semisquare",
        "Sesquiquadrate",
        "Tredecile",
        "Quattuordecile",
    ]:
        assert name in COMPLETE_ASPECTS
    assert COMPLETE_ASPECTS["Tredecile"] == 108.0
    assert COMPLETE_ASPECTS["Quattuordecile"] == 25.714285714285715
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
    assert "Tredecile" in complete
    assert "Tredecile" not in major


@pytest.mark.parametrize(
    "name,expected",
    [
        ("Conjunction", 0.0),
        ("Quattuordecile", 25.714285714285715),
        ("Semisextile", 30.0),
        ("Undecile", 32.72727272727273),
        ("Decile", 36.0),
        ("Novile", 40.0),
        ("Semisquare", 45.0),
        ("Septile", 51.42857142857143),
        ("Sextile", 60.0),
        ("Tridecile", 65.45454545454545),
        ("Quintile", 72.0),
        ("Binovile", 80.0),
        ("Square", 90.0),
        ("Biseptile", 102.85714285714286),
        ("Tredecile", 108.0),
        ("Trine", 120.0),
        ("Sesquiquadrate", 135.0),
        ("Biquintile", 144.0),
        ("Quincunx", 150.0),
        ("Triseptile", 154.28571428571428),
        ("Quadranovile", 160.0),
        ("Opposition", 180.0),
        ("Semi-Octile", 22.5),
        ("Sesqui-Octile", 67.5),
        ("Vigintile", 18.0),
        ("Quinvigintile", 14.4),
        ("Quadraundecile", 130.9090909090909),
        ("Septdecile", 21.176470588235293),
        ("Semiduodecile", 15.0),
        ("Sesquiquintile", 144.0),
    ],
)
def test_complete_catalog_values_within_tolerance(name, expected):
    assert name in COMPLETE_ASPECTS
    assert abs(COMPLETE_ASPECTS[name] - expected) < 1e-6


def test_complete_catalog_omits_216_variant():
    assert "Biquintile-216" not in COMPLETE_ASPECTS
