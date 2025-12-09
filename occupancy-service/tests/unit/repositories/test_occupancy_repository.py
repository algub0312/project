"""Unit tests for OccupancyRepository."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.models.db.occupancy_record import OccupancyRecord
from src.repositories.occupancy_repository import OccupancyRepository

# Constants for magic values
EXPECTED_RECORD_COUNT = 2


@pytest.fixture
def mock_session() -> MagicMock:
    """Mock database session for testing."""
    return MagicMock()


@pytest.fixture
def repository(mock_session: MagicMock) -> OccupancyRepository:
    """Create OccupancyRepository instance with mocked session."""
    return OccupancyRepository(mock_session)


def test_create_record_success(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test successful creation of an occupancy record."""
    # Arrange
    record = OccupancyRecord(
        desk_id="desk_001",
        occupied=True,
        timestamp=datetime.now(),
    )

    # Act
    result = repository.create(record)

    # Assert
    mock_session.add.assert_called_once_with(record)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(record)
    assert result == record


def test_get_latest_by_desk_found(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test getting latest record for a desk when it exists."""
    # Arrange
    desk_id = "desk_001"
    expected_record = OccupancyRecord(
        id=uuid4(),
        desk_id=desk_id,
        occupied=True,
        timestamp=datetime.now(),
        created_at=datetime.now(),
    )

    mock_result = MagicMock()
    mock_result.first.return_value = expected_record
    mock_session.exec.return_value = mock_result

    # Act
    result = repository.get_latest_by_desk(desk_id)

    # Assert
    mock_session.exec.assert_called_once()
    mock_session.exec.call_args[0][0]
    assert result == expected_record


def test_get_latest_by_desk_not_found(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test getting latest record for a desk when it doesn't exist."""
    # Arrange
    desk_id = "nonexistent_desk"

    mock_result = MagicMock()
    mock_result.first.return_value = None
    mock_session.exec.return_value = mock_result

    # Act
    result = repository.get_latest_by_desk(desk_id)

    # Assert
    mock_session.exec.assert_called_once()
    assert result is None


def test_get_all_latest(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test getting latest records for all desks."""
    # Arrange
    mock_rows = [
        MagicMock(
            id=uuid4(),
            desk_id="desk_001",
            occupied=True,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
        MagicMock(
            id=uuid4(),
            desk_id="desk_002",
            occupied=False,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
    ]
    mock_session.exec.return_value = mock_rows

    # Act
    result = repository.get_all_latest()

    # Assert
    mock_session.exec.assert_called_once()
    assert len(result) == EXPECTED_RECORD_COUNT
    assert isinstance(result[0], OccupancyRecord)
    assert isinstance(result[1], OccupancyRecord)
    assert result[0].desk_id == "desk_001"
    assert result[1].desk_id == "desk_002"


def test_get_history_by_desk(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test getting occupancy history for a specific desk."""
    # Arrange
    desk_id = "desk_001"
    limit = 50
    expected_records = [
        OccupancyRecord(
            id=uuid4(),
            desk_id=desk_id,
            occupied=True,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
        OccupancyRecord(
            id=uuid4(),
            desk_id=desk_id,
            occupied=False,
            timestamp=datetime.now(),
            created_at=datetime.now(),
        ),
    ]

    mock_result = MagicMock()
    mock_result.all.return_value = expected_records
    mock_session.exec.return_value = mock_result

    # Act
    result = repository.get_history_by_desk(desk_id, limit)

    # Assert
    mock_session.exec.assert_called_once()
    mock_session.exec.call_args[0][0]
    assert result == expected_records


def test_get_history_by_desk_default_limit(
    repository: OccupancyRepository, mock_session: MagicMock
) -> None:
    """Test getting occupancy history with default limit."""
    # Arrange
    desk_id = "desk_001"
    expected_records = []

    mock_result = MagicMock()
    mock_result.all.return_value = expected_records
    mock_session.exec.return_value = mock_result

    # Act
    result = repository.get_history_by_desk(desk_id)  # No limit specified

    # Assert
    mock_session.exec.assert_called_once()
    assert result == expected_records
