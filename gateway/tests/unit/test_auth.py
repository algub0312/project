from typing import Annotated, Any, Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI, status
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from src.dependencies.auth import (
    JWKS_CACHE,
    get_current_user,
    require_role,
)

app = FastAPI()


@app.get("/protected", dependencies=[Depends(require_role("admin"))])
def protected_route(user: Annotated[dict, Depends(get_current_user)]) -> dict:
    """Set protected route that requires 'admin' role."""
    return {"ok": True, "user": user["preferred_username"]}


client = TestClient(app)


@pytest.fixture
def fake_jwks_key() -> dict:
    """Return fixture to provide a fake JWKS key for testing."""
    return {
        "kid": "test-kid",
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "n": "abc123",
        "e": "AQAB",
    }


@pytest.fixture
def reset_jwks_cache() -> Generator[Any, None, None]:
    """Return fixture to reset JWKS cache before and after each test."""
    JWKS_CACHE["keys"] = []
    JWKS_CACHE["expires_at"] = 0
    yield
    JWKS_CACHE["keys"] = []
    JWKS_CACHE["expires_at"] = 0


def test_get_current_user_success(
    fake_jwks_key: dict, reset_jwks_cache: Generator[Any, None, None]
) -> None:
    """Test successful retrieval of current user from token."""
    token = "dummy.jwt.value"  # noqa: S105

    with patch("src.dependencies.auth.jwt.get_unverified_header") as hdr_mock:
        hdr_mock.return_value = {"kid": "test-kid"}

        with patch("src.dependencies.auth.jwt.decode") as decode_mock:
            decode_mock.return_value = {
                "preferred_username": "alice",
                "resource_access": {"vue-app": {"roles": ["admin"]}},
            }

            with patch("src.dependencies.auth.requests.get") as req_mock:
                mock_resp = MagicMock()
                mock_resp.status_code = status.HTTP_200_OK
                mock_resp.json.return_value = {"keys": [fake_jwks_key]}
                req_mock.return_value = mock_resp

                # Simulate FastAPI dependency
                user = get_current_user(token=MagicMock(credentials=token))

                assert user["preferred_username"] == "alice"
                assert user["resource_access"]["vue-app"]["roles"] == ["admin"]
                decode_mock.assert_called_once()


def test_get_current_user_jwks_key_missing(
    reset_jwks_cache: Generator[Any, None, None],
) -> None:
    """Test behavior when JWKS key is missing."""
    token = "dummy.jwt.value"  # noqa: S105

    with patch("src.dependencies.auth.jwt.get_unverified_header") as hdr_mock:
        hdr_mock.return_value = {"kid": "nonexistent"}

        with patch("src.dependencies.auth.requests.get") as req_mock:
            mock_resp = MagicMock()
            mock_resp.status_code = status.HTTP_200_OK
            mock_resp.json.return_value = {"keys": []}
            req_mock.return_value = mock_resp

            with pytest.raises(HTTPException) as exc:
                get_current_user(token=MagicMock(credentials=token))

            assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Public key not found" in exc.value.detail


def test_get_current_user_invalid_token(
    fake_jwks_key: dict, reset_jwks_cache: Generator[Any, None, None]
) -> None:
    """Test behavior with an invalid token."""
    token = "invalid.jwt"  # noqa: S105

    with patch("src.dependencies.auth.jwt.get_unverified_header") as hdr_mock:
        hdr_mock.return_value = {"kid": "test-kid"}

        with patch("src.dependencies.auth.jwt.decode") as decode_mock:
            decode_mock.side_effect = Exception("broken token")

            with patch("src.dependencies.auth.requests.get") as req_mock:
                mock_resp = MagicMock()
                mock_resp.status_code = status.HTTP_200_OK
                mock_resp.json.return_value = {"keys": [fake_jwks_key]}
                req_mock.return_value = mock_resp

                with pytest.raises(HTTPException) as exc:
                    get_current_user(token=MagicMock(credentials=token))

                assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Invalid or expired token" in exc.value.detail


def test_require_role_allows_access(
    reset_jwks_cache: Generator[Any, None, None], fake_jwks_key: dict
) -> None:
    """Test /protected has require_role("admin") — should allow access."""

    def fake_get_current_user() -> dict:
        """Fake current user with admin role."""
        return {
            "preferred_username": "alice",
            "resource_access": {"vue-app": {"roles": ["admin"]}},
        }

    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.get("/protected", headers={"Authorization": "Bearer x"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["ok"] is True
        assert response.json()["user"] == "alice"
    finally:
        # cleanup override
        app.dependency_overrides.pop(get_current_user, None)


def test_require_role_denies_access(
    reset_jwks_cache: Generator[Any, None, None], fake_jwks_key: dict
) -> None:
    """Test user lacks admin → should be 403."""

    def fake_get_current_user() -> dict:
        """Fake current user without user role."""
        return {
            "preferred_username": "bob",
            "resource_access": {"vue-app": {"roles": ["user"]}},
        }

    app.dependency_overrides[get_current_user] = fake_get_current_user

    try:
        response = client.get("/protected", headers={"Authorization": "Bearer x"})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Not enough permissions"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
