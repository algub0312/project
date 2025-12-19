"""API routes for desk inventory."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import get_desk_inventory_service
from src.models.dto.desk_inventory_dto import DeskInventoryDTO
from src.models.dto.desk_inventory_update_request import DeskInventoryUpdateRequest
from src.services.desk_inventory_service import DeskInventoryService

MESSAGE = "message"
DESK_NOT_FOUND_MESSAGE = "Desk not found"
DELETED_SUCCESSFULLY = "Desk deleted successfully"

router = APIRouter(prefix="/api/v1/desks", tags=["desks"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_desks(
    service: Annotated[DeskInventoryService, Depends(get_desk_inventory_service)],
) -> list[DeskInventoryDTO]:
    """List all desks in inventory."""
    desks = await service.list_desks()
    return desks


@router.get("/{desk_id}", status_code=status.HTTP_200_OK)
async def get_desk(
    desk_id: int,
    service: Annotated[DeskInventoryService, Depends(get_desk_inventory_service)],
    response: Response,
) -> DeskInventoryDTO | dict[str, str]:
    """Get a specific desk by its ID."""
    desk = await service.get_desk(desk_id)
    if desk is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return desk or {MESSAGE: DESK_NOT_FOUND_MESSAGE}


@router.put("/{desk_id}", status_code=status.HTTP_200_OK)
async def update_desk(
    desk_id: int,
    request: DeskInventoryUpdateRequest,
    service: Annotated[DeskInventoryService, Depends(get_desk_inventory_service)],
    response: Response,
) -> DeskInventoryDTO | dict[str, str]:
    """Update an existing desk."""
    desk = await service.update_desk(desk_id, request)
    if desk is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return desk or {MESSAGE: DESK_NOT_FOUND_MESSAGE}
