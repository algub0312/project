import enum
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Column, Enum, Field, SQLModel

from src.models.msg.booking_message import BookingMessage


class JobStatus(str, enum.Enum):
    """Enumeration of possible job statuses."""

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MonitoringJob(SQLModel, table=True):
    """Database model for a monitoring job.

    Attributes:
        job_id (UUID): Unique identifier for the monitoring job.
        booking_id (UUID): Identifier of the associated booking.
        scheduled_time (datetime): Scheduled date and time for the job.
        status (JobStatus): Current status of the job.
        created_at (datetime): Timestamp when the job was created.
        updated_at (datetime): Timestamp when the job was last updated.

    """

    job_id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    booking_id: UUID = Field(index=True)
    desk_id: int = Field(index=True)
    scheduled_time: datetime
    status: JobStatus = Field(
        default=JobStatus.PENDING, sa_column=Column(Enum(JobStatus))
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_dto(cls, dto: BookingMessage) -> "MonitoringJob":
        """Create a MonitoringJob instance from a BookingMessage DTO.

        Args:
            dto (BookingMessage): The DTO containing booking message details.

        Returns:
            MonitoringJob: The created MonitoringJob instance.

        """
        return cls(
            booking_id=dto.booking_id,
            desk_id=dto.desk_id,
            scheduled_time=dto.start_time,
        )
