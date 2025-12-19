from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

from src.models.dto.desk_error_dto import DeskErrorDTO

if TYPE_CHECKING:
    from src.models.db.desk import Desk


class DeskError(SQLModel, table=True):
    """Records errors related to desks."""

    __tablename__ = "desk_errors"

    id: int | None = Field(default=None, primary_key=True)
    desk_id: int = Field(
        foreign_key="desks.id", index=True, ondelete="CASCADE", sa_type=BigInteger
    )

    # Error information from the device
    time_s: int
    error_code: int

    # Additional metadata
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship
    desk: "Desk" = Relationship(back_populates="errors")

    @classmethod
    def from_dto(cls, desk_id: int, dto: DeskErrorDTO) -> "DeskError":
        """Create a DeskError instance from a DeskErrorDTO.

        Args:
            desk_id (int): The identifier for the desk.
            dto (DeskErrorDTO): The DTO containing error details.

        Returns:
            DeskError: The created DeskError instance.

        """
        return cls(
            desk_id=desk_id,
            time_s=dto.time_s,
            error_code=dto.error_code,
        )
