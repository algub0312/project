from typing import Optional

from pydantic import BaseModel


class UserDTO(BaseModel):
    """Response model for user data."""

    user_id: str
    preferred_standing_height_cm: Optional[int] = None
    preferred_sitting_height_cm: Optional[int] = None
    user_height_cm: Optional[int] = None
