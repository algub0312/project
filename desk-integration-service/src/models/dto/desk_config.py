from pydantic import BaseModel


class DeskConfig(BaseModel):
    """Data model representing a desk configuration."""

    name: str
    manufacturer: str
