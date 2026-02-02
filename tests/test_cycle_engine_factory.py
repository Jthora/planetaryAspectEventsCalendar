import pytest

from daily_transit.cycles.engine_factory import get_cycle_detection_engine


def test_invalid_engine_name_raises_and_lists_allowed():
    with pytest.raises(ValueError) as excinfo:
        get_cycle_detection_engine("invalid-engine")
    message = str(excinfo.value)
    assert "unsupported cycle engine" in message.lower()
    assert "helionext-cycles" in message


def test_off_engine_rejected_with_hint():
    with pytest.raises(ValueError) as excinfo:
        get_cycle_detection_engine("off")
    assert "enable with --cycle-engine" in str(excinfo.value).lower()
