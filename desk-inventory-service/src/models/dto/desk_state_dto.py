from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.models.db.desk_state import DeskState


class DeskStateDTO(BaseModel):
    """State data."""

    position_mm: int | None = None
    speed_mms: int | None = None
    status: str | None = None
    is_position_lost: bool = False
    is_overload_protection_up: bool = False
    is_overload_protection_down: bool = False
    is_anti_collision: bool = False

    @classmethod
    def from_entity(cls, entity: "DeskState") -> "DeskStateDTO":
        """Create a DeskStateDTO from a DeskState entity.

        Args:
            entity: The DeskState entity.

        Returns:
            DeskStateDTO: The created DTO instance.

        """
        return cls(
            position_mm=entity.position_mm,
            speed_mms=entity.speed_mms,
            status=entity.status,
            is_position_lost=entity.is_position_lost,
            is_overload_protection_up=entity.is_overload_protection_up,
            is_overload_protection_down=entity.is_overload_protection_down,
            is_anti_collision=entity.is_anti_collision,
        )
