from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeskBookingUpdateRequest(BaseModel):
    """DTO for updating a desk booking request.

    Attributes:
        user_id (UUID): Identifier of the user making the booking.
        desk_id (UUID): Identifier of the desk to be booked.
        start_time (datetime): Start date and time of the booking.
        end_time (datetime): End date and time of the booking.

    """

    user_id: UUID
    desk_id: int
    start_time: datetime
    end_time: datetime
