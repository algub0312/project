"""Unit tests for the main application entry point."""

import importlib
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

import main
from main import app
from src.messaging.messaging_manager import messaging_manager
from src.services.mqtt_service import mqtt_service


@pytest.fixture
def mock_messaging_manager() -> MagicMock:
    """Mock the messaging manager for testing purposes."""
    mock = MagicMock()
    mock.start_all = AsyncMock()
    mock.stop_all = AsyncMock()
    mock.add_pubsub = MagicMock()

    # Assign the mocked methods to the actual messaging manager
    messaging_manager.add_pubsub = mock.add_pubsub
    messaging_manager.start_all = mock.start_all
    messaging_manager.stop_all = mock.stop_all
    return mock


@pytest.fixture
def mock_mqtt_service() -> MagicMock:
    """Mock the MQTT service for testing purposes."""
    mock = MagicMock()
    mock.start = MagicMock()
    mock.stop = MagicMock()
    mock.set_occupancy_service = MagicMock()

    # Replace the global mqtt_service
    mqtt_service.start = mock.start
    mqtt_service.stop = mock.stop
    mqtt_service.set_occupancy_service = mock.set_occupancy_service
    mqtt_service._connected = True
    return mock


@pytest.fixture
def mock_get_occupancy_service() -> MagicMock:
    """Mock the get_occupancy_service dependency."""
    with patch("src.api.dependencies.get_occupancy_service") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def client(
    mock_messaging_manager: MagicMock,
    mock_mqtt_service: MagicMock,
    mock_get_occupancy_service: MagicMock,
) -> Generator[TestClient, None, None]:
    """Fixture to initialize the FastAPI TestClient with mocked services."""
    with TestClient(app) as client:
        yield client


def test_root(client: TestClient) -> None:
    """Test the root endpoint (GET /)."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"service": "Occupancy Service"}


def test_health(client: TestClient) -> None:
    """Test the health check endpoint (GET /health)."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "ok"
    assert "mqtt_connected" in data
    assert "mqtt_topic" in data


@patch.dict("os.environ", {"AMQP_URL": "", "MQTT_HOST": "test", "MQTT_PORT": "1883"})
def test_missing_amqp_url() -> None:
    """Test that missing AMQP_URL raises ValueError."""
    with pytest.raises(ValueError, match="AMQP_URL is not set"):
        # Re-import to trigger the environment check

        importlib.reload(main)
