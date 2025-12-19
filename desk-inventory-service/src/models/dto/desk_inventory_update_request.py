from pydantic import BaseModel


class DeskInventoryUpdateRequest(BaseModel):
    """DTO for updating desk inventory data.

    Attributes:
        orientation (str | None): Orientation of the desk.
        pos_x (float | None): X coordinate in the office layout.
        pos_y (float | None): Y coordinate in the office layout.

    """

    orientation: str | None = None
    pos_x: float | None = None
    pos_y: float | None = None
