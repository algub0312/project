"""Integration tests for desk integration router."""

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app
from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage

# Test constants
EXPECTED_DESK_COUNT = 2
TEST_POSITION_750 = 750
TEST_POSITION_800 = 800
TEST_POSITION_1000 = 1000
TEST_SPEED_10 = 10
TEST_ACTIVATIONS_250 = 250
TEST_SIT_STAND_125 = 125
TEST_TIMESTAMP_1 = 1234567890
TEST_TIMESTAMP_2 = 1234567900
TEST_ERROR_CODE_1 = 1
TEST_ERROR_CODE_2 = 2


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_desk_service() -> MagicMock:
    """Create a mock DeskService."""
    return MagicMock()


def test_get_desks_success(client: TestClient, mock_desk_service: MagicMock) -> None:
    """Test GET /api/v1/desks returns list of desks."""
    mock_desk_service.get_all_desks.return_value = [
        "cd:fb:1a:53:fb:e6",
        "aa:bb:cc:dd:ee:ff",
    ]

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == EXPECTED_DESK_COUNT
    assert "cd:fb:1a:53:fb:e6" in response.json()


def test_get_desk_by_id_success(
    client: TestClient, mock_desk_service: MagicMock
) -> None:
    """Test GET /api/v1/desks/{desk_id} returns desk details."""
    mock_desk = Desk(
        config=DeskConfig(name="Test Desk", manufacturer="TestCo"),
        state=DeskState(
            position_mm=TEST_POSITION_750,
            speed_mms=0,
            status="idle",
            is_position_lost=False,
            is_overload_protection_up=False,
            is_overload_protection_down=False,
            is_anti_collision=False,
        ),
        usage=DeskUsage(activations_counter=100, sit_stand_counter=50),
        last_errors=[],
    )
    mock_desk_service.get_desk_by_id.return_value = mock_desk

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks/cd:fb:1a:53:fb:e6")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["config"]["name"] == "Test Desk"
    assert data["state"]["position_mm"] == TEST_POSITION_750


def test_get_config_success(client: TestClient, mock_desk_service: MagicMock) -> None:
    """Test GET /api/v1/desks/{desk_id}/config returns configuration."""
    mock_config = DeskConfig(name="Office Desk", manufacturer="DeskCorp")
    mock_desk_service.get_desk_config.return_value = mock_config

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks/cd:fb:1a:53:fb:e6/config")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Office Desk"
    assert data["manufacturer"] == "DeskCorp"


def test_get_state_success(client: TestClient, mock_desk_service: MagicMock) -> None:
    """Test GET /api/v1/desks/{desk_id}/state returns desk state."""
    mock_state = DeskState(
        position_mm=TEST_POSITION_800,
        speed_mms=TEST_SPEED_10,
        status="moving",
        is_position_lost=False,
        is_overload_protection_up=False,
        is_overload_protection_down=False,
        is_anti_collision=False,
    )
    mock_desk_service.get_desk_state.return_value = mock_state

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks/cd:fb:1a:53:fb:e6/state")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["position_mm"] == TEST_POSITION_800
    assert data["speed_mms"] == TEST_SPEED_10


def test_set_desk_height_success(
    client: TestClient, mock_desk_service: MagicMock
) -> None:
    """Test PUT /api/v1/desks/{desk_id}/state sets desk height."""
    mock_state = DeskState(
        position_mm=TEST_POSITION_1000,
        speed_mms=0,
        status="idle",
        is_position_lost=False,
        is_overload_protection_up=False,
        is_overload_protection_down=False,
        is_anti_collision=False,
    )
    mock_desk_service.set_desk_position.return_value = mock_state

    with (
        patch("src.routers.desk_integration.desks_service", mock_desk_service),
    ):
        response = client.put("/api/v1/desks/cd:fb:1a:53:fb:e6/state?position_mm=1000")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["position_mm"] == TEST_POSITION_1000
    mock_desk_service.set_desk_position.assert_called_once_with(
        "cd:fb:1a:53:fb:e6", TEST_POSITION_1000
    )


def test_get_usage_success(client: TestClient, mock_desk_service: MagicMock) -> None:
    """Test GET /api/v1/desks/{desk_id}/usage returns desk usage."""
    mock_usage = DeskUsage(
        activations_counter=TEST_ACTIVATIONS_250,
        sit_stand_counter=TEST_SIT_STAND_125,
    )
    mock_desk_service.get_desk_usage.return_value = mock_usage

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks/cd:fb:1a:53:fb:e6/usage")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["activations_counter"] == TEST_ACTIVATIONS_250
    assert data["sit_stand_counter"] == TEST_SIT_STAND_125


def test_get_errors_success(client: TestClient, mock_desk_service: MagicMock) -> None:
    """Test GET /api/v1/desks/{desk_id}/errors returns desk errors."""
    mock_errors = [
        DeskError(time_s=TEST_TIMESTAMP_1, error_code=TEST_ERROR_CODE_1),
        DeskError(time_s=TEST_TIMESTAMP_2, error_code=TEST_ERROR_CODE_2),
    ]
    mock_desk_service.get_desk_errors.return_value = mock_errors

    with patch("src.routers.desk_integration.desks_service", mock_desk_service):
        response = client.get("/api/v1/desks/cd:fb:1a:53:fb:e6/errors")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == EXPECTED_DESK_COUNT
    assert data[0]["error_code"] == TEST_ERROR_CODE_1
