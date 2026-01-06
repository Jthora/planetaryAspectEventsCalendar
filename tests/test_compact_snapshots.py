from datetime import datetime

from daily_transit.aspect_detection import AspectEvent
from daily_transit.compact_formatter import format_compact_aspect
from daily_transit.zodiac_metadata import PlanetZodiacInfo, SignMetadata


def _meta(name: str) -> SignMetadata:
    return SignMetadata(
        name=name,
        emoji="",
        element_name="Fire",
        element_glyph="",
        element_color_emoji="",
        element_color_name="Red",
        modality_name="Cardinal",
        modality_symbol="▲",
        left_framing="<",
        right_framing=">",
    )


def _context():
    return {
        "Sun": PlanetZodiacInfo("Sun", 10.5, "Aries", _meta("Aries"), house=1),
        "Moon": PlanetZodiacInfo("Moon", 45.0, "Taurus", _meta("Taurus"), house=4),
        "Mercury": PlanetZodiacInfo("Mercury", 120.25, "Leo", _meta("Leo"), house=10),
        "Mars": PlanetZodiacInfo("Mars", 200.75, "Libra", _meta("Libra"), house=7),
    }


def test_compact_snapshot_decimal_glyph_with_retro():
    ev = AspectEvent(
        time=datetime(2025, 1, 2, 5, 4, 3),
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.2,
        planet1_retrograde=False,
        planet2_retrograde=True,
    )

    line = format_compact_aspect(
        ev,
        _context(),
        planets=[("Sun", "☉"), ("Moon", "☾")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=False,
    )

    expected = "2025-01-02T05:04:03Z | ☉ Z:Ari H:1 010.50° Conjunction ☾ ℞ Z:Tau H:4 045.00° | Δ=000.20°"
    assert line == expected


def test_compact_snapshot_dms_ascii_no_retro():
    ev = AspectEvent(
        time=datetime(2025, 1, 2, 6, 30, 0),
        planet1="Mercury",
        planet2="Mars",
        aspect="Square",
        exact_degrees=90.0,
        raw_separation=90.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    line = format_compact_aspect(
        ev,
        _context(),
        planets=[("Mercury", "☿"), ("Mars", "♂")],
        precision_deg="dms",
        precision_time="minutes",
        ascii_only=True,
    )

    expected = (
        "2025-01-02T06:30Z | Mercury Z:Leo H:10 120 deg15'00\" Square Mars Z:Lib H:7 200 deg45'00\" | Δ=00 deg00'00\""
    )
    assert line == expected


def test_compact_snapshot_retro_both_ascii_and_glyph_mix():
    ev = AspectEvent(
        time=datetime(2025, 1, 2, 7, 15, 45),
        planet1="Moon",
        planet2="Sun",
        aspect="Opposition",
        exact_degrees=180.0,
        raw_separation=179.8,
        delta=0.2,
        planet1_retrograde=True,
        planet2_retrograde=True,
    )

    line_ascii = format_compact_aspect(
        ev,
        _context(),
        planets=[("Moon", "☾"), ("Sun", "☉")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=True,
    )

    expected_ascii = "2025-01-02T07:15:45Z | Moon R Z:Tau H:4 045.00 deg Opposition Sun R Z:Ari H:1 010.50 deg | Δ=000.20 deg"
    assert line_ascii == expected_ascii

    line_glyph = format_compact_aspect(
        ev,
        _context(),
        planets=[("Moon", "☾"), ("Sun", "☉")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=False,
    )

    expected_glyph = "2025-01-02T07:15:45Z | ☾ ℞ Z:Tau H:4 045.00° Opposition ☉ ℞ Z:Ari H:1 010.50° | Δ=000.20°"
    assert line_glyph == expected_glyph
