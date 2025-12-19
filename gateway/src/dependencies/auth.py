import json
import logging
import os
import time
from typing import Any, Callable

import requests
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from requests import get

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 5

load_dotenv()

KEYCLOAK_ISSUER = os.getenv("KEYCLOAK_ISSUER")
JWKS_URL = os.getenv("JWKS_URL")
AUDIENCE = os.getenv("AUDIENCE")


if KEYCLOAK_ISSUER is None:
    raise RuntimeError("KEYCLOAK_ISSUER environment variable is not set")
if JWKS_URL is None:
    raise RuntimeError("JWKS_URL environment variable is not set")
if AUDIENCE is None:
    raise RuntimeError("BOOKING_SERVICE_URL environment variable is not set")

JWKS_CACHE = {"keys": [], "expires_at": 0.0}
JWKS_TTL = 600  # 10 minutes

bearer_scheme = HTTPBearer()


def get_jwks() -> list:
    """Fetch JWKS from Keycloak with caching."""
    now = time.time()

    # Refresh only when cache expired
    if now >= JWKS_CACHE["expires_at"]:
        logger.info("Refreshing JWKS")
        response = requests.get(JWKS_URL, timeout=REQUEST_TIMEOUT)

        if response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not fetch JWKS from Keycloak",
            )

        JWKS_CACHE["keys"] = response.json().get("keys", [])
        JWKS_CACHE["expires_at"] = now + JWKS_TTL

    return JWKS_CACHE["keys"]


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    """Return the current user."""
    token = token.credentials

    try:
        unverified_header = jwt.get_unverified_header(token)
        jwks = get_jwks()

        # Find the matching public key
        key = next((k for k in jwks if k["kid"] == unverified_header["kid"]), None)
        logger.info("Token kid: %s", unverified_header["kid"])
        logger.info("JWKS kids: %s", [k["kid"] for k in jwks])
        # If no matching key found → refresh once
        if not key:
            logger.info("JWKS mismatch → forcing refresh")
            JWKS_CACHE["expires_at"] = 0
            jwks = get_jwks()
            key = next((k for k in jwks if k["kid"] == unverified_header["kid"]), None)

        if not key:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Public key not found in JWKS"
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=KEYCLOAK_ISSUER,
            options={"verify_at_hash": False},
        )

        logger.info("payload: \n%s", json.dumps(payload, indent=4))
        return payload

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(err)}",
        ) from err


def require_role(role: str) -> Callable[[{get}], dict[str, Any]]:
    """Check if the user has the specified role."""

    def role_checker(
        user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        logger.info("user: %s", user)
        roles = user.get("resource_access", {}).get("vue-app", {}).get("roles", [])
        logger.info("Roles of logged in user: %s", roles)
        if role not in roles:
            logger.info("Access denied for role: %s", role)
            raise HTTPException(status_code=403, detail="Not enough permissions")
        logger.info("Access granted for role: %s", role)
        return user

    return role_checker
