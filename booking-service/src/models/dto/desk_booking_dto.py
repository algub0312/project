from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.models.db.desk_booking import DeskBooking


class DeskBookingDTO(BaseModel):
    """DTO for desk booking.

    Attributes:
        id (UUID): Unique identifier for the desk booking.
        user_id (UUID): Identifier of the user who made the booking.
        desk_id (int): Identifier of the desk being booked.
        start_time (datetime): Start date and time of the booking.
        end_time (datetime): End date and time of the booking.

    """

    id: UUID
    user_id: UUID
    desk_id: int
    start_time: datetime
    end_time: datetime

    @classmethod
    def from_entity(cls, entity: DeskBooking) -> "DeskBookingDTO":
        """Create a DeskBookingDTO from a DeskBooking entity.

        Args:
            entity: The DeskBooking entity.

        Returns:
            DeskBookingDTO: The created DTO instance.

        """
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            desk_id=entity.desk_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
        )
