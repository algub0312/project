"""Service for interacting with the WiFi2BLE Box Simulator API."""

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _load_timeout() -> int:
    """Load timeout from environment with fallback.

    Falls back to 10 seconds if the env var is missing or invalid.
    """
    raw = os.getenv("DESK_API_TIMEOUT_SECONDS", "10")
    try:
        return int(raw)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid DESK_API_TIMEOUT_SECONDS value '%s'; falling back to 10 seconds",
            raw,
        )
        return 10


DEFAULT_TIMEOUT = _load_timeout()
HTTP_ERROR_THRESHOLD = 400  # First HTTP error status code (4xx/5xx)


class DeskServiceError(RuntimeError):
    """Base exception raised for desk service errors."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class _DeskServiceConfig:
    """Configuration container for the DeskService."""

    base_url: str
    api_key: str

    @classmethod
    def from_env(cls) -> "_DeskServiceConfig":
        """Load configuration from environment variables."""
        base = os.getenv("DESK_API_BASE_URL", "http://localhost:8000/api/v2").rstrip(
            "/"
        )
        api_key = os.getenv("DESK_API_KEY", "")

        if not api_key:
            logger.error("DESK_API_KEY environment variable is not set!")
            raise ValueError("DESK_API_KEY is required")

        logger.info(
            "DeskService initialized: base_url=%s, api_key=%s...",
            base,
            api_key[:8],
        )
        return cls(base_url=base, api_key=api_key)


class DeskService:
    """Service for interacting with the WiFi2BLE Box Simulator API."""

    _config = _DeskServiceConfig.from_env()

    @classmethod
    def _build_url(cls, *segments: str) -> str:
        """Build URL with API key in path for WiFi2BLE Box Simulator.

        Format: {base_url}/{api_key}/desks/...

        The requests library automatically handles URL encoding, so we don't need
        to encode manually.

        Examples:
            _build_url("desks/") -> http://localhost:8000/api/v2/API_KEY/desks/
            _build_url("desks", "cd:fb:1a:53:fb:e6")
                -> http://localhost:8000/api/v2/API_KEY/desks/cd:fb:1a:53:fb:e6

        """
        parts: List[str] = [cls._config.base_url, cls._config.api_key]
        parts.extend(segment.strip("/") for segment in segments if segment)
        url = "/".join(parts)

        # Ensure trailing slash for directory endpoints
        if segments and segments[-1].endswith("/"):
            url += "/"

        logger.debug("Built URL: %s", url)
        return url

    @classmethod
    def _request(
        cls,
        method: str,
        url: str,
        **kwargs: dict[str, object],
    ) -> requests.Response:
        """Make HTTP request with proper error handling."""
        headers: Dict[str, str] = kwargs.pop("headers", {}) or {}  # type: ignore[assignment]
        headers.setdefault("Content-Type", "application/json")

        logger.info("Making %s request to %s", method, url)
        if "json" in kwargs:
            logger.debug("Request payload: %s", kwargs["json"])

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
                **kwargs,  # type: ignore[arg-type]
            )
            logger.info("Response status: %s", response.status_code)

        except requests.exceptions.Timeout as exc:
            logger.error(
                "Request timeout after %ss for %s: %s", DEFAULT_TIMEOUT, url, exc
            )
            raise DeskServiceError(
                "Request timeout after %ss" % DEFAULT_TIMEOUT
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error to %s: %s", url, exc)
            raise DeskServiceError(
                "Failed to connect to desk API - check if simulator is running"
            ) from exc

        except requests.RequestException as exc:
            logger.exception("Request failed to %s: %s", url, exc)
            raise DeskServiceError("Failed to communicate with desk API") from exc

        if response.status_code >= HTTP_ERROR_THRESHOLD:
            error_text = response.text[:500] if response.text else "No error message"
            logger.error(
                "Desk API error %s for %s %s: %s",
                response.status_code,
                method,
                url,
                error_text,
            )
            raise DeskServiceError(
                "Desk API responded with HTTP %s: %s"
                % (response.status_code, error_text),
                status_code=response.status_code,
            )

        return response

    @classmethod
    def get_all_desks(cls) -> List[str]:
        """Fetch all desk identifiers from the desk API.

        Returns:
            List of MAC addresses like ["cd:fb:1a:53:fb:e6", ...]

        Raises:
            DeskServiceError: If the API request fails

        """
        logger.info("Fetching all desks from API")

        # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/
        url = cls._build_url("desks/")
        response = cls._request("GET", url)

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Failed to parse JSON response: %s", exc)
            raise DeskServiceError("Invalid JSON response from desk API") from exc

        # WiFi2BLE returns a simple list of MAC addresses (strings)
        if isinstance(payload, list):
            desk_ids = [str(item) for item in payload if item]
            logger.info("✓ Found %d desks: %s", len(desk_ids), desk_ids)
            return desk_ids

        logger.error("Unexpected payload format: %s - %s", type(payload), payload)
        raise DeskServiceError("Desk API returned an unexpected response format")

    @classmethod
    def get_desk_state(cls, desk_id: str) -> Optional[Dict[str, object]]:
        """Get the current state of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")

        Returns:
            Dict with 'config', 'state', 'usage', 'lastErrors' keys,
            or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk state without an identifier")
            return None

        try:
            # WiFi2BLE API endpoint: GET /api/v2/{api_key}/desks/{desk_id}
            url = cls._build_url("desks", desk_id)
            response = cls._request("GET", url)
            state = response.json()

            logger.debug(
                "Desk %s state: position=%smm",
                desk_id,
                (state.get("state", {}) or {}).get("position_mm"),
            )
            return state

        except DeskServiceError as exc:
            logger.warning("Failed to get state for desk %s: %s", desk_id, exc)
            return None

    @classmethod
    def set_desk_position(cls, desk_id: str, position_mm: int) -> Dict[str, object]:
        """Set a specific desk to a target position.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6")
            position_mm: Target position in millimeters

        Returns:
            API response dict

        Raises:
            DeskServiceError: If the operation fails

        """
        if not desk_id:
            raise DeskServiceError("Desk identifier is required")

        if not isinstance(position_mm, int) or position_mm < 0:
            raise DeskServiceError(
                "Invalid position: %smm (must be positive integer)" % position_mm
            )

        logger.info("Setting desk %s to position %smm", desk_id, position_mm)

        # WiFi2BLE API endpoint: PUT /api/v2/{api_key}/desks/{desk_id}/state
        payload = {"position_mm": position_mm}
        url = cls._build_url("desks", desk_id, "state")

        response = cls._request("PUT", url, json=payload)
        logger.info("✓ Successfully commanded desk %s to %smm", desk_id, position_mm)

        try:
            return response.json()  # type: ignore[return-value]
        except ValueError:
            return {"success": True, "position_mm": position_mm}

    @classmethod
    def raise_all_desks(
        cls,
        position_mm: int,
        *,
        context: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """Raise all desks to the specified height and broadcast the outcome.

        Args:
            position_mm: Target position in millimeters
            context: Optional context dict for logging/events

        Returns:
            List of results for each desk

        """
        return cls._move_all_desks("raise", position_mm, context=context)

    @classmethod
    def lower_all_desks(
        cls,
        position_mm: int,
        *,
        context: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """Lower all desks to the specified height and broadcast the outcome.

        Args:
            position_mm: Target position in millimeters
            context: Optional context dict for logging/events

        Returns:
            List of results for each desk

        """
        return cls._move_all_desks("lower", position_mm, context=context)

    @classmethod
    def _move_all_desks(
        cls,
        action: str,
        position_mm: int,
        *,
        context: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        """Move all desks to a specified position."""
        logger.info("=" * 60)
        logger.info(
            "Starting %s operation for all desks to %smm", action.upper(), position_mm
        )
        logger.info("=" * 60)

        try:
            desk_ids = cls.get_all_desks()
        except DeskServiceError as exc:
            logger.error("Failed to get desk list: %s", exc)
            return []

        logger.info("Found %d desks to %s", len(desk_ids), action)

        results: List[Dict[str, object]] = []

        for i, desk_id in enumerate(desk_ids, 1):
            logger.info("[%d/%d] Processing desk %s", i, len(desk_ids), desk_id)

            try:
                cls.set_desk_position(desk_id, position_mm)
                success = True
                logger.info("  ✓ Successfully commanded desk %s", desk_id)

            except DeskServiceError as exc:
                logger.error("  ✗ Failed to move desk %s: %s", desk_id, exc)
                success = False

            results.append(
                {
                    "desk_id": desk_id,
                    "success": success,
                    "position_mm": position_mm,
                }
            )

        successful = sum(1 for r in results if r["success"])
        logger.info("=" * 60)
        logger.info(
            "%s complete: %d/%d desks successful",
            action.upper(),
            successful,
            len(results),
        )
        logger.info("=" * 60)

        cls._publish_rabbitmq_event(
            action=action,
            position_mm=position_mm,
            results=results,
            context=context,
        )

        return results

    @staticmethod
    def _publish_rabbitmq_event(
        *,
        action: str,
        position_mm: int,
        results: List[Dict[str, object]],
        context: Optional[Dict[str, object]],
    ) -> None:
        """Publish desk action event to RabbitMQ."""
        successful = sum(1 for r in results if r["success"])

        payload: Dict[str, object] = {
            "action": action,
            "position_mm": position_mm,
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "total_desks": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results,
        }

        if context:
            payload["context"] = context
