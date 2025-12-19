from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from main import app
from src.dependencies.auth import get_current_user


def fake_get_current_user() -> dict:
    """Fake current user for testing purposes."""
    return {
        "preferred_username": "test-user",
        "resource_access": {"vue-app": {"roles": ["user"]}},
    }


app.dependency_overrides[get_current_user] = fake_get_current_user


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture to initialize the FastAPI TestClient."""
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
@patch("src.utils.http_client.client.request")
async def test_proxy_get_request(mock_request: AsyncMock, client: TestClient) -> None:
    """Test GET request proxy to the Booking Service."""
    mock_response = AsyncMock()
    mock_response.status_code = status.HTTP_200_OK
    mock_response.content = b'{"message": "Success"}'
    mock_response.headers = {"content-type": "application/json"}
    mock_request.return_value = mock_response

    response = client.get(
        "/booking/some/path?param=value",
        headers={"accept": "application/json", "host": "test-server"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Success"}

    mock_request.assert_called_once_with(
        method="GET",
        url="http://booking-service:8000/some/path?param=value",
        headers=mock_request.call_args[1]["headers"],
        content=b"",
    )


@pytest.mark.asyncio
@patch("src.utils.http_client.client.request")
async def test_proxy_post_request(mock_request: AsyncMock, client: TestClient) -> None:
    """Test POST request proxy to the Booking Service."""
    mock_response = AsyncMock()
    mock_response.status_code = status.HTTP_201_CREATED
    mock_response.content = b'{"message": "Created"}'
    mock_response.headers = {"content-type": "application/json"}

    mock_request.return_value = mock_response

    response = client.post("/booking/some/path", json={"key": "value"})

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Created"}
    mock_request.assert_called_once_with(
        method="POST",
        url="http://booking-service:8000/some/path",
        headers=mock_request.call_args[1]["headers"],
        content=b'{"key":"value"}',
    )


@pytest.mark.asyncio
@patch("src.utils.http_client.client.request")
async def test_proxy_put_request(mock_request: AsyncMock, client: TestClient) -> None:
    """Test PUT request proxy to the Booking Service."""
    mock_response = AsyncMock()
    mock_response.status_code = status.HTTP_200_OK
    mock_response.content = b'{"message": "Updated"}'
    mock_response.headers = {"content-type": "application/json"}

    mock_request.return_value = mock_response

    response = client.put("/booking/some/path", json={"key": "value"})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Updated"}
    mock_request.assert_called_once_with(
        method="PUT",
        url="http://booking-service:8000/some/path",
        headers=mock_request.call_args[1]["headers"],
        content=b'{"key":"value"}',
    )


@pytest.mark.asyncio
@patch("src.utils.http_client.client.request")
async def test_proxy_delete_request(
    mock_request: AsyncMock, client: TestClient
) -> None:
    """Test DELETE request proxy to the Booking Service."""
    mock_response = AsyncMock()
    mock_response.status_code = status.HTTP_204_NO_CONTENT
    mock_response.content = b""
    mock_response.headers = {}

    mock_request.return_value = mock_response

    response = client.delete("/booking/some/path")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    mock_request.assert_called_once_with(
        method="DELETE",
        url="http://booking-service:8000/some/path",
        headers=mock_request.call_args[1]["headers"],
        content=b"",
    )
