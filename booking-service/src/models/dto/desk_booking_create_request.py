from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeskBookingCreateRequest(BaseModel):
    """DTO for creating a desk booking request.

    Attributes:
        user_id (UUID): Identifier of the user making the booking.
        desk_id (int): Identifier of the desk to be booked.
        start_time (datetime): Start date and time of the booking.
        end_time (datetime): End date and time of the booking.

    """

    user_id: UUID
    desk_id: int
    start_time: datetime
    end_time: datetime
