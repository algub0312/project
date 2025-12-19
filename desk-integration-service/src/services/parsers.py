"""Response parsers for desk API data."""

import logging
from typing import Any

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage

logger = logging.getLogger(__name__)


def parse_desk_list(payload: object) -> list[str]:  # Changed from Any to object
    """Parse desk list response.

    Args:
        payload: Raw response payload from the API.

    Returns:
        List of desk MAC addresses.

    Raises:
        ValueError: If payload format is unexpected.

    """
    if isinstance(payload, list):
        desk_ids = [str(item) for item in payload if item]
        logger.info("✓ Found %d desks: %s", len(desk_ids), desk_ids)
        return desk_ids

    logger.error("Unexpected payload format: %s - %s", type(payload), payload)
    raise ValueError("Desk API returned an unexpected response format")


def parse_errors(
    errors_payload: object,
) -> list[DeskError]:  # Changed from Any and List
    """Parse error list from API response.

    Args:
        errors_payload: Raw errors data from the API.

    Returns:
        List of DeskError objects.

    """
    errors: list[DeskError] = []  # Changed from List to list

    if not errors_payload:
        return errors

    if not isinstance(errors_payload, list):
        return errors

    for error in errors_payload:
        if not isinstance(error, dict):
            continue
        time_s = error.get("time_s")
        raw_code = error.get("error_code")
        try:
            error_code = int(raw_code) if raw_code is not None else 0
        except (TypeError, ValueError):
            error_code = 0
        errors.append(DeskError(time_s=time_s, error_code=error_code))

    return errors


def parse_desk(desk_data: dict[str, Any]) -> Desk:  # Changed from Dict to dict
    """Parse full desk data including config, state, and usage.

    Args:
        desk_data: Raw desk data from the API.

    Returns:
        Desk object with all nested data.

    """
    # Extract nested sections
    config_payload = desk_data.get("config", {}) or {}
    state_payload = desk_data.get("state", {}) or {}
    usage_payload = desk_data.get("usage", {}) or {}
    errors_payload = desk_data.get("lastErrors")

    # Parse errors
    last_errors = parse_errors(errors_payload)

    # Build Desk object
    return Desk(
        config=DeskConfig(
            name=config_payload.get("name"),
            manufacturer=config_payload.get("manufacturer"),
        ),
        state=DeskState(
            position_mm=state_payload.get("position_mm"),
            speed_mms=state_payload.get("speed_mms"),
            status=state_payload.get("status"),
            is_position_lost=state_payload.get("isPositionLost"),
            is_overload_protection_up=state_payload.get("isOverloadProtectionUp"),
            is_overload_protection_down=state_payload.get("isOverloadProtectionDown"),
            is_anti_collision=state_payload.get("isAntiCollision"),
        ),
        usage=DeskUsage(
            activations_counter=usage_payload.get("activationsCounter"),
            sit_stand_counter=usage_payload.get("sitStandCounter"),
        ),
        last_errors=last_errors,
    )


def parse_config(
    config_data: dict[str, Any],
) -> DeskConfig:  # Changed from Dict to dict
    """Parse desk configuration data.

    Args:
        config_data: Raw config data from the API.

    Returns:
        DeskConfig object.

    """
    return DeskConfig(
        name=config_data.get("name"),
        manufacturer=config_data.get("manufacturer"),
    )


def parse_state(state_data: dict[str, Any]) -> DeskState:  # Changed from Dict to dict
    """Parse desk state data.

    Args:
        state_data: Raw state data from the API.

    Returns:
        DeskState object.

    """
    return DeskState(
        position_mm=state_data.get("position_mm"),
        speed_mms=state_data.get("speed_mms"),
        status=state_data.get("status"),
        is_position_lost=state_data.get("isPositionLost"),
        is_overload_protection_up=state_data.get("isOverloadProtectionUp"),
        is_overload_protection_down=state_data.get("isOverloadProtectionDown"),
        is_anti_collision=state_data.get("isAntiCollision"),
    )


def parse_usage(usage_data: dict[str, Any]) -> DeskUsage:  # Changed from Dict to dict
    """Parse desk usage data.

    Args:
        usage_data: Raw usage data from the API.

    Returns:
        DeskUsage object.

    """
    return DeskUsage(
        activations_counter=usage_data.get("activationsCounter"),
        sit_stand_counter=usage_data.get("sitStandCounter"),
    )


def parse_state_or_fallback(
    state_data: dict[str, Any],
    position_mm: int,  # Changed from Dict to dict
) -> DeskState:
    """Parse desk state data with fallback values.

    Used when setting desk position and response might be incomplete.

    Args:
        state_data: Raw state data from the API.
        position_mm: Target position as fallback.

    Returns:
        DeskState object with fallback values if needed.

    """
    try:
        return parse_state(state_data)
    except (ValueError, KeyError) as e:
        logger.warning("Failed to parse desk state response: %s", e)
        # Return minimal valid DeskState
        return DeskState(
            position_mm=position_mm,
            speed_mms=0,
            status="unknown",
            is_position_lost=False,
            is_overload_protection_up=False,
            is_overload_protection_down=False,
            is_anti_collision=False,
        )
