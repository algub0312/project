"""Configuration for the Desk Service."""

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def load_timeout() -> int:
    """Load timeout from environment with fallback.

    Falls back to 10 seconds if the env var is missing or invalid.
    """
    raw = os.getenv("DESK_API_TIMEOUT_SECONDS", "10")
    try:
        return int(raw)
    except (TypeError, ValueError):
        logger.warning(
            "Invalid DESK_API_TIMEOUT_SECONDS value '%s'; falling back to 10 seconds",
            raw,
        )
        return 10


@dataclass(frozen=True)
class DeskServiceConfig:
    """Configuration container for the DeskService."""

    base_url: str
    api_key: str
    timeout: int = 10

    @classmethod
    def from_env(cls) -> "DeskServiceConfig":
        """Load configuration from environment variables."""
        base = ""
        operating_system = os.getenv("OPERATING_SYSTEM", "windows").lower()
        logger.info("Loading DeskServiceConfig for OS: %s", operating_system)
        if operating_system == "linux":
            base = os.getenv("DESK_API_BASE_URL_LINUX").rstrip("/")
        elif operating_system == "windows":
            base = os.getenv("DESK_API_BASE_URL_WINDOWS").rstrip("/")
        else:
            logger.info(
                "Running on Unknown OS, please check specified OS environment variable"
            )
            raise ValueError("Unsupported OS specified in environment variable")
        if base is None or base == "":
            logger.error("DESK_API_BASE_URL for %s is not set!", operating_system)
            raise ValueError(
                f"DESK_API_BASE_URL_{operating_system.upper()} is required"
            )
        api_key = os.getenv("DESK_API_KEY", "")
        timeout = load_timeout()

        if not api_key:
            logger.error("DESK_API_KEY environment variable is not set!")
            raise ValueError("DESK_API_KEY is required")

        logger.info(
            "DeskService initialized: base_url=%s, api_key=%s..., timeout=%ss",
            base,
            api_key[:8],
            timeout,
        )
        return cls(base_url=base, api_key=api_key, timeout=timeout)


# Constants
HTTP_ERROR_THRESHOLD = 400  # First HTTP error status code (4xx/5xx)
