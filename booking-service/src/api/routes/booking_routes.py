"""API routes for desk bookings."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from src.api.dependencies import get_booking_service
from src.models.dto.desk_booking_create_request import DeskBookingCreateRequest
from src.models.dto.desk_booking_dto import DeskBookingDTO
from src.models.dto.desk_booking_update_request import DeskBookingUpdateRequest
from src.services.desk_booking_service import DeskBookingService

MESSAGE = "message"
BOOKING_NOT_FOUND_MESSAGE = "Booking not found"
DELETED_SUCCESSFULLY = "Booking deleted successfully"

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_bookings(
    service: Annotated[DeskBookingService, Depends(get_booking_service)],
    response: Response,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[DeskBookingDTO] | dict[str, str]:
    """List all desk bookings. Optionally filter by start and end datetime.

    Args:
        service (DeskBookingService): The desk booking service instance.
        response (Response): The response object to set status codes.
        start (datetime | None): Optional start datetime to filter bookings.
        end (datetime | None): Optional end datetime to filter bookings.

    Returns:
        list[DeskBookingDTO]: A list of desk bookings within the specified range.

    """
    try:
        bookings = await service.list_bookings(start, end)
        return bookings
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {MESSAGE: str(e)}


@router.get("/{booking_id}", status_code=status.HTTP_200_OK)
async def get_booking(
    booking_id: UUID,
    service: Annotated[DeskBookingService, Depends(get_booking_service)],
    response: Response,
) -> DeskBookingDTO | dict[str, str]:
    """Get a specific desk booking by its ID.

    Args:
        booking_id (UUID): The ID of the booking to retrieve.
        service (DeskBookingService): The desk booking service instance.
        response (Response): The response object to set status codes.

    Returns:
        DeskBookingDTO | str: The requested booking data or a not found message.

    """
    booking = await service.get_booking(booking_id)
    if booking is None:
        response.status_code = status.HTTP_404_NOT_FOUND
    return booking or {MESSAGE: BOOKING_NOT_FOUND_MESSAGE}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: DeskBookingCreateRequest,
    service: Annotated[DeskBookingService, Depends(get_booking_service)],
    response: Response,
) -> DeskBookingDTO | dict[str, str]:
    """Create a new desk booking.

    Args:
        request (DeskBookingCreateRequest): The booking creation request data.
        service (DeskBookingService): The desk booking service instance.
        response (Response): The response object to set status codes.

    Returns:
        DeskBookingDTO: The created booking response data.

    """
    try:
        booking = await service.create_booking(request)
        return booking
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {MESSAGE: str(e)}


@router.put("/{booking_id}", status_code=status.HTTP_200_OK)
async def update_booking(
    booking_id: UUID,
    request: DeskBookingUpdateRequest,
    service: Annotated[DeskBookingService, Depends(get_booking_service)],
    response: Response,
) -> DeskBookingDTO | dict[str, str]:
    """Update an existing desk booking.

    Args:
        booking_id (UUID): The ID of the booking to update.
        request (DeskBookingUpdateRequest): The updated booking data.
        service (DeskBookingService): The desk booking service instance.
        response (Response): The response object to set status codes.

    Returns:
        DeskBookingDTO | str: The updated booking data or a not found message.

    """
    try:
        booking = await service.update_booking(booking_id, request)
        if booking is None:
            response.status_code = status.HTTP_404_NOT_FOUND
        return booking or {MESSAGE: BOOKING_NOT_FOUND_MESSAGE}
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {MESSAGE: str(e)}


@router.delete("/{booking_id}", status_code=status.HTTP_200_OK)
async def delete_booking(
    booking_id: UUID,
    service: Annotated[DeskBookingService, Depends(get_booking_service)],
    response: Response,
) -> dict[str, str]:
    """Delete an existing desk booking.

    Args:
        booking_id (UUID): The ID of the booking to delete.
        service (DeskBookingService): The desk booking service instance.
        response (Response): The response object to set status codes.

    """
    success = await service.delete_booking(booking_id)
    if not success:
        response.status_code = status.HTTP_404_NOT_FOUND
    return (
        {MESSAGE: DELETED_SUCCESSFULLY}
        if success
        else {MESSAGE: BOOKING_NOT_FOUND_MESSAGE}
    )
