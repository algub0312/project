from pydantic import BaseModel


class DeskInventoryCreateRequest(BaseModel):
    """DTO for creating a desk inventory entry.

    Attributes:
        desk_id (int): Unique identifier for the desk.

    """

    desk_id: int
