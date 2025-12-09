from datetime import datetime

from src.models.msg.abstract_message import AbstractMessage


class OccupancyUpdatedMessage(AbstractMessage):
    """Message published when desk occupancy is updated."""

    desk_id: str
    occupied: bool
    timestamp: datetime
