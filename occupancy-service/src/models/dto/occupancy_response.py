from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.models.db.occupancy_record import OccupancyRecord


class OccupancyResponse(BaseModel):
    """DTO for occupancy response.

    Attributes:
        id (UUID): Unique identifier for the occupancy record.
        desk_id (str): Identifier of the desk.
        occupied (bool): Whether the desk is occupied.
        timestamp (datetime): When the occupancy state was recorded.

    """

    id: UUID
    desk_id: str
    occupied: bool
    timestamp: datetime

    @classmethod
    def from_entity(cls, entity: OccupancyRecord) -> "OccupancyResponse":
        """Create an OccupancyResponse DTO from an OccupancyRecord entity.

        Args:
            entity: The OccupancyRecord entity.

        Returns:
            OccupancyResponse: The created DTO instance.

        """
        return cls(
            id=entity.id,
            desk_id=entity.desk_id,
            occupied=entity.occupied,
            timestamp=entity.timestamp,
        )
