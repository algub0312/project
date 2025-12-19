from pydantic import BaseModel


class DeskError(BaseModel):
    """Data model representing a desk error."""

    time_s: int
    error_code: int
