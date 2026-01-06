from daily_transit.zodiac_metadata import build_context_from_longitudes


def test_context_includes_houses_when_provided():
    longs = {"Sun": 10.0, "Moon": 40.0}
    houses = {"Sun": 1, "Moon": 2}
    ctx = build_context_from_longitudes(longs, houses=houses, ayanamsa_name="tropical")

    assert ctx["Sun"].house == 1
    assert ctx["Moon"].house == 2
    assert ctx["Sun"].ayanamsa_name == "tropical"
