from typing import Optional

from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    """Request model for creating a user."""

    user_id: str
    preferred_standing_height_cm: Optional[int] = None
    preferred_sitting_height_cm: Optional[int] = None
    user_height_cm: Optional[int] = None
