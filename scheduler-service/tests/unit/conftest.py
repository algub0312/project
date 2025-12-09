"""Pytest configuration and fixtures for unit tests."""

import os
import sys
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest

# This prevents desk_service from trying to load real config during import
os.environ.setdefault("DESK_API_BASE_URL", "http://localhost:8000/api/v2")
os.environ.setdefault("DESK_API_KEY", "test-api-key-for-unit-tests")
os.environ.setdefault("DESK_API_TIMEOUT_SECONDS", "10")
os.environ.setdefault("RABBITMQ_HOST", "localhost")
os.environ.setdefault("RABBITMQ_PORT", "5672")
os.environ.setdefault("RABBITMQ_USERNAME", "guest")
os.environ.setdefault("RABBITMQ_PASSWORD", "guest")  # noqa: S105  (tests only)

# Add src directory to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def reset_env_vars() -> Iterator[None]:
    """Reset environment variables for each test."""
    original_env = os.environ.copy()

    # Ensure required env vars are set
    os.environ["DESK_API_BASE_URL"] = "http://localhost:8000/api/v2"
    os.environ["DESK_API_KEY"] = "test-api-key-for-unit-tests"
    os.environ["DESK_API_TIMEOUT_SECONDS"] = "10"
    os.environ["RABBITMQ_HOST"] = "localhost"
    os.environ["RABBITMQ_PORT"] = "5672"
    os.environ["RABBITMQ_USERNAME"] = "guest"
    os.environ["RABBITMQ_PASSWORD"] = "guest"  # noqa: S105  (tests only)

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_desk_service() -> Mock:
    """Fixture to mock DeskService."""
    mock = Mock()
    return mock


@pytest.fixture
def mock_scheduler() -> Mock:
    """Fixture to mock APScheduler."""
    mock = Mock()
    mock.state = 1  # STATE_RUNNING
    return mock
