from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OccupancyUpdateRequest(BaseModel):
    """DTO for occupancy update request.

    Attributes:
        desk_id (str): Identifier of the desk.
        occupied (bool): Whether the desk is occupied.
        timestamp (Optional[datetime]): When the occupancy state was recorded.
                                       If not provided, current time will be used.

    """

    desk_id: str
    occupied: bool
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
