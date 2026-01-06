from datetime import datetime

import pytz

from DailyTransitAspectCalendarGenerator import build_config_from_args, parse_args, select_aspects
from daily_transit.aspect_catalog import COMPLETE_ASPECTS


def test_cli_complete_scope_propagates_to_config():
    args = parse_args([
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-02",
        "--aspect-scope",
        "complete",
    ])

    aspect_map = select_aspects(args.aspects)
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")

    config = build_config_from_args(
        args,
        aspect_map,
        [("Sun", "Sun"), ("Moon", "Moon")],
        pytz.UTC,
        start_date=start_date,
        end_date=end_date,
    )

    assert config.aspect_degrees == COMPLETE_ASPECTS
    assert len(config.aspect_degrees) > 5
