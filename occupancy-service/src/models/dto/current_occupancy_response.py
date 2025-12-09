from datetime import datetime

from pydantic import BaseModel


class CurrentOccupancyResponse(BaseModel):
    """DTO for current occupancy status response.

    Attributes:
        desk_id (str): Identifier of the desk.
        occupied (bool): Whether the desk is currently occupied.
        last_updated (datetime): When the occupancy state was last updated.

    """

    desk_id: str
    occupied: bool
    last_updated: datetime
