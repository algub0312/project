from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from src.models.db.desk_error import DeskError


class DeskErrorDTO(BaseModel):
    """Error log entry."""

    time_s: int
    error_code: int
    recorded_at: datetime | None = None

    @classmethod
    def from_entity(cls, entity: "DeskError") -> "DeskErrorDTO":
        """Create a DeskErrorDTO from a DeskError entity.

        Args:
            entity: The DeskError entity.

        Returns:
            DeskErrorDTO: The created DTO instance.

        """
        return cls(
            time_s=entity.time_s,
            error_code=entity.error_code,
            recorded_at=entity.recorded_at,
        )
