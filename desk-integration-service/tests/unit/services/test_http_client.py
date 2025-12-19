"""Unit tests for DeskAPIClient."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.services.config import DeskServiceConfig
from src.services.exceptions import DeskServiceError
from src.services.http_client import DeskAPIClient

# Test constants
HTTP_OK = 200
HTTP_NOT_FOUND = 404
HTTP_SERVER_ERROR = 500
DEFAULT_TIMEOUT = 10


@pytest.fixture
def mock_config() -> DeskServiceConfig:
    """Create a mock configuration for testing."""
    return DeskServiceConfig(
        base_url="http://test.api",
        api_key="test_key_123",
        timeout=DEFAULT_TIMEOUT,
    )


@pytest.fixture
def client(mock_config: DeskServiceConfig) -> DeskAPIClient:
    """Create a DeskAPIClient instance."""
    return DeskAPIClient(config=mock_config)


def test_build_url_simple(client: DeskAPIClient) -> None:
    """Test building a simple URL."""
    url = client.build_url("desks/")
    assert url == "http://test.api/test_key_123/desks/"


def test_build_url_with_id(client: DeskAPIClient) -> None:
    """Test building URL with desk ID."""
    url = client.build_url("desks", "cd:fb:1a:53:fb:e6")
    assert url == "http://test.api/test_key_123/desks/cd:fb:1a:53:fb:e6"


def test_build_url_with_multiple_segments(client: DeskAPIClient) -> None:
    """Test building URL with multiple path segments."""
    url = client.build_url("desks", "cd:fb:1a:53:fb:e6", "state")
    assert url == "http://test.api/test_key_123/desks/cd:fb:1a:53:fb:e6/state"


def test_build_url_preserves_trailing_slash(client: DeskAPIClient) -> None:
    """Test that trailing slash is preserved for directory endpoints."""
    url = client.build_url("desks/")
    assert url.endswith("/")


@patch("requests.request")
def test_request_success(mock_request: MagicMock, client: DeskAPIClient) -> None:
    """Test successful HTTP request."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = HTTP_OK
    mock_response.text = '{"status": "ok"}'
    mock_request.return_value = mock_response

    response = client.request("GET", "http://test.api/endpoint")

    assert response.status_code == HTTP_OK
    mock_request.assert_called_once()


@patch("requests.request")
def test_request_timeout(mock_request: MagicMock, client: DeskAPIClient) -> None:
    """Test handling of request timeout."""
    mock_request.side_effect = requests.exceptions.Timeout("Timeout")

    with pytest.raises(DeskServiceError, match="Request timeout"):
        client.request("GET", "http://test.api/endpoint")


@patch("requests.request")
def test_request_connection_error(
    mock_request: MagicMock, client: DeskAPIClient
) -> None:
    """Test handling of connection error."""
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(DeskServiceError, match="Failed to connect to desk API"):
        client.request("GET", "http://test.api/endpoint")


@patch("requests.request")
def test_request_http_error_404(mock_request: MagicMock, client: DeskAPIClient) -> None:
    """Test handling of 404 HTTP error."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = HTTP_NOT_FOUND
    mock_response.text = "Not found"
    mock_request.return_value = mock_response

    with pytest.raises(DeskServiceError) as exc_info:
        client.request("GET", "http://test.api/endpoint")

    assert exc_info.value.status_code == HTTP_NOT_FOUND


@patch("requests.request")
def test_request_http_error_500(mock_request: MagicMock, client: DeskAPIClient) -> None:
    """Test handling of 500 HTTP error."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = HTTP_SERVER_ERROR
    mock_response.text = "Internal server error"
    mock_request.return_value = mock_response

    with pytest.raises(DeskServiceError) as exc_info:
        client.request("GET", "http://test.api/endpoint")

    assert exc_info.value.status_code == HTTP_SERVER_ERROR


@patch("requests.request")
def test_request_with_json_payload(
    mock_request: MagicMock, client: DeskAPIClient
) -> None:
    """Test request with JSON payload."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = HTTP_OK
    mock_request.return_value = mock_response

    payload = {"position_mm": 1000}
    client.request("PUT", "http://test.api/endpoint", json=payload)

    call_kwargs = mock_request.call_args.kwargs
    assert call_kwargs["json"] == payload
    assert call_kwargs["headers"]["Content-Type"] == "application/json"


@patch("requests.request")
def test_request_uses_timeout(mock_request: MagicMock, client: DeskAPIClient) -> None:
    """Test that request uses configured timeout."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = HTTP_OK
    mock_request.return_value = mock_response

    client.request("GET", "http://test.api/endpoint")

    call_kwargs = mock_request.call_args.kwargs
    assert call_kwargs["timeout"] == DEFAULT_TIMEOUT
