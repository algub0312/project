from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.models.db.desk_usage import DeskUsage


class DeskUsageDTO(BaseModel):
    """Usage statistics."""

    activations_counter: int = 0
    sit_stand_counter: int = 0

    @classmethod
    def from_entity(cls, entity: "DeskUsage") -> "DeskUsageDTO":
        """Create a DeskUsageDTO from a DeskUsage entity.

        Args:
            entity: The DeskUsage entity.

        Returns:
            DeskUsageDTO: The created DTO instance.

        """
        return cls(
            activations_counter=entity.activations_counter,
            sit_stand_counter=entity.sit_stand_counter,
        )
