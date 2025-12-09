"""Database model for scheduled desk actions."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Schedule(SQLModel, table=True):
    """Database model for a scheduled desk action.

    Attributes:
        id (UUID): Unique identifier for the schedule.
        job_id (str): Unique job identifier for APScheduler.
        name (str): Human-readable name for the schedule.
        position_mm (int): Target position in millimeters.
        hour (int): Hour to execute (0-23).
        minute (int): Minute to execute (0-59).
        day_of_week (str): Days to run (e.g., '*', 'mon-fri', '0-6').
        is_active (bool): Whether the schedule is currently active.
        created_at (datetime): When the schedule was created.
        updated_at (datetime): When the schedule was last updated.

    """

    __tablename__ = "schedules"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    job_id: str = Field(unique=True, index=True)
    name: str
    position_mm: int
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    day_of_week: str = Field(default="*")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
