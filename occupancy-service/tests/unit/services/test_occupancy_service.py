"""Unit tests for OccupancyService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.models.db.occupancy_record import OccupancyRecord
from src.services.occupancy_service import OccupancyService

# Constants for magic values
EXPECTED_RECORD_COUNT = 2


@pytest.fixture
def mock_repository() -> MagicMock:
    """Mock repository for testing."""
    return MagicMock()


@pytest.fixture
def mock_messaging() -> MagicMock:
    """Mock messaging manager for testing."""
    messaging = MagicMock()
    messaging.get_pubsub = MagicMock()
    pubsub = MagicMock()
    pubsub.publish = AsyncMock()
    messaging.get_pubsub.return_value = pubsub
    return messaging


@pytest.fixture
def service(mock_repository: MagicMock, mock_messaging: MagicMock) -> OccupancyService:
    """Create OccupancyService instance with mocked dependencies."""
    return OccupancyService(mock_repository, mock_messaging)


@patch("src.services.occupancy_service.datetime")
@pytest.mark.asyncio
async def test_process_mqtt_update_success(
    mock_datetime: MagicMock,
    service: OccupancyService,
    mock_repository: MagicMock,
    mock_messaging: MagicMock,
) -> None:
    """Test successful processing of MQTT update."""
    # Arrange
    desk_id = "desk_001"
    occupied = True
    input_timestamp = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    server_timestamp = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    # Mock datetime.now() to return a fixed time
    mock_datetime.now.return_value = server_timestamp

    created_record = OccupancyRecord(
        id=uuid4(),
        desk_id=desk_id,
        occupied=occupied,
        timestamp=server_timestamp,  # Should use server time, not input
        created_at=datetime.now(),
    )
    mock_repository.create.return_value = created_record

    # Act
    result = await service.process_mqtt_update(desk_id, occupied, input_timestamp)

    # Assert
    mock_repository.create.assert_called_once()
    created_record_arg = mock_repository.create.call_args[0][0]
    assert created_record_arg.desk_id == desk_id
    assert created_record_arg.occupied == occupied
    # Should use server timestamp, not input timestamp
    assert created_record_arg.timestamp == server_timestamp

    # Verify messaging was called
    pubsub = mock_messaging.get_pubsub.return_value
    pubsub.publish.assert_called_once()

    # Verify response
    assert result.desk_id == desk_id
    assert result.occupied == occupied
    assert result.timestamp == server_timestamp


@pytest.mark.asyncio
async def test_process_mqtt_update_messaging_failure(
    service: OccupancyService,
    mock_repository: MagicMock,
    mock_messaging: MagicMock,
    capfd: pytest.CaptureFixture[str],
) -> None:
    """Test MQTT update processing when messaging fails."""
    # Arrange
    desk_id = "desk_001"
    occupied = True
    timestamp = datetime.now()

    created_record = OccupancyRecord(
        id=uuid4(),
        desk_id=desk_id,
        occupied=occupied,
        timestamp=timestamp,
        created_at=datetime.now(),
    )
    mock_repository.create.return_value = created_record

    # Make messaging fail
    pubsub = mock_messaging.get_pubsub.return_value
    pubsub.publish.side_effect = Exception("Messaging error")

    # Act
    result = await service.process_mqtt_update(desk_id, occupied, timestamp)

    # Assert
    mock_repository.create.assert_called_once()
    pubsub.publish.assert_called_once()

    # Verify error was captured
    captured = capfd.readouterr()
    assert "Failed to publish occupancy update" in captured.out

    # Verify response is still returned
    assert result.desk_id == desk_id


def test_get_current_occupancy_found(
    service: OccupancyService, mock_repository: MagicMock
) -> None:
    """Test getting current occupancy when record exists."""
    # Arrange
    desk_id = "desk_001"
    record = OccupancyRecord(
        id=uuid4(),
        desk_id=desk_id,
        occupied=True,
        timestamp=datetime.now(),
        created_at=datetime.now(),
    )
    mock_repository.get_latest_by_desk.return_value = record

    # Act
    result = service.get_current_occupancy(desk_id)

    # Assert
    mock_repository.get_latest_by_desk.assert_called_once_with(desk_id)
    assert result is not None
    assert result.desk_id == desk_id
    assert result.occupied == record.occupied
    assert result.last_updated == record.timestamp


def test_get_current_occupancy_not_found(
    service: OccupancyService, mock_repository: MagicMock
) -> None:
    """Test getting current occupancy when no record exists."""
    # Arrange
    desk_id = "nonexistent_desk"
    mock_repository.get_latest_by_desk.return_value = None

    # Act
    result = service.get_current_occupancy(desk_id)

    # Assert
    mock_repository.get_latest_by_desk.assert_called_once_with(desk_id)
    assert result is None


def test_get_all_current_occupancy(
    service: OccupancyService, mock_repository: MagicMock
) -> None:
    """Test getting all current occupancy statuses."""
    # Arrange
    records = [
        OccupancyRecord(
            id=uuid4(),
            desk_id="desk_001",
            occupied=True,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
        OccupancyRecord(
            id=uuid4(),
            desk_id="desk_002",
            occupied=False,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
    ]
    mock_repository.get_all_latest.return_value = records

    # Act
    result = service.get_all_current_occupancy()

    # Assert
    mock_repository.get_all_latest.assert_called_once()
    assert len(result) == EXPECTED_RECORD_COUNT
    assert result[0].desk_id == "desk_001"
    assert result[0].occupied is True
    assert result[1].desk_id == "desk_002"
    assert result[1].occupied is False


def test_get_occupancy_history(
    service: OccupancyService, mock_repository: MagicMock
) -> None:
    """Test getting occupancy history for a desk."""
    # Arrange
    desk_id = "desk_001"
    limit = 50
    records = [
        OccupancyRecord(
            id=uuid4(),
            desk_id=desk_id,
            occupied=True,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
    ]
    mock_repository.get_history_by_desk.return_value = records

    # Act
    result = service.get_occupancy_history(desk_id, limit)

    # Assert
    mock_repository.get_history_by_desk.assert_called_once_with(desk_id, limit)
    assert len(result) == 1
    assert result[0].desk_id == desk_id
    assert result[0].occupied is True
