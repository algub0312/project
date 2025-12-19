"""Unit tests for DeskService."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage
from src.services.config import DeskServiceConfig
from src.services.desk_service import DeskService
from src.services.exceptions import DeskServiceError

# Test constants
EXPECTED_DESK_COUNT = 2
TEST_POSITION_750 = 750
TEST_POSITION_800 = 800
TEST_POSITION_1000 = 1000
TEST_SPEED_10 = 10
TEST_ACTIVATIONS_100 = 100
TEST_ACTIVATIONS_250 = 250
TEST_SIT_STAND_125 = 125
TEST_ERROR_CODE_1 = 1
TEST_ERROR_CODE_2 = 2


@pytest.fixture
def mock_config() -> DeskServiceConfig:
    """Create a mock configuration for testing."""
    return DeskServiceConfig(
        base_url="http://test.api",
        api_key="test_key",
        timeout=10,
    )


@pytest.fixture
def desk_service(mock_config: DeskServiceConfig) -> DeskService:
    """Create a DeskService instance with mock config."""
    return DeskService(config=mock_config)


@pytest.fixture
def mock_response() -> MagicMock:
    """Create a mock response object."""
    response = MagicMock(spec=requests.Response)
    response.status_code = 200
    return response


def test_get_all_desks_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of all desks."""
    mock_response.json.return_value = [
        "cd:fb:1a:53:fb:e6",
        "aa:bb:cc:dd:ee:ff",
    ]

    with patch.object(desk_service.client, "request", return_value=mock_response):
        desks = desk_service.get_all_desks()

    assert len(desks) == EXPECTED_DESK_COUNT
    assert "cd:fb:1a:53:fb:e6" in desks
    assert "aa:bb:cc:dd:ee:ff" in desks


def test_get_all_desks_invalid_json(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test handling of invalid JSON response."""
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with (
        patch.object(desk_service.client, "request", return_value=mock_response),
        pytest.raises(DeskServiceError, match="Invalid JSON response"),
    ):
        desk_service.get_all_desks()


def test_get_desk_by_id_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of a desk by ID."""
    mock_response.json.return_value = {
        "config": {"name": "Test Desk", "manufacturer": "TestCo"},
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
        "lastErrors": [],
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        desk = desk_service.get_desk_by_id("cd:fb:1a:53:fb:e6")

    assert isinstance(desk, Desk)
    assert desk.config.name == "Test Desk"
    assert desk.state.position_mm == TEST_POSITION_750
    assert desk.usage.activations_counter == TEST_ACTIVATIONS_100


def test_get_desk_by_id_empty_id(desk_service: DeskService) -> None:
    """Test handling of empty desk ID."""
    result = desk_service.get_desk_by_id("")
    assert result is None


def test_get_desk_by_id_not_found(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test handling when desk is not found."""
    with patch.object(
        desk_service.client, "request", side_effect=DeskServiceError("Not found")
    ):
        desk = desk_service.get_desk_by_id("invalid_id")

    assert desk is None


def test_get_desk_config_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of desk configuration."""
    mock_response.json.return_value = {
        "name": "Office Desk",
        "manufacturer": "DeskCorp",
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        config = desk_service.get_desk_config("cd:fb:1a:53:fb:e6")

    assert isinstance(config, DeskConfig)
    assert config.name == "Office Desk"
    assert config.manufacturer == "DeskCorp"


def test_get_desk_state_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of desk state."""
    mock_response.json.return_value = {
        "position_mm": TEST_POSITION_800,
        "speed_mms": TEST_SPEED_10,
        "status": "moving",
        "isPositionLost": False,
        "isOverloadProtectionUp": False,
        "isOverloadProtectionDown": False,
        "isAntiCollision": False,
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        state = desk_service.get_desk_state("cd:fb:1a:53:fb:e6")

    assert isinstance(state, DeskState)
    assert state.position_mm == TEST_POSITION_800
    assert state.speed_mms == TEST_SPEED_10
    assert state.status == "moving"


def test_get_desk_usage_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of desk usage."""
    mock_response.json.return_value = {
        "activationsCounter": TEST_ACTIVATIONS_250,
        "sitStandCounter": TEST_SIT_STAND_125,
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        usage = desk_service.get_desk_usage("cd:fb:1a:53:fb:e6")

    assert isinstance(usage, DeskUsage)
    assert usage.activations_counter == TEST_ACTIVATIONS_250
    assert usage.sit_stand_counter == TEST_SIT_STAND_125


def test_get_desk_errors_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful retrieval of desk errors."""
    mock_response.json.return_value = {
        "lastErrors": [
            {"time_s": 1234567890, "error_code": TEST_ERROR_CODE_1},
            {"time_s": 1234567900, "error_code": TEST_ERROR_CODE_2},
        ]
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        errors = desk_service.get_desk_errors("cd:fb:1a:53:fb:e6")

    assert isinstance(errors, list)
    assert len(errors) == EXPECTED_DESK_COUNT
    assert all(isinstance(e, DeskError) for e in errors)
    assert errors[0].error_code == TEST_ERROR_CODE_1
    assert errors[1].error_code == TEST_ERROR_CODE_2


def test_set_desk_position_success(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test successful setting of desk position."""
    mock_response.json.return_value = {
        "position_mm": TEST_POSITION_1000,
        "speed_mms": 0,
        "status": "idle",
        "isPositionLost": False,
        "isOverloadProtectionUp": False,
        "isOverloadProtectionDown": False,
        "isAntiCollision": False,
    }

    with patch.object(desk_service.client, "request", return_value=mock_response):
        state = desk_service.set_desk_position("cd:fb:1a:53:fb:e6", TEST_POSITION_1000)

    assert isinstance(state, DeskState)
    assert state.position_mm == TEST_POSITION_1000


def test_set_desk_position_empty_id(desk_service: DeskService) -> None:
    """Test handling of empty desk ID when setting position."""
    with pytest.raises(DeskServiceError, match="Desk identifier is required"):
        desk_service.set_desk_position("", TEST_POSITION_1000)


def test_set_desk_position_invalid_position(desk_service: DeskService) -> None:
    """Test handling of invalid position value."""
    with pytest.raises(DeskServiceError, match="Invalid position"):
        desk_service.set_desk_position("cd:fb:1a:53:fb:e6", -100)


def test_set_desk_position_with_fallback(
    desk_service: DeskService, mock_response: MagicMock
) -> None:
    """Test position setting with fallback when response is incomplete."""
    mock_response.json.return_value = {}

    with patch.object(desk_service.client, "request", return_value=mock_response):
        state = desk_service.set_desk_position("cd:fb:1a:53:fb:e6", TEST_POSITION_1000)

    assert isinstance(state, DeskState)
    assert state.position_mm == TEST_POSITION_1000
    assert state.status == "unknown"
