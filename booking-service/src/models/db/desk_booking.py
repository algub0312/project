from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from src.models.dto.desk_booking_create_request import DeskBookingCreateRequest
from src.models.dto.desk_booking_update_request import DeskBookingUpdateRequest


class DeskBooking(SQLModel, table=True):
    """Database model for a desk booking.

    Attributes:
        id (UUID): Unique identifier for the desk booking.
        user_id (UUID): Identifier of the user who made the booking.
        desk_id (int): Identifier of the desk being booked.
        start_time (datetime): Start date and time of the booking.
        end_time (datetime): End date and time of the booking.

    """

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID
    desk_id: int
    start_time: datetime
    end_time: datetime

    @classmethod
    def from_create_dto(cls, dto: DeskBookingCreateRequest) -> "DeskBooking":
        """Create a DeskBooking instance from a DeskBookingCreateRequest DTO.

        Args:
            dto (DeskBookingCreateRequest): The DTO containing booking details.

        Returns:
            DeskBooking: The created DeskBooking instance.

        """
        return cls(
            user_id=dto.user_id,
            desk_id=dto.desk_id,
            start_time=dto.start_time,
            end_time=dto.end_time,
        )

    @classmethod
    def from_update_dto(
        cls, db_id: UUID, dto: DeskBookingUpdateRequest
    ) -> "DeskBooking":
        """Create a DeskBooking instance from a DeskBookingUpdateRequest DTO.

        Args:
            db_id (UUID): The unique identifier for the desk booking.
            dto (DeskBookingUpdateRequest): The DTO containing updated booking details.

        Returns:
            DeskBooking: The created DeskBooking instance.

        """
        return cls(
            id=db_id,
            user_id=dto.user_id,
            desk_id=dto.desk_id,
            start_time=dto.start_time,
            end_time=dto.end_time,
        )
