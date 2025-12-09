from datetime import datetime, timedelta
from uuid import UUID

from sqlmodel import Session, select

from src.models.db.desk_booking import DeskBooking


class DeskBookingRepository:
    """Repository for managing DeskBooking entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create(self, booking: DeskBooking) -> DeskBooking:
        """Create a new DeskBooking in the database.

        Args:
            booking (DeskBooking): The DeskBooking entity to create.

        Returns:
            DeskBooking: The created DeskBooking entity with updated fields.

        """
        self._save_and_refresh(booking)
        return booking

    def get_all(self) -> list[DeskBooking]:
        """Retrieve all DeskBooking entities from the database.

        Returns:
            list[DeskBooking]: A list of DeskBooking entities.

        """
        return list(self._session.exec(select(DeskBooking)))

    def get_by_id(self, booking_id: UUID) -> DeskBooking | None:
        """Retrieve a DeskBooking by its ID.

        Args:
            booking_id (UUID): The ID of the DeskBooking to retrieve.

        Returns:
            DeskBooking | None: The DeskBooking entity if found, else None.

        """
        return self._session.get(DeskBooking, booking_id)

    def get_bookings_in_time_range(
        self, start: datetime, end: datetime
    ) -> list[DeskBooking]:
        """Retrieve all DeskBooking entities from the database.

        Args:
            start (datetime): The start datetime to filter bookings.
            end (datetime): The end datetime to filter bookings.

        Returns:
            list[DeskBooking]: A list of DeskBooking entities.

        """
        return list(
            self._session.exec(
                select(DeskBooking).where(
                    DeskBooking.start_time < end,
                    DeskBooking.end_time > start,
                )
            )
        )

    def update(self, booking: DeskBooking) -> DeskBooking | None:
        """Update an existing DeskBooking in the database.

        Args:
            booking (DeskBooking): The DeskBooking entity to update.

        Returns:
            DeskBooking: The updated DeskBooking entity.

        """
        update_booking = self._update_fields(booking)
        if update_booking is None:
            return None
        self._save_and_refresh(update_booking)
        return booking

    def delete(self, booking_id: UUID) -> DeskBooking | None:
        """Delete a DeskBooking by its ID.

        Args:
            booking_id (UUID): The ID of the DeskBooking to delete.

        Returns:
            DeskBooking: The deleted DeskBooking entity.

        """
        booking = self.get_by_id(booking_id)
        if booking is None:
            return None
        booking_copy = DeskBooking.model_copy(
            booking
        )  # Detached copy to return after deletion
        self._session.delete(booking)
        self._session.commit()
        return booking_copy

    def has_overlapping_booking(
        self,
        desk_id: int,
        start_time: datetime,
        end_time: datetime,
        tolerance: timedelta = timedelta(0),
    ) -> bool:
        """Return True if there is any booking for `desk_id` that overlaps the given time window.

        An additional `tolerance` may be provided (a timedelta). The new booking's time window
        is expanded by the tolerance (start_time - tolerance, end_time + tolerance), so any
        existing booking within that expanded window is considered overlapping.

        Overlap condition used: existing.start_time < (end_time + tolerance)
                               and existing.end_time > (start_time - tolerance)

        Args:
            desk_id (UUID): The ID of the desk to check for overlapping bookings.
            start_time (datetime): The start time of the new booking.
            end_time (datetime): The end time of the new booking.
            tolerance (timedelta): Additional margin to treat near-touching bookings as overlapping.

        Returns:
            bool: True if there is an overlapping booking, False otherwise.

        Raises:
            ValueError: If end_time is not after start_time or tolerance is negative.

        """  # noqa: E501
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        if tolerance < timedelta(0):
            raise ValueError("tolerance must be non-negative")

        adjusted_start = start_time - tolerance
        adjusted_end = end_time + tolerance

        stmt = select(DeskBooking).where(
            DeskBooking.desk_id == desk_id,
            DeskBooking.start_time < adjusted_end,
            DeskBooking.end_time > adjusted_start,
        )
        result = self._session.exec(stmt).first()
        return result is not None

    def _save_and_refresh(self, instance: DeskBooking) -> None:
        """Save and refresh an instance in the database.

        Args:
            instance (DeskBooking): The DeskBooking instance to save and refresh.

        """
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)

    def _update_fields(self, updated_booking: DeskBooking) -> DeskBooking | None:
        """Update fields of an existing DeskBooking.

        Args:
            updated_booking (DeskBooking): The DeskBooking entity with updated fields.

        Returns:
            DeskBooking | None: The updated DeskBooking entity or None if not found.

        """
        current_booking = self.get_by_id(updated_booking.id)
        if current_booking is None:
            return None
        current_booking.user_id = updated_booking.user_id
        current_booking.desk_id = updated_booking.desk_id
        current_booking.start_time = updated_booking.start_time
        current_booking.end_time = updated_booking.end_time
        return current_booking
