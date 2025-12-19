from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

from src.models.dto.desk_config_dto import DeskConfigDTO

if TYPE_CHECKING:
    from src.models.db.desk import Desk


class DeskConfig(SQLModel, table=True):
    """Stores configuration information for desks."""

    __tablename__ = "desk_config"

    desk_id: int = Field(
        foreign_key="desks.id",
        primary_key=True,
        index=True,
        ondelete="CASCADE",
        sa_type=BigInteger,
    )

    # Configuration fields
    name: str
    manufacturer: str | None = None

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship
    desk: "Desk" = Relationship(back_populates="config")

    @classmethod
    def from_dto(cls, desk_id: int, dto: DeskConfigDTO) -> "DeskConfig":
        """Create a DeskConfig instance from a DeskConfigDTO.

        Args:
            desk_id (int): The identifier for the desk.
            dto (DeskConfigDTO): The DTO containing configuration details.

        Returns:
            DeskConfig: The created DeskConfig instance.

        """
        return cls(
            desk_id=desk_id,
            name=dto.name,
            manufacturer=dto.manufacturer,
        )
