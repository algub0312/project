"""Integration tests for MQTT service with environment-aware testing."""

import asyncio
import json
import os
import socket
import time
from asyncio import AbstractEventLoop
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import paho.mqtt.client as mqtt
import pytest

from src.services.mqtt_service import MQTTService

# Constants for magic values
EXPECTED_RESULT_CODE = 0
DEFAULT_SOCKET_TIMEOUT = 2
CONNECTION_WAIT_TIME = 2
MESSAGE_PROCESSING_WAIT_TIME = 3
ASYNC_PROCESSING_WAIT_TIME = 0.1


def is_mqtt_broker_available(host: str = "localhost", port: int = 1883) -> bool:
    """Check if MQTT broker is available."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(DEFAULT_SOCKET_TIMEOUT)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == EXPECTED_RESULT_CODE
    except Exception:
        return False


class RealMosquittoContainer:
    """Real container connection to running Mosquitto broker."""

    def __init__(self, host: str = "localhost", port: int = 1883) -> None:
        """Initialize the container connection."""
        self.host = host
        self.port = port

    def __enter__(self) -> "RealMosquittoContainer":
        """Enter context manager."""
        return self

    def __exit__(self, *args: object) -> None:
        """Exit context manager."""

    def get_connection_params(self) -> object:
        """Get connection parameters.

        Returns:
            Connection parameters object with host and port attributes.

        """
        return type("obj", (object,), {"host": self.host, "port": self.port})


@pytest.fixture(scope="module")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    """Create an instance of the event loop for the module scope."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def mqtt_container() -> Generator[RealMosquittoContainer, None, None]:
    """Set up connection to real MQTT container."""
    with RealMosquittoContainer() as container:
        yield container


@pytest.mark.skipif(
    not is_mqtt_broker_available() or os.getenv("CI") == "true",
    reason="Requires real MQTT broker running on localhost:1883. Skip in CI.",
)
def test_mqtt_integration_real_broker(mqtt_container: RealMosquittoContainer) -> None:
    """Integration test with real MQTT broker running in Docker.

    This test only runs when:
    1. MQTT broker is available on localhost:1883
    2. Not running in CI environment
    """
    # Arrange
    mqtt_service = MQTTService()
    received_messages = []

    def capture_process_call(*args: object, **kwargs: object) -> None:
        """Capture process calls for testing."""
        received_messages.append(args)

    # Create a simple mock that captures calls without async issues
    mock_occupancy_service = MagicMock()
    mock_occupancy_service.process_mqtt_update = MagicMock(
        side_effect=capture_process_call
    )
    mqtt_service.set_occupancy_service(mock_occupancy_service)

    # Start MQTT service
    connection_params = mqtt_container.get_connection_params()
    mqtt_service.start(
        host=connection_params.host, port=connection_params.port, topic="occupancy/+"
    )

    # Wait for connection
    time.sleep(CONNECTION_WAIT_TIME)

    try:
        # Verify connection
        assert mqtt_service.is_connected, (
            "MQTT service should be connected to real broker"
        )

        # Publish test message using separate client
        test_client = mqtt.Client()
        test_client.connect(connection_params.host, connection_params.port, 60)

        test_message = {
            "desk_id": "desk_001",
            "state": True,
            "timestamp": "2025-01-01T10:00:00Z",
        }

        test_client.publish("occupancy/desk_001", json.dumps(test_message))
        test_client.disconnect()

        # Wait for message processing
        time.sleep(MESSAGE_PROCESSING_WAIT_TIME)

        # Assert
        assert len(received_messages) >= 1, (
            f"Expected at least 1 message, got {len(received_messages)}"
        )
        assert received_messages[0][0] == "desk_001"  # desk_id
        assert received_messages[0][1] is True  # occupied

    finally:
        # Cleanup
        mqtt_service.stop()


@pytest.mark.asyncio
async def test_mqtt_service_with_mocked_occupancy_service() -> None:
    """Test MQTT service with mocked occupancy service."""
    # Arrange
    mqtt_service = MQTTService()
    mock_occupancy_service = AsyncMock()
    mqtt_service.set_occupancy_service(mock_occupancy_service)

    # Create mock message
    test_payload = {
        "desk_id": "desk_001",
        "state": True,
        "timestamp": "2025-01-01T10:00:00Z",
    }
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(test_payload)

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Give async processing time to complete
    await asyncio.sleep(ASYNC_PROCESSING_WAIT_TIME)

    # Assert
    mock_occupancy_service.process_mqtt_update.assert_called()


def test_mqtt_connection_lifecycle() -> None:
    """Test MQTT connection establishment and teardown."""
    # Arrange
    mqtt_service = MQTTService()

    # Test initial state
    assert not mqtt_service.is_connected
    assert mqtt_service._client is None

    # Test connection callback
    mock_client = MagicMock()
    mqtt_service._topic = "occupancy/+"

    # Simulate successful connection
    mqtt_service._on_connect(mock_client, None, None, EXPECTED_RESULT_CODE)
    assert mqtt_service.is_connected
    mock_client.subscribe.assert_called_once_with("occupancy/+", qos=1)

    # Simulate disconnection
    mqtt_service._on_disconnect(mock_client, None, None)
    assert not mqtt_service.is_connected


@pytest.mark.asyncio
async def test_message_processing_error_handling() -> None:
    """Test error handling in message processing."""
    # Arrange
    mqtt_service = MQTTService()
    mock_occupancy_service = AsyncMock()
    mock_occupancy_service.process_mqtt_update.side_effect = Exception(
        "Processing error"
    )
    mqtt_service.set_occupancy_service(mock_occupancy_service)

    # Create mock message
    test_payload = {
        "desk_id": "desk_001",
        "state": True,
        "timestamp": "2025-01-01T10:00:00Z",
    }
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(test_payload)

    # Act - should not raise exception
    mqtt_service._on_message(None, None, mock_msg)

    # Give async processing time to complete
    await asyncio.sleep(ASYNC_PROCESSING_WAIT_TIME)

    # Assert
    mock_occupancy_service.process_mqtt_update.assert_called()


def test_mqtt_service_configuration() -> None:
    """Test MQTT service configuration and setup."""
    # Arrange
    mqtt_service = MQTTService()
    mock_occupancy_service = MagicMock()

    # Act
    mqtt_service.set_occupancy_service(mock_occupancy_service)

    # Assert
    assert mqtt_service._occupancy_service == mock_occupancy_service
    assert not mqtt_service.is_connected

    # Test that callbacks are properly set after start (mocked)
    with patch("src.services.mqtt_service.mqtt.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mqtt_service.start("localhost", 1883, "occupancy/+")

        # Verify client configuration
        assert mqtt_service._client == mock_client
        assert mqtt_service._topic == "occupancy/+"
        assert mqtt_service._client.on_connect is not None
        assert mqtt_service._client.on_message is not None
        assert mqtt_service._client.on_disconnect is not None


def test_invalid_json_message_handling() -> None:
    """Test handling of invalid JSON messages."""
    # Arrange
    mqtt_service = MQTTService()
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = "invalid json"

    # Act - should not raise exception
    mqtt_service._on_message(None, None, mock_msg)


def test_missing_required_fields() -> None:
    """Test handling of messages with missing required fields."""
    # Arrange
    mqtt_service = MQTTService()
    payload = {"desk_id": "desk_001"}  # Missing state and timestamp
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(payload)

    # Act - should not raise exception
    mqtt_service._on_message(None, None, mock_msg)
