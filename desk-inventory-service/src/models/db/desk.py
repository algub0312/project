from datetime import UTC, datetime

from sqlalchemy import BigInteger
from sqlmodel import Field, Relationship, SQLModel

from src.models.db.desk_config import DeskConfig
from src.models.db.desk_error import DeskError
from src.models.db.desk_state import DeskState
from src.models.db.desk_usage import DeskUsage
from src.models.dto.desk_inventory_dto import DeskInventoryDTO


class Desk(SQLModel, table=True):
    """Represents a desk in the inventory system."""

    __tablename__ = "desks"

    id: int = Field(primary_key=True, sa_type=BigInteger, index=True)
    floor: int | None = None
    orientation: str | None = None
    pos_x: int | None = None
    pos_y: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    config: DeskConfig = Relationship(
        back_populates="desk",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
        cascade_delete=True,
    )
    state: DeskState = Relationship(
        back_populates="desk",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
        cascade_delete=True,
    )
    usage: DeskUsage = Relationship(
        back_populates="desk",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
        },
        cascade_delete=True,
    )
    errors: list[DeskError] = Relationship(
        back_populates="desk",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
        cascade_delete=True,
    )

    @classmethod
    def from_dto(cls, dto: DeskInventoryDTO) -> "Desk":
        """Create a Desk entity from a DeskInventoryDTO.

        Args:
            dto (DeskInventoryDTO): The DTO containing desk details.

        Returns:
            Desk: The created Desk entity.

        """
        return cls(
            id=dto.id,
            floor=dto.floor,
            orientation=dto.orientation,
            pos_x=dto.pos_x,
            pos_y=dto.pos_y,
            config=DeskConfig.from_dto(dto.id, dto.config),
            state=DeskState.from_dto(dto.id, dto.state),
            usage=DeskUsage.from_dto(dto.id, dto.usage),
            errors=[DeskError.from_dto(dto.id, error) for error in dto.errors],
        )
