from typing import Optional

from pydantic import BaseModel, Field


class CronSchedule(BaseModel):
    """Cron-like time specification for a recurring job using a 24-hour clock."""

    hour: int = Field(ge=0, le=23, description="Hour (0-23)")
    minute: int = Field(ge=0, le=59, description="Minute (0-59)")
    day_of_week: str = Field(
        default="*", description="Day of week (e.g., 'mon-fri', '*', '0-6')"
    )


class ScheduleCreate(BaseModel):
    """Payload for creating a scheduled desk action with an optional custom ID."""

    name: str = Field(..., description="Name of the schedule")
    position_mm: int = Field(
        default=1200, ge=0, description="Target position in millimeters"
    )
    cron: CronSchedule
    id: Optional[str] = Field(None, description="Optional custom ID for the schedule")


class ScheduleResponse(BaseModel):
    """Response returned after creating a schedule, including the next run time."""

    message: str
    job_id: str
    next_run: Optional[str] = None


class Schedule(BaseModel):
    """Public representation of a scheduled job and its trigger details."""

    id: str
    name: str
    next_run: Optional[str]
    trigger: str


class DeskPositionRequest(BaseModel):
    """Request body to set a target desk height in millimeters."""

    position_mm: int = Field(
        default=1200, ge=0, description="Target position in millimeters"
    )


class DeskActionResult(BaseModel):
    """Result of a desk action attempt for a specific desk."""

    desk_id: str
    success: bool
    position_mm: int


class HealthResponse(BaseModel):
    """Health and runtime status of the scheduler service."""

    status: str
    scheduler_running: bool
    jobs_count: int
