"""Unit tests for configuration."""

import os
from unittest.mock import patch

import pytest

from src.services.config import DeskServiceConfig, load_timeout

# Constants for test values
DEFAULT_TIMEOUT = 10
TEST_TIMEOUT_15 = 15
TEST_TIMEOUT_20 = 20
TEST_TIMEOUT_30 = 30


def test_desk_service_config_creation() -> None:
    """Test creating DeskServiceConfig directly."""
    config = DeskServiceConfig(
        base_url="http://example.com",
        api_key="test_key",
        timeout=TEST_TIMEOUT_15,
    )

    assert config.base_url == "http://example.com"
    assert config.api_key == "test_key"
    assert config.timeout == TEST_TIMEOUT_15


def test_desk_service_config_default_timeout() -> None:
    """Test default timeout value."""
    config = DeskServiceConfig(
        base_url="http://example.com",
        api_key="test_key",
    )

    assert config.timeout == DEFAULT_TIMEOUT


@patch.dict(
    os.environ,
    {
        "OPERATING_SYSTEM": "windows",
        "DESK_API_BASE_URL_WINDOWS": "http://test.api",
        "DESK_API_KEY": "test_key_123",
        "DESK_API_TIMEOUT_SECONDS": "20",
    },
)
def test_from_env_success() -> None:
    """Test loading configuration from environment variables."""
    config = DeskServiceConfig.from_env()

    assert config.base_url == "http://test.api"
    assert config.api_key == "test_key_123"
    assert config.timeout == TEST_TIMEOUT_20


@patch.dict(
    os.environ,
    {
        "OPERATING_SYSTEM": "windows",
        "DESK_API_BASE_URL_WINDOWS": "http://test.api/",
        "DESK_API_KEY": "test_key",
    },
)
def test_from_env_strips_trailing_slash() -> None:
    """Test that trailing slash is removed from base URL."""
    config = DeskServiceConfig.from_env()

    assert config.base_url == "http://test.api"


@patch.dict(
    os.environ,
    {
        "OPERATING_SYSTEM": "windows",
        "DESK_API_BASE_URL_WINDOWS": "http://test.api",
    },
    clear=True,
)
def test_from_env_missing_api_key() -> None:
    """Test error when API key is missing."""
    with pytest.raises(ValueError, match="DESK_API_KEY is required"):
        DeskServiceConfig.from_env()


@patch.dict(
    os.environ,
    {
        "OPERATING_SYSTEM": "windows",
        "DESK_API_BASE_URL_WINDOWS": "http://test.api",
        "DESK_API_KEY": "",
    },
    clear=True,
)
def test_from_env_empty_api_key() -> None:
    """Test error when API key is empty."""
    with pytest.raises(ValueError, match="DESK_API_KEY is required"):
        DeskServiceConfig.from_env()


def test_load_timeout_valid() -> None:
    """Test loading valid timeout value."""
    with patch.dict(os.environ, {"DESK_API_TIMEOUT_SECONDS": "30"}):
        timeout = load_timeout()
        assert timeout == TEST_TIMEOUT_30


def test_load_timeout_invalid() -> None:
    """Test loading invalid timeout value falls back to default."""
    with patch.dict(os.environ, {"DESK_API_TIMEOUT_SECONDS": "invalid"}):
        timeout = load_timeout()
        assert timeout == DEFAULT_TIMEOUT


def test_load_timeout_missing() -> None:
    """Test missing timeout value uses default."""
    with patch.dict(os.environ, {}, clear=True):
        timeout = load_timeout()
        assert timeout == DEFAULT_TIMEOUT
