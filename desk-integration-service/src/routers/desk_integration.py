import logging
from dataclasses import dataclass

from fastapi import APIRouter, Response, status

from src.models.dto.desk import Desk
from src.models.dto.desk_config import DeskConfig
from src.models.dto.desk_error import DeskError
from src.models.dto.desk_state import DeskState
from src.models.dto.desk_usage import DeskUsage
from src.services.desk_service import DeskService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _DeskServiceConfig:
    """Configuration container for the DeskService."""

    base_url: str
    api_key: str


DESK_NOT_FOUND_MESSAGE = {"detail": "Desk not found"}
desks_service = DeskService()

router = APIRouter(prefix="/api/v1", tags=["desks"])


@router.get("/desks")
def get_desks() -> list[str]:
    """Retrieve the list of all desks."""
    return desks_service.get_all_desks()


@router.get("/desks/{desk_id}")
def get_desk_by_id(desk_id: str, response: Response) -> Desk | None:
    """Retrieve a specific desk by its ID."""
    desk = desks_service.get_desk_by_id(desk_id)
    if desk is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return desk or DESK_NOT_FOUND_MESSAGE


@router.get("/desks/{desk_id}/config")
def get_config(desk_id: str, response: Response) -> DeskConfig:
    """Retrieve the configuration of a specific desk."""
    usage_stats = desks_service.get_desk_config(desk_id)
    if usage_stats is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return usage_stats or DESK_NOT_FOUND_MESSAGE


@router.get("/desks/{desk_id}/state")
def get_state(desk_id: str, response: Response) -> DeskState | None:
    """Retrieve the current state of a specific desk."""
    desk_state = desks_service.get_desk_state(desk_id)
    if desk_state is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return desk_state or DESK_NOT_FOUND_MESSAGE


@router.put("/desks/{desk_id}/state")
def set_desk_height(
    desk_id: str, position_mm: int, response: Response
) -> DeskState | dict[str, str]:
    """Set a desk to a specific height and publish event to RabbitMQ."""
    # Set desk position via WiFi2BLE API
    desk_state = desks_service.set_desk_position(desk_id, position_mm)

    if desk_state is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": "Desk not found"}

    return desk_state


@router.get("/desks/{desk_id}/usage")
def get_usage(desk_id: str, response: Response) -> DeskUsage:  # noqa: E501
    """Retrieve usage data for a specific desk."""
    usage_stats = desks_service.get_desk_usage(desk_id)
    if usage_stats is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return usage_stats or DESK_NOT_FOUND_MESSAGE


@router.get("/desks/{desk_id}/errors")
def get_errors(desk_id: str, response: Response) -> list[DeskError]:
    """Retrieve error logs for a specific desk."""
    errors = desks_service.get_desk_errors(desk_id)
    if errors is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return errors or DESK_NOT_FOUND_MESSAGE
