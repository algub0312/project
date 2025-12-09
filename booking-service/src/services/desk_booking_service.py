import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from src.messaging.messaging_manager import MessagingManager
from src.messaging.pubsub_exchanges import (
    DESK_BOOKING_CREATED,
    DESK_BOOKING_DELETED,
    DESK_BOOKING_UPDATED,
)
from src.models.db.desk_booking import DeskBooking
from src.models.dto.desk_booking_create_request import DeskBookingCreateRequest
from src.models.dto.desk_booking_dto import DeskBookingDTO
from src.models.dto.desk_booking_update_request import DeskBookingUpdateRequest
from src.models.msg.booking_message import BookingMessage
from src.repositories.booking_repository import DeskBookingRepository
from src.services.transformations.date import normalize_to_utc

TOLERANCE_IN_MINUTES = 10

logger = logging.getLogger(__name__)


class DeskBookingService:
    """Service for managing desk bookings."""

    def __init__(
        self,
        repo: DeskBookingRepository,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the DeskBookingService.

        Args:
            repo (DeskBookingRepository): The repository for desk bookings.
            messaging (MessagingManager): The messaging manager for handling messages.

        """
        self._repo = repo
        self._messaging = messaging

    async def create_booking(self, request: DeskBookingCreateRequest) -> DeskBookingDTO:
        """Create a new desk booking.

        Args:
            request (DeskBookingCreateRequest): The request DTO containing booking details.

        Returns:
            DeskBookingDTO: The response DTO containing created booking details.

        """  # noqa: E501
        request.start_time, request.end_time = (
            DeskBookingService._normalize_booking_times_to_utc(
                request.start_time, request.end_time
            )
        )
        if self._repo.has_overlapping_booking(
            request.desk_id,
            request.start_time,
            request.end_time,
            timedelta(minutes=TOLERANCE_IN_MINUTES),
        ):
            raise ValueError(
                "Selected desk is already booked for the requested time range."
            )
        booking = self._repo.create(DeskBooking.from_create_dto(request))
        self._publish_message(booking, DESK_BOOKING_CREATED)
        return DeskBookingDTO.from_entity(booking)

    async def list_bookings(
        self, start: datetime, end: datetime
    ) -> list[DeskBookingDTO]:
        """List all desk bookings.

        Args:
            start (datetime): Start datetime to filter bookings.
            end (datetime): End datetime to filter bookings.

        Returns:
            list[DeskBookingDTO]: A list of all desk bookings.

        """
        if start is None and end is None:
            bookings = self._repo.get_all()
            return [DeskBookingDTO.from_entity(booking) for booking in bookings]
        start = datetime.min if start is None else start
        end = datetime.max if end is None else end
        if start >= end:
            raise ValueError("Start datetime must be before end datetime.")
        start, end = DeskBookingService._normalize_booking_times_to_utc(start, end)
        bookings = self._repo.get_bookings_in_time_range(start, end)
        return [DeskBookingDTO.from_entity(booking) for booking in bookings]

    async def get_booking(self, booking_id: UUID) -> DeskBookingDTO | None:
        """Get a specific desk booking by its ID.

        Args:
            booking_id (UUID): The ID of the booking to retrieve.

        Returns:
            DeskBookingDTO: The requested booking data.

        """
        booking = self._repo.get_by_id(booking_id)
        return DeskBookingDTO.from_entity(booking) if booking else None

    async def update_booking(
        self, booking_id: UUID, request: DeskBookingUpdateRequest
    ) -> DeskBookingDTO | None:
        """Update an existing desk booking.

        Args:
            booking_id (UUID): The ID of the booking to update.
            request (DeskBookingDTO): The DTO containing updated booking details.

        Returns:
            DeskBookingDTO: The updated booking data.

        """
        booking = self._repo.get_by_id(booking_id)
        if booking is None:
            return None
        if self._repo.has_overlapping_booking(
            request.desk_id, request.start_time, request.end_time
        ):
            raise ValueError(
                "Selected desk is already booked for the requested time range."
            )

        request.start_time, request.end_time = (
            DeskBookingService._normalize_booking_times_to_utc(
                request.start_time, request.end_time
            )
        )
        updated_booking = self._repo.update(
            DeskBooking.from_update_dto(booking.id, request)
        )
        self._publish_message(updated_booking, DESK_BOOKING_UPDATED)
        return DeskBookingDTO.from_entity(updated_booking)

    async def delete_booking(self, booking_id: UUID) -> bool:
        """Delete a desk booking by its ID.

        Args:
            booking_id (UUID): The ID of the booking to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """
        booking = self._repo.delete(booking_id)
        if booking is not None:
            self._publish_message(booking, DESK_BOOKING_DELETED)
        return booking is not None

    def _publish_message(self, booking: DeskBooking, exchange: str) -> None:
        """Publish a booking message to the specified exchange asynchronously.

        Args:
            booking (DeskBooking): The booking entity to publish.
            exchange (str): The exchange to publish the message to.

        """
        task = asyncio.create_task(
            self._messaging.get_pubsub(exchange).publish(
                BookingMessage.from_entity(booking)
            )
        )
        task.add_done_callback(DeskBookingService._log_task_exception)

    @staticmethod
    def _log_task_exception(task: asyncio.Task) -> None:
        """Log exceptions from an asyncio Task."""
        try:
            task.result()
        except Exception as e:
            logger.exception("Background publish failed: %s", e)

    @staticmethod
    def _normalize_booking_times_to_utc(
        start: datetime, end: datetime
    ) -> tuple[datetime, datetime]:
        """Normalize booking start and end times to UTC.

        Args:
            start (datetime): The start datetime of the booking.
            end (datetime): The end datetime of the booking.

        Returns:
            tuple[datetime, datetime]: The normalized start and end datetimes.

        """
        return normalize_to_utc(start), normalize_to_utc(end)
