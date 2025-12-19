"""HTTP client for making requests to the WiFi2BLE Box Simulator API."""

import logging
from typing import Any

import requests

from .config import HTTP_ERROR_THRESHOLD, DeskServiceConfig
from .exceptions import DeskServiceError

logger = logging.getLogger(__name__)


class DeskAPIClient:
    """HTTP client for interacting with the WiFi2BLE Box Simulator API."""

    def __init__(self, config: DeskServiceConfig) -> None:
        """Initialize the API client.

        Args:
            config: Configuration for the desk service.

        """
        self.config = config

    def build_url(self, *segments: str) -> str:
        """Build URL with API key in path for WiFi2BLE Box Simulator.

        Format: {base_url}/{api_key}/desks/...

        Args:
            segments: URL path segments to append.

        Returns:
            Complete URL string.

        Examples:
            build_url("desks/") -> http://host:8000/api/v2/API_KEY/desks/
            build_url("desks", "cd:fb:1a:53:fb:e6")
                -> http://host:8000/api/v2/API_KEY/desks/cd:fb:1a:53:fb:e6

        """
        # Start with API key, then add segments
        parts: list[str] = [self.config.api_key]
        parts.extend(segment.strip("/") for segment in segments if segment)

        # Join all parts
        path = "/".join(parts)

        # Combine base_url with the path
        url = f"{self.config.base_url}/{path}"

        # Ensure trailing slash for directory endpoints
        if segments and segments[-1].endswith("/"):
            url += "/"

        logger.debug("Built URL: %s", url)
        return url

    def request(
        self,
        method: str,
        url: str,
        **kwargs: dict[str, Any],  # Changed from **kwargs: Any
    ) -> requests.Response:
        """Make HTTP request with proper error handling.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: Full URL to make request to.
            **kwargs: Additional arguments to pass to requests.

        Returns:
            Response object from the API.

        Raises:
            DeskServiceError: If the request fails or returns an error status.

        """
        headers: dict[str, str] = (
            kwargs.pop("headers", {}) or {}
        )  # Also changed Dict to dict
        headers.setdefault("Content-Type", "application/json")

        logger.info("Making %s request to %s", method, url)
        if "json" in kwargs:
            logger.debug("Request payload: %s", kwargs["json"])

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.config.timeout,
                **kwargs,
            )
            logger.info("Response status: %s", response.status_code)
            logger.debug("Response body: %s", response.text)

        except requests.exceptions.Timeout as exc:
            logger.error(
                "Request timeout after %ss for %s: %s",
                self.config.timeout,
                url,
                exc,
            )
            raise DeskServiceError(
                f"Request timeout after {self.config.timeout}s"
            ) from exc

        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error to %s: %s", url, exc)
            raise DeskServiceError(
                "Failed to connect to desk API - check if simulator is running"
            ) from exc

        except requests.RequestException as exc:
            logger.exception("Request failed to %s: %s", url, exc)
            raise DeskServiceError("Failed to communicate with desk API") from exc

        # Check for HTTP errors
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
                f"Desk API responded with HTTP {response.status_code}: {error_text}",
                status_code=response.status_code,
            )

        return response
