"""Tests for main FastAPI application."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app
from src.messaging.messaging_manager import messaging_manager


# Mocking messaging manager to prevent real connection attempts during testing
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
def client(
    mock_messaging_manager: MagicMock,
) -> Generator[TestClient, None, None]:
    """Fixture to initialize the FastAPI TestClient."""
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    """Test the health check endpoint (GET /health)."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}
