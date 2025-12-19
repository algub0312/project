from pydantic import BaseModel


class DeskState(BaseModel):
    """Data model representing the state of a desk."""

    position_mm: int
    speed_mms: int
    status: str
    is_position_lost: bool
    is_overload_protection_up: bool
    is_overload_protection_down: bool
    is_anti_collision: bool
