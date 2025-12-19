"""Service for interacting with the WiFi2BLE Box Simulator API."""

import logging
from typing import List, Optional

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage

from .config import DeskServiceConfig
from .exceptions import DeskServiceError
from .http_client import DeskAPIClient
from .parsers import (
    parse_config,
    parse_desk,
    parse_desk_list,
    parse_errors,
    parse_state,
    parse_state_or_fallback,
    parse_usage,
)

logger = logging.getLogger(__name__)


class DeskService:
    """Service for interacting with the WiFi2BLE Box Simulator API."""

    def __init__(self, config: Optional[DeskServiceConfig] = None) -> None:
        """Initialize the DeskService.

        Args:
            config: Optional configuration. If not provided, loads from environment.

        """
        self.config = config or DeskServiceConfig.from_env()
        logger.info("DeskServiceConfig: base_url=%s", self.config.base_url)
        self.client = DeskAPIClient(self.config)

    def get_all_desks(self) -> list[str]:
        """Fetch all desk identifiers from the desk API.

        Returns:
            List of MAC addresses like ["cd:fb:1a:53:fb:e6", ...].

        Raises:
            DeskServiceError: If the API request fails.

        """
        logger.info("Fetching all desks from API")

        url = self.client.build_url("desks/")
        response = self.client.request("GET", url)

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Failed to parse JSON response: %s", exc)
            raise DeskServiceError("Invalid JSON response from desk API") from exc

        return parse_desk_list(payload)

    def get_desk_by_id(self, desk_id: str) -> Optional[Desk]:
        """Get the data of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").

        Returns:
            Desk object, or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk without an identifier")
            return None

        try:
            url = self.client.build_url("desks", desk_id)
            response = self.client.request("GET", url)
            desk_data = response.json()

            if not isinstance(desk_data, dict):
                logger.error("Expected dict response, got: %s", type(desk_data))
                return None

            return parse_desk(desk_data)

        except DeskServiceError as exc:
            logger.warning("Failed to get data of desk %s: %s", desk_id, exc)
            return None
        except Exception as exc:
            logger.exception("Unexpected error fetching desk %s: %s", desk_id, exc)
            return None

    def get_desk_config(self, desk_id: str) -> Optional[DeskConfig]:
        """Get the current configuration of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").

        Returns:
            DeskConfig object, or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk config without an identifier")
            return None

        try:
            url = self.client.build_url("desks", desk_id, "config")
            response = self.client.request("GET", url)
            config_data = response.json()
            return parse_config(config_data)

        except DeskServiceError as exc:
            logger.warning("Failed to get configuration for desk %s: %s", desk_id, exc)
            return None

    def get_desk_state(self, desk_id: str) -> Optional[DeskState]:
        """Get the current state of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").

        Returns:
            DeskState object, or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk state without an identifier")
            return None

        try:
            url = self.client.build_url("desks", desk_id, "state")
            response = self.client.request("GET", url)
            state_data = response.json()
            return parse_state(state_data)

        except DeskServiceError as exc:
            logger.warning("Failed to get state for desk %s: %s", desk_id, exc)
            return None

    def get_desk_usage(self, desk_id: str) -> Optional[DeskUsage]:
        """Get the usage data of a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").

        Returns:
            DeskUsage object, or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk usage without an identifier")
            return None

        try:
            url = self.client.build_url("desks", desk_id, "usage")
            response = self.client.request("GET", url)
            usage_data = response.json()
            return parse_usage(usage_data)

        except DeskServiceError as exc:
            logger.warning("Failed to get usage for desk %s: %s", desk_id, exc)
            return None

    def get_desk_errors(self, desk_id: str) -> Optional[List[DeskError]]:
        """Get the list of errors for a specific desk.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").

        Returns:
            List of DeskError objects, or None if failed.

        """
        if not desk_id:
            logger.warning("Attempted to fetch desk errors without an identifier")
            return None

        try:
            url = self.client.build_url("desks", desk_id)
            response = self.client.request("GET", url)
            payload = response.json()

            errors_payload = (
                payload.get("lastErrors") if isinstance(payload, dict) else None
            )
            return parse_errors(errors_payload)

        except DeskServiceError as exc:
            logger.warning("Failed to get errors for desk %s: %s", desk_id, exc)
            return None
        except Exception as exc:
            logger.exception(
                "Unexpected error fetching errors for desk %s: %s", desk_id, exc
            )
            return None

    def set_desk_position(self, desk_id: str, position_mm: int) -> Optional[DeskState]:
        """Set a specific desk to a target position.

        Args:
            desk_id: MAC address of the desk (e.g., "cd:fb:1a:53:fb:e6").
            position_mm: Target position in millimeters.

        Returns:
            DeskState object with the new desk state, or None if failed.

        Raises:
            DeskServiceError: If the operation fails due to invalid input.

        """
        if not desk_id:
            raise DeskServiceError("Desk identifier is required")

        if not isinstance(position_mm, int) or position_mm < 0:
            raise DeskServiceError(
                f"Invalid position: {position_mm}mm (must be positive integer)"
            )

        logger.info("Setting desk %s to position %smm", desk_id, position_mm)

        payload = {"position_mm": position_mm}
        url = self.client.build_url("desks", desk_id, "state")

        response = self.client.request("PUT", url, json=payload)
        logger.info("✓ Successfully commanded desk %s to %smm", desk_id, position_mm)

        # Parse response with fallback
        state_data = response.json()
        return parse_state_or_fallback(state_data, position_mm)
