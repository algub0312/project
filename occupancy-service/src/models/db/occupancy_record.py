from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, Column
from sqlmodel import Field, SQLModel

from src.models.dto.occupancy_update_request import OccupancyUpdateRequest


class OccupancyRecord(SQLModel, table=True):
    """Database model for an occupancy record.

    Attributes:
        id (UUID): Unique identifier for the occupancy record.
        desk_id (str): Identifier of the desk.
        occupied (bool): Whether the desk is occupied.
        timestamp (datetime): When the occupancy state was recorded.
        created_at (datetime): When this record was created in the database.

    """

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    desk_id: str = Field(index=True)
    occupied: bool
    timestamp: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True), index=True))
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), default=lambda: datetime.now().astimezone()
        )
    )

    @classmethod
    def from_dto(cls, dto: OccupancyUpdateRequest) -> "OccupancyRecord":
        """Create an OccupancyRecord instance from an OccupancyUpdateRequest DTO.

        Args:
            dto (OccupancyUpdateRequest): The DTO containing occupancy details.

        Returns:
            OccupancyRecord: The created OccupancyRecord instance.

        """
        return cls(
            desk_id=dto.desk_id,
            occupied=dto.occupied,
            timestamp=dto.timestamp,
        )
