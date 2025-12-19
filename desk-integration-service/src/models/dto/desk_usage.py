from pydantic import BaseModel


class DeskUsage(BaseModel):
    """Data model representing the usage statistics of a desk."""

    activations_counter: int
    sit_stand_counter: int
