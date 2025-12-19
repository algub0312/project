from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.models.db.desk_config import DeskConfig


class DeskConfigDTO(BaseModel):
    """Configuration data."""

    name: str
    manufacturer: str | None = None

    @classmethod
    def from_entity(cls, entity: "DeskConfig") -> "DeskConfigDTO":
        """Create a DeskConfigDTO from a DeskConfig entity.

        Args:
            entity: The DeskConfig entity.

        Returns:
            DeskConfigDTO: The created DTO instance.

        """
        return cls(
            name=entity.name,
            manufacturer=entity.manufacturer,
        )
