from datetime import datetime

from DailyTransitAspectCalendarGenerator import fold_ical_lines

from daily_transit.aspect_detection import AspectEvent
from daily_transit.compact_formatter import format_compact_aspect
from daily_transit.zodiac_metadata import PlanetZodiacInfo, SignMetadata, get_sign_metadata
import unicodedata


def make_context():
    meta = SignMetadata(
        name="Aries",
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
    return {
        "Sun": PlanetZodiacInfo(
            planet="Sun",
            longitude=15.0,
            sign="Aries",
            metadata=meta,
            house=1,
        ),
        "Moon": PlanetZodiacInfo(
            planet="Moon",
            longitude=75.0,
            sign="Gemini",
            metadata=meta,
            house=3,
        ),
    }


def test_compact_formatter_decimal_with_houses_and_retro():
    ev = AspectEvent(
        time=datetime(2025, 1, 1, 12, 0, 30),
        planet1="Sun",
        planet2="Moon",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=0.0,
        delta=0.25,
        planet1_retrograde=False,
        planet2_retrograde=True,
    )

    line = format_compact_aspect(
        ev,
        make_context(),
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=True,
    )

    assert "Sun" in line
    assert "Moon R" in line
    assert "H:1" in line and "H:3" in line


def test_compact_formatter_normalizes_unicode_output():
    # Provide decomposed accent in planet glyph to ensure NFC normalization in output.
    planets = [("Venus", "e\u0301")]  # e + combining acute
    context = {
        "Venus": PlanetZodiacInfo(
            planet="Venus",
            longitude=10.0,
            sign="Taurus",
            metadata=get_sign_metadata("Taurus"),
            house=2,
        )
    }
    ev = AspectEvent(
        planet1="Venus",
        planet2="Venus",
        aspect="Conjunction",
        time=datetime(2025, 1, 1, 12, 0),
        delta=0.05,
        exact_degrees=0.0,
        raw_separation=0.05,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    line = format_compact_aspect(ev, context, planets=planets, ascii_only=False)

    assert unicodedata.is_normalized("NFC", line)
    assert "Δ=" in line
    assert "12:00:00" in line


def test_compact_formatter_dms_precision():
    ev = AspectEvent(
        time=datetime(2025, 1, 1, 6, 15, 0),
        planet1="Sun",
        planet2="Moon",
        aspect="Trine",
        exact_degrees=120.0,
        raw_separation=120.0,
        delta=0.0,
        planet1_retrograde=False,
        planet2_retrograde=False,
    )

    line = format_compact_aspect(
        ev,
        make_context(),
        precision_deg="dms",
        precision_time="minutes",
        ascii_only=False,
    )

    assert "06:15" in line
    assert "°" in line
    assert "Trine" in line


def test_compact_formatter_ascii_degrades_labels_and_retro_marker():
    ev = AspectEvent(
        time=datetime(2025, 1, 2, 7, 45, 0),
        planet1="Mercury",
        planet2="Mars",
        aspect="Square",
        exact_degrees=90.0,
        raw_separation=89.8,
        delta=0.2,
        planet1_retrograde=True,
        planet2_retrograde=False,
    )

    context = make_context()
    context.update(
        {
            "Mercury": PlanetZodiacInfo(
                planet="Mercury",
                longitude=121.5,
                sign="Leo",
                metadata=context["Sun"].metadata,
                house=10,
            ),
            "Mars": PlanetZodiacInfo(
                planet="Mars",
                longitude=222.0,
                sign="Scorpio",
                metadata=context["Sun"].metadata,
                house=5,
            ),
        }
    )

    line = format_compact_aspect(
        ev,
        context,
        planets=[("Mercury", "☿"), ("Mars", "♂")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=True,
    )

    assert "Mercury R" in line  # retro marker remains in ASCII
    assert "Mars" in line and "H:10" in line and "H:5" in line
    assert " deg" in line  # ASCII degree label
    assert "☿" not in line and "♂" not in line  # glyphs stripped


def test_compact_formatter_glyph_mode_uses_planet_glyphs():
    ev = AspectEvent(
        time=datetime(2025, 1, 3, 9, 0, 15),
        planet1="Venus",
        planet2="Jupiter",
        aspect="Opposition",
        exact_degrees=180.0,
        raw_separation=179.9,
        delta=0.1,
        planet1_retrograde=False,
        planet2_retrograde=True,
    )

    context = make_context()
    context.update(
        {
            "Venus": PlanetZodiacInfo(
                planet="Venus",
                longitude=45.0,
                sign="Taurus",
                metadata=context["Sun"].metadata,
                house=2,
            ),
            "Jupiter": PlanetZodiacInfo(
                planet="Jupiter",
                longitude=225.0,
                sign="Scorpio",
                metadata=context["Sun"].metadata,
                house=8,
            ),
        }
    )

    line = format_compact_aspect(
        ev,
        context,
        planets=[("Venus", "♀"), ("Jupiter", "♃")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=False,
    )

    assert "♀" in line and "♃" in line
    assert "℞" in line  # retro marker glyph
    assert "H:2" in line and "H:8" in line
    assert "deg" not in line


def test_compact_formatter_summary_folds_under_75_bytes_with_glyphs():
    ev = AspectEvent(
        time=datetime(2025, 1, 4, 10, 45, 50),
        planet1="Saturn",
        planet2="Neptune",
        aspect="Conjunction",
        exact_degrees=0.0,
        raw_separation=359.8,
        delta=0.2,
        planet1_retrograde=True,
        planet2_retrograde=True,
    )

    context = make_context()
    context.update(
        {
            "Saturn": PlanetZodiacInfo(
                planet="Saturn",
                longitude=299.9,
                sign="Aquarius",
                metadata=context["Sun"].metadata,
                house=11,
            ),
            "Neptune": PlanetZodiacInfo(
                planet="Neptune",
                longitude=119.0,
                sign="Leo",
                metadata=context["Sun"].metadata,
                house=5,
            ),
        }
    )

    line = format_compact_aspect(
        ev,
        context,
        planets=[("Saturn", "♄"), ("Neptune", "♆")],
        precision_deg="decimal",
        precision_time="seconds",
        ascii_only=False,
    )

    ics_line = "SUMMARY:" + line
    assert len(ics_line.encode("utf-8")) > 75  # ensure folding scenario

    folded = fold_ical_lines(ics_line)
    lines = folded.strip().split("\r\n")

    assert all(len(chunk.encode("utf-8")) <= 75 for chunk in lines)
    assert lines[0].startswith("SUMMARY:")
    for continuation in lines[1:]:
        assert continuation.startswith(" ")
