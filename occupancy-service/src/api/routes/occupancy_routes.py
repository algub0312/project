"""API routes for occupancy tracking."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from src.api.dependencies import get_db_session, get_occupancy_service
from src.models.dto.current_occupancy_response import CurrentOccupancyResponse
from src.models.dto.occupancy_response import OccupancyResponse
from src.services.occupancy_service import OccupancyService

router = APIRouter(prefix="/api/v1/occupancy", tags=["occupancy"])


@router.get("/{desk_id}")
async def get_current_occupancy(
    desk_id: str,
    service: Annotated[OccupancyService, Depends(get_occupancy_service)],
) -> CurrentOccupancyResponse:
    """Get current occupancy status for a specific desk.

    Args:
        desk_id (str): The desk identifier.
        service (OccupancyService): The occupancy service instance.

    Returns:
        CurrentOccupancyResponse: The current occupancy status.

    """
    occupancy = service.get_current_occupancy(desk_id)
    if not occupancy:
        raise HTTPException(
            status_code=404, detail=f"No occupancy data found for desk {desk_id}"
        )
    return occupancy


@router.get("/")
async def get_all_current_occupancy(
    service: Annotated[OccupancyService, Depends(get_occupancy_service)],
) -> list[CurrentOccupancyResponse]:
    """Get current occupancy status for all desks.

    Args:
        service (OccupancyService): The occupancy service instance.

    Returns:
        list[CurrentOccupancyResponse]: A list of current occupancy statuses.

    """
    return service.get_all_current_occupancy()


@router.get("/{desk_id}/history")
async def get_occupancy_history(
    desk_id: str,
    service: Annotated[OccupancyService, Depends(get_occupancy_service)],
    limit: Annotated[
        int, Query(ge=1, le=1000, description="Number of records to return")
    ] = 100,
    start_date: Annotated[
        datetime | None, Query(description="Start date for filtering (ISO format)")
    ] = None,
    end_date: Annotated[
        datetime | None, Query(description="End date for filtering (ISO format)")
    ] = None,
) -> list[OccupancyResponse]:
    """Get occupancy history for a specific desk.

    Args:
        desk_id: The desk identifier.
        limit: Maximum number of records to return (1-1000, default: 100).
        service: The occupancy service instance.
        start_date: Optional start date for filtering results.
        end_date: Optional end date for filtering results.

    Returns:
        list[OccupancyResponse]: Historical occupancy data.

    """
    return service.get_occupancy_history(
        desk_id=desk_id, limit=limit, start_date=start_date, end_date=end_date
    )


@router.delete("/dev/")
def clear_all_occupancy() -> dict[str, str]:
    """Clear all occupancy records for testing."""
    with next(get_db_session()) as session:
        session.exec(text("DELETE FROM occupancyrecord"))
        session.commit()
        return {"message": "All records deleted"}
