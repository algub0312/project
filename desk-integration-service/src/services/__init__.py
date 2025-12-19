"""Services package for desk integration."""

from .config import DeskServiceConfig
from .desk_service import DeskService
from .exceptions import DeskServiceError

__all__ = ["DeskService", "DeskServiceConfig", "DeskServiceError"]
