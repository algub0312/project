from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

from src.models.dto.desk_config_dto import DeskConfigDTO
from src.models.dto.desk_error_dto import DeskErrorDTO
from src.models.dto.desk_state_dto import DeskStateDTO
from src.models.dto.desk_usage_dto import DeskUsageDTO

if TYPE_CHECKING:
    from src.models.db.desk import Desk


class DeskInventoryDTO(BaseModel):
    """DTO for desk inventory data.

    Attributes:
        id (int): Unique identifier for the desk.
        floor (int | None): Floor number where the desk is located.
        orientation (str | None): Orientation of the desk.
        pos_x (int | None): X coordinate in the office layout.
        pos_y (int | None): Y coordinate in the office layout.
        config (src.models.dto.desk_config_dto.DeskConfigDTO | None): Configuration data.
        state (src.models.dto.desk_state_dto.DeskStateDTO | None): Current state data.
        usage (src.models.dto.desk_usage_dto.DeskUsageDTO | None): Usage statistics.
        errors (list[src.models.dto.desk_error_dto.DeskErrorDTO]): Recent error logs.
        created_at (datetime): When the desk was added to inventory.
        updated_at (datetime): Last update timestamp.

    """  # noqa: E501

    id: int
    floor: int | None = None
    orientation: str | None = None
    pos_x: int | None = None
    pos_y: int | None = None
    config: DeskConfigDTO | None = None
    state: DeskStateDTO | None = None
    usage: DeskUsageDTO | None = None
    errors: list[DeskErrorDTO] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, entity: "Desk") -> "DeskInventoryDTO":
        """Create a DeskInventoryDTO from a Desk entity.

        Args:
            entity: The Desk entity with relationships loaded.

        Returns:
            DeskInventoryDTO: The created DTO instance.

        """
        return cls(
            id=entity.id,
            floor=entity.floor,
            orientation=entity.orientation,
            pos_x=entity.pos_x,
            pos_y=entity.pos_y,
            config=DeskConfigDTO.from_entity(entity.config) if entity.config else None,
            state=DeskStateDTO.from_entity(entity.state) if entity.state else None,
            usage=DeskUsageDTO.from_entity(entity.usage) if entity.usage else None,
            errors=[DeskErrorDTO.from_entity(error) for error in entity.errors],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @classmethod
    def from_dict(cls, desk_id: int, data: dict) -> "DeskInventoryDTO":
        """Create a DeskInventoryDTO from a dictionary.

        Args:
            desk_id: The unique identifier for the desk.
            data: The dictionary containing desk inventory data.

        Returns:
            DeskInventoryDTO: The created DTO instance.

        """
        return cls(
            id=desk_id,
            floor=data.get("floor"),
            orientation=data.get("orientation"),
            pos_x=data.get("pos_x"),
            pos_y=data.get("pos_y"),
            config=DeskConfigDTO(
                name=data.get("config").get("name"),
                manufacturer=data.get("config").get("manufacturer"),
            ),
            state=DeskStateDTO(
                position_mm=data.get("state").get("position_mm"),
                speed_mms=data.get("state").get("speed_mms"),
                status=data.get("state").get("status"),
                is_position_lost=data.get("state").get("is_position_lost"),
                is_overload_protection_up=data.get("state").get(
                    "is_overload_protection_up"
                ),
                is_overload_protection_down=data.get("state").get(
                    "is_overload_protection_down"
                ),
                is_anti_collision=data.get("state").get("is_anti_collision"),
            ),
            usage=DeskUsageDTO(
                activations_counter=data.get("usage").get("activations_counter"),
                sit_stand_counter=data.get("usage").get("sit_stand_counter"),
            ),
            errors=[
                DeskErrorDTO(
                    time_s=error.get("time_s"),
                    error_code=error.get("error_code"),
                )
                for error in data.get("last_errors", [])
            ],
        )
