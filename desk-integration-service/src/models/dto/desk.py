from pydantic import BaseModel

from .desk_config import DeskConfig
from .desk_error import DeskError
from .desk_state import DeskState
from .desk_usage import DeskUsage


class Desk(BaseModel):
    """Data model representing a desk."""

    config: DeskConfig
    state: DeskState
    usage: DeskUsage
    last_errors: list[DeskError] = []
