"""Unit tests for response parsers."""

import pytest

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage
from src.services.parsers import (
    parse_config,
    parse_desk,
    parse_desk_list,
    parse_errors,
    parse_state,
    parse_state_or_fallback,
    parse_usage,
)

# Test constants
EXPECTED_COUNT_TWO = 2
EXPECTED_COUNT_ONE = 1
TEST_POSITION_750 = 750
TEST_POSITION_800 = 800
TEST_POSITION_1000 = 1000
TEST_POSITION_1200 = 1200
TEST_SPEED_10 = 10
TEST_ACTIVATIONS_100 = 100
TEST_ACTIVATIONS_250 = 250
TEST_SIT_STAND_125 = 125
TEST_TIMESTAMP = 1234567890
TEST_ERROR_CODE_1 = 1


def test_parse_desk_list_success() -> None:
    """Test parsing a list of desk IDs."""
    payload = ["cd:fb:1a:53:fb:e6", "aa:bb:cc:dd:ee:ff"]
    result = parse_desk_list(payload)

    assert len(result) == EXPECTED_COUNT_TWO
    assert "cd:fb:1a:53:fb:e6" in result
    assert "aa:bb:cc:dd:ee:ff" in result


def test_parse_desk_list_empty() -> None:
    """Test parsing an empty desk list."""
    payload = []
    result = parse_desk_list(payload)

    assert len(result) == 0


def test_parse_desk_list_filters_empty_strings() -> None:
    """Test that empty strings are filtered out."""
    payload = ["cd:fb:1a:53:fb:e6", "", "aa:bb:cc:dd:ee:ff"]
    result = parse_desk_list(payload)

    assert len(result) == EXPECTED_COUNT_TWO
    assert "" not in result


def test_parse_desk_list_invalid_format() -> None:
    """Test handling of invalid format."""
    payload = {"invalid": "format"}

    with pytest.raises(ValueError, match="unexpected response format"):
        parse_desk_list(payload)


def test_parse_errors_success() -> None:
    """Test parsing error list."""
    errors_payload = [
        {"time_s": TEST_TIMESTAMP, "error_code": TEST_ERROR_CODE_1},
        {"time_s": 1234567900, "error_code": 2},
    ]
    result = parse_errors(errors_payload)

    assert len(result) == EXPECTED_COUNT_TWO
    assert all(isinstance(e, DeskError) for e in result)
    assert result[0].time_s == TEST_TIMESTAMP
    assert result[0].error_code == TEST_ERROR_CODE_1


def test_parse_errors_empty() -> None:
    """Test parsing empty error list."""
    result = parse_errors([])
    assert len(result) == 0


def test_parse_errors_none() -> None:
    """Test parsing None as errors."""
    result = parse_errors(None)
    assert len(result) == 0


def test_parse_errors_invalid_format() -> None:
    """Test parsing errors with invalid format."""
    errors_payload = "not a list"
    result = parse_errors(errors_payload)
    assert len(result) == 0


def test_parse_errors_with_invalid_entries() -> None:
    """Test parsing errors with some invalid entries."""
    errors_payload = [
        {"time_s": TEST_TIMESTAMP, "error_code": TEST_ERROR_CODE_1},
        "invalid entry",
        {"time_s": 1234567900, "error_code": 2},
    ]
    result = parse_errors(errors_payload)

    assert len(result) == EXPECTED_COUNT_TWO


def test_parse_config_success() -> None:
    """Test parsing desk configuration."""
    config_data = {
        "name": "Office Desk",
        "manufacturer": "DeskCorp",
    }
    result = parse_config(config_data)

    assert isinstance(result, DeskConfig)
    assert result.name == "Office Desk"
    assert result.manufacturer == "DeskCorp"


def test_parse_state_success() -> None:
    """Test parsing desk state."""
    state_data = {
        "position_mm": TEST_POSITION_800,
        "speed_mms": TEST_SPEED_10,
        "status": "moving",
        "isPositionLost": False,
        "isOverloadProtectionUp": False,
        "isOverloadProtectionDown": False,
        "isAntiCollision": True,
    }
    result = parse_state(state_data)

    assert isinstance(result, DeskState)
    assert result.position_mm == TEST_POSITION_800
    assert result.speed_mms == TEST_SPEED_10
    assert result.status == "moving"
    assert result.is_anti_collision is True


def test_parse_usage_success() -> None:
    """Test parsing desk usage."""
    usage_data = {
        "activationsCounter": TEST_ACTIVATIONS_250,
        "sitStandCounter": TEST_SIT_STAND_125,
    }
    result = parse_usage(usage_data)

    assert isinstance(result, DeskUsage)
    assert result.activations_counter == TEST_ACTIVATIONS_250
    assert result.sit_stand_counter == TEST_SIT_STAND_125


def test_parse_desk_success() -> None:
    """Test parsing complete desk data."""
    desk_data = {
        "config": {
            "name": "Test Desk",
            "manufacturer": "TestCo",
        },
        "state": {
            "position_mm": TEST_POSITION_750,
            "speed_mms": 0,
            "status": "idle",
            "isPositionLost": False,
            "isOverloadProtectionUp": False,
            "isOverloadProtectionDown": False,
            "isAntiCollision": False,
        },
        "usage": {
            "activationsCounter": TEST_ACTIVATIONS_100,
            "sitStandCounter": 50,
        },
        "lastErrors": [
            {"time_s": TEST_TIMESTAMP, "error_code": TEST_ERROR_CODE_1},
        ],
    }
    result = parse_desk(desk_data)

    assert isinstance(result, Desk)
    assert result.config.name == "Test Desk"
    assert result.state.position_mm == TEST_POSITION_750
    assert result.usage.activations_counter == TEST_ACTIVATIONS_100
    assert len(result.last_errors) == EXPECTED_COUNT_ONE


def test_parse_desk_with_missing_fields() -> None:
    """Test parsing desk data with missing optional fields."""
    desk_data = {
        "config": {"name": "Default Desk", "manufacturer": "Unknown"},
        "state": {
            "position_mm": 0,
            "speed_mms": 0,
            "status": "unknown",
            "isPositionLost": False,
            "isOverloadProtectionUp": False,
            "isOverloadProtectionDown": False,
            "isAntiCollision": False,
        },
        "usage": {"activationsCounter": 0, "sitStandCounter": 0},
    }
    result = parse_desk(desk_data)

    assert isinstance(result, Desk)
    assert len(result.last_errors) == 0


def test_parse_state_or_fallback_success() -> None:
    """Test parsing state with valid data."""
    state_data = {
        "position_mm": TEST_POSITION_1000,
        "speed_mms": 5,
        "status": "moving",
        "isPositionLost": False,
        "isOverloadProtectionUp": False,
        "isOverloadProtectionDown": False,
        "isAntiCollision": False,
    }
    result = parse_state_or_fallback(state_data, TEST_POSITION_1000)

    assert isinstance(result, DeskState)
    assert result.position_mm == TEST_POSITION_1000
    assert result.status == "moving"


def test_parse_state_or_fallback_with_fallback() -> None:
    """Test fallback when state data is invalid."""
    state_data = {}
    result = parse_state_or_fallback(state_data, TEST_POSITION_1200)

    assert isinstance(result, DeskState)
    assert result.position_mm == TEST_POSITION_1200
    assert result.status == "unknown"
    assert result.speed_mms == 0
