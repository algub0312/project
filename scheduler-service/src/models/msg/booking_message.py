from datetime import datetime
from uuid import UUID

from src.models.msg.abstract_message import AbstractMessage


class BookingMessage(AbstractMessage):
    """Message class for desk booking events.

    Attributes:
        booking_id (str): Unique identifier for the booking.
        desk_id (int): Identifier of the desk being booked.
        start_time (str): Start date and time of the booking in ISO format.

    """

    booking_id: UUID
    desk_id: int
    start_time: datetime
