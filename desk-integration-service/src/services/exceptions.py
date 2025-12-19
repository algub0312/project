"""Custom exceptions for the Desk Service."""

from typing import Optional


class DeskServiceError(RuntimeError):
    """Base exception raised for desk service errors."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        """Initialize DeskServiceError.

        Args:
            message: Error message describing what went wrong.
            status_code: Optional HTTP status code if applicable.

        """
        super().__init__(message)
        self.status_code = status_code
