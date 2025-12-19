from typing import Optional

from pydantic import BaseModel


class UserUpdateRequest(BaseModel):
    """Request model for updating user preferences."""

    preferred_standing_height_cm: Optional[int] = None
    preferred_sitting_height_cm: Optional[int] = None
    user_height_cm: Optional[int] = None
