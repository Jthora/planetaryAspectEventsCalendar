from datetime import datetime

import pytz

from DailyTransitAspectCalendarGenerator import build_config_from_args, parse_args


def test_defaults_propagate_into_config():
    args = parse_args(["--start", "2025-01-01", "--end", "2025-01-02"])
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")

    config = build_config_from_args(
        args,
        {"Conjunction": 0.0},
        [("Sun", "Sun")],
        pytz.UTC,
        start_date=start_date,
        end_date=end_date,
    )

    assert config.mode == "standard"
    assert config.ayanamsa == "tropical"
    assert config.precision_deg == "decimal"
    assert config.precision_time == "seconds"
    assert config.latitude is None
    assert config.longitude is None
    assert config.elevation_m == 0.0
