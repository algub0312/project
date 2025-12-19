from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

from src.models.dto.desk_state_dto import DeskStateDTO

if TYPE_CHECKING:
    from src.models.db.desk import Desk


class DeskState(SQLModel, table=True):
    """Stores current state information for desks."""

    __tablename__ = "desk_state"

    desk_id: int = Field(
        foreign_key="desks.id",
        primary_key=True,
        index=True,
        ondelete="CASCADE",
        sa_type=BigInteger,
    )

    # Position and movement
    position_mm: int | None = None
    speed_mms: int | None = None

    # Status
    status: str | None = None

    # Flags
    is_position_lost: bool = Field(default=False)
    is_overload_protection_up: bool = Field(default=False)
    is_overload_protection_down: bool = Field(default=False)
    is_anti_collision: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship
    desk: "Desk" = Relationship(back_populates="state")

    @classmethod
    def from_dto(cls, desk_id: int, dto: DeskStateDTO) -> "DeskState":
        """Create a DeskState instance from a DeskStateDTO.

        Args:
            desk_id (int): The identifier for the desk.
            dto (DeskStateDTO): The DTO containing state details.

        Returns:
            DeskState: The created DeskState instance.

        """
        return cls(
            desk_id=desk_id,
            position_mm=dto.position_mm,
            speed_mms=dto.speed_mms,
            status=dto.status,
            is_position_lost=dto.is_position_lost,
            is_overload_protection_up=dto.is_overload_protection_up,
            is_overload_protection_down=dto.is_overload_protection_down,
            is_anti_collision=dto.is_anti_collision,
        )
