from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

from src.models.dto.desk_usage_dto import DeskUsageDTO

if TYPE_CHECKING:
    from src.models.db.desk import Desk


class DeskUsage(SQLModel, table=True):
    """Tracks usage statistics for desks."""

    __tablename__ = "desk_usage"

    desk_id: int = Field(
        foreign_key="desks.id", primary_key=True, ondelete="CASCADE", sa_type=BigInteger
    )

    # Usage counters
    activations_counter: int = Field(default=0)
    sit_stand_counter: int = Field(default=0)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship
    desk: "Desk" = Relationship(back_populates="usage")

    @classmethod
    def from_dto(cls, desk_id: int, dto: DeskUsageDTO) -> "DeskUsage":
        """Create a DeskUsage instance from a DeskUsageDTO.

        Args:
            desk_id (int): The identifier for the desk.
            dto (DeskUsageDTO): The DTO containing usage details.

        Returns:
            DeskUsage: The created DeskUsage instance.

        """
        return cls(
            desk_id=desk_id,
            activations_counter=dto.activations_counter,
            sit_stand_counter=dto.sit_stand_counter,
        )
