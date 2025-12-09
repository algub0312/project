"""Unit tests for MQTTService."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.mqtt_service import MQTTService


@pytest.fixture
def mqtt_service() -> MQTTService:
    """Create MQTTService instance for testing."""
    return MQTTService()


@pytest.fixture
def mock_mqtt_client() -> MagicMock:
    """Mock MQTT client for testing."""
    return MagicMock()


def test_init(mqtt_service: MQTTService) -> None:
    """Test MQTTService initialization."""
    assert mqtt_service._client is None
    assert mqtt_service._connected is False
    assert mqtt_service._occupancy_service is None


@patch("src.services.mqtt_service.mqtt.Client")
@patch("threading.Thread")
def test_start_success(
    mock_thread: MagicMock,
    mock_client_class: MagicMock,
    mqtt_service: MQTTService,
    mock_mqtt_client: MagicMock,
) -> None:
    """Test successful MQTT service start."""
    # Arrange
    mock_client_class.return_value = mock_mqtt_client
    mock_thread_instance = MagicMock()
    mock_thread.return_value = mock_thread_instance

    host = "localhost"
    port = 1883
    topic = "occupancy/+"

    # Act
    mqtt_service.start(host, port, topic)

    # Assert
    mock_client_class.assert_called_once()
    assert mqtt_service._client == mock_mqtt_client
    assert mqtt_service._topic == topic

    # Verify callbacks are set
    assert mqtt_service._client.on_connect is not None
    assert mqtt_service._client.on_message is not None
    assert mqtt_service._client.on_disconnect is not None

    # Verify connection attempt
    mock_mqtt_client.connect.assert_called_once_with(host, port, 60)
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()


@patch("src.services.mqtt_service.mqtt.Client")
def test_start_connection_failure(
    mock_client_class: MagicMock,
    mqtt_service: MQTTService,
    mock_mqtt_client: MagicMock,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Test MQTT service start when connection fails."""
    # Arrange
    mock_client_class.return_value = mock_mqtt_client
    mock_mqtt_client.connect.side_effect = Exception("Connection failed")

    host = "localhost"
    port = 1883
    topic = "occupancy/+"

    # Act
    mqtt_service.start(host, port, topic)

    # Assert
    captured = capfd.readouterr()
    assert "Failed to start MQTT client" in captured.out


def test_stop(mqtt_service: MQTTService, mock_mqtt_client: MagicMock) -> None:
    """Test MQTT service stop."""
    # Arrange
    mqtt_service._client = mock_mqtt_client

    # Act
    mqtt_service.stop()

    # Assert
    mock_mqtt_client.disconnect.assert_called_once()


def test_stop_no_client(mqtt_service: MQTTService) -> None:
    """Test MQTT service stop when no client exists."""
    # Act (should not raise exception)
    mqtt_service.stop()


def test_set_occupancy_service(mqtt_service: MQTTService) -> None:
    """Test setting occupancy service."""
    # Arrange
    mock_service = MagicMock()

    # Act
    mqtt_service.set_occupancy_service(mock_service)

    # Assert
    assert mqtt_service._occupancy_service == mock_service


def test_is_connected_true(mqtt_service: MQTTService) -> None:
    """Test is_connected when connected."""
    # Arrange
    mqtt_service._connected = True

    # Act & Assert
    assert mqtt_service.is_connected is True


def test_is_connected_false(mqtt_service: MQTTService) -> None:
    """Test is_connected when not connected."""
    # Arrange
    mqtt_service._connected = False

    # Act & Assert
    assert mqtt_service.is_connected is False


def test_on_connect_success(
    mqtt_service: MQTTService,
    mock_mqtt_client: MagicMock,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Test successful MQTT connection callback."""
    # Arrange
    mqtt_service._topic = "occupancy/+"

    # Act
    mqtt_service._on_connect(mock_mqtt_client, None, None, 0)

    # Assert
    assert mqtt_service._connected is True
    mock_mqtt_client.subscribe.assert_called_once_with("occupancy/+", qos=1)
    captured = capfd.readouterr()
    assert "Connected to MQTT broker" in captured.out


def test_on_connect_failure(
    mqtt_service: MQTTService,
    mock_mqtt_client: MagicMock,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Test failed MQTT connection callback."""
    # Act
    mqtt_service._on_connect(mock_mqtt_client, None, None, 1)

    # Assert
    assert mqtt_service._connected is False
    mock_mqtt_client.subscribe.assert_not_called()
    captured = capfd.readouterr()
    assert "Failed to connect to MQTT broker" in captured.out


def test_on_disconnect(
    mqtt_service: MQTTService, capfd: pytest.CaptureFixture[str]
) -> None:
    """Test MQTT disconnection callback."""
    # Arrange
    mqtt_service._connected = True

    # Act
    mqtt_service._on_disconnect(None, None, None)

    # Assert
    assert mqtt_service._connected is False
    captured = capfd.readouterr()
    assert "Disconnected from MQTT broker" in captured.out


@patch("asyncio.get_event_loop")
@patch("asyncio.new_event_loop")
@patch("asyncio.set_event_loop")
def test_on_message_success(
    mock_set_event_loop: MagicMock,
    mock_new_event_loop: MagicMock,
    mock_get_event_loop: MagicMock,
    mqtt_service: MQTTService,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Test successful MQTT message processing."""
    # Arrange
    mock_occupancy_service = AsyncMock()
    mqtt_service._occupancy_service = mock_occupancy_service

    # Mock event loop
    mock_loop = MagicMock()
    mock_get_event_loop.side_effect = RuntimeError("No event loop")
    mock_new_event_loop.return_value = mock_loop

    # Create mock message
    payload = {
        "desk_id": "desk_001",
        "state": True,
        "timestamp": "2025-01-01T10:00:00Z",
    }
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(payload)

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Assert
    mock_loop.run_until_complete.assert_called_once()
    captured = capfd.readouterr()
    assert "Successfully processed MQTT message" in captured.out


def test_on_message_invalid_json(
    mqtt_service: MQTTService, capfd: pytest.CaptureFixture[str]
) -> None:
    """Test MQTT message processing with invalid JSON."""
    # Arrange
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = "invalid json"

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Assert
    captured = capfd.readouterr()
    assert "Invalid JSON in MQTT message" in captured.out


def test_on_message_missing_fields(
    mqtt_service: MQTTService, capfd: pytest.CaptureFixture[str]
) -> None:
    """Test MQTT message processing with missing required fields."""
    # Arrange
    payload = {"desk_id": "desk_001"}  # Missing state and timestamp
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(payload)

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Assert
    captured = capfd.readouterr()
    assert "Invalid payload: missing required fields" in captured.out


def test_on_message_no_service(
    mqtt_service: MQTTService, capfd: pytest.CaptureFixture[str]
) -> None:
    """Test MQTT message processing when no occupancy service is set."""
    # Arrange
    payload = {
        "desk_id": "desk_001",
        "state": True,
        "timestamp": "2025-01-01T10:00:00Z",
    }
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(payload)

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Assert - should not crash, just not process
    captured = capfd.readouterr()
    assert "Received MQTT message" in captured.out


def test_on_message_with_timestamp_ignored(
    mqtt_service: MQTTService, capfd: pytest.CaptureFixture[str]
) -> None:
    """Test MQTT message processing with timestamp that gets ignored."""
    # Arrange
    mock_occupancy_service = AsyncMock()
    mqtt_service._occupancy_service = mock_occupancy_service

    # Include timestamp but it should be ignored
    payload = {"desk_id": "desk_001", "state": True, "timestamp": "invalid-timestamp"}
    mock_msg = MagicMock()
    mock_msg.payload.decode.return_value = json.dumps(payload)

    # Act
    mqtt_service._on_message(None, None, mock_msg)

    # Assert
    captured = capfd.readouterr()
    # Should not see the old error message, just the new current timestamp message
    assert "Using current server timestamp" in captured.out
    assert "Invalid timestamp format, using current time" not in captured.out
