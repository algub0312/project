from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, select

from src.models.db.monitoring_job import JobStatus, MonitoringJob
from src.models.msg.booking_message import BookingMessage


class MonitoringJobRepository:
    """Repository for managing MonitoringJob entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create(self, job: MonitoringJob) -> MonitoringJob:
        """Create a new MonitoringJob in the database.

        Args:
            job (MonitoringJob): The MonitoringJob entity to create.

        Returns:
            MonitoringJob: The created MonitoringJob entity with updated fields.

        """
        self._session.add(job)
        self._save_and_refresh(job)
        return job

    def update(self, update: BookingMessage) -> MonitoringJob | None:
        """Update an existing MonitoringJob in the database.

        Args:
            update (BookingMessage): The BookingMessage containing updated details.

        Returns:
            MonitoringJob: The updated MonitoringJob entity with refreshed fields.

        """
        persisted_job = self.get_job_by_booking_id(update.booking_id)
        if persisted_job is None:
            return None
        job = self._update_fields(persisted_job, update)
        updated_job = self._session.merge(job)
        self._save_and_refresh(updated_job)
        return updated_job

    def get_by_id(self, job_id: UUID) -> MonitoringJob | None:
        """Retrieve a MonitoringJob by its ID.

        Args:
            job_id (UUID): The ID of the MonitoringJob to retrieve.

        Returns:
            MonitoringJob | None: The MonitoringJob entity if found, else None.

        """
        return self._session.get(MonitoringJob, job_id)

    def get_job_by_booking_id(self, booking_id: UUID) -> MonitoringJob | None:
        """Retrieve a MonitoringJob by its associated booking ID.

        Args:
            booking_id (UUID): The booking ID associated with the MonitoringJob.

        Returns:
            MonitoringJob | None: The MonitoringJob entity if found, else None.

        """
        statement = select(MonitoringJob).where(MonitoringJob.booking_id == booking_id)
        results = self._session.exec(statement)
        return results.first()

    def get_jobs_in_window(
        self, start_time: datetime, end_time: datetime, status: JobStatus
    ) -> list[MonitoringJob]:
        """Retrieve MonitoringJobs within a specific time window and status.

        Args:
            start_time (datetime): The start datetime to filter jobs.
            end_time (datetime): The end datetime to filter jobs.
            status (JobStatus): The status to filter jobs.

        Returns:
            list[MonitoringJob]: A list of MonitoringJob entities.

        """
        statement = select(MonitoringJob).where(
            MonitoringJob.scheduled_time >= start_time,
            MonitoringJob.scheduled_time <= end_time,
            MonitoringJob.status == status,
        )
        results = self._session.exec(statement)
        return list(results.all())

    def get_jobs_to_promote(self, cutoff_time: datetime) -> list[MonitoringJob]:
        """Retrieve MonitoringJobs that are due for promotion.

        Args:
            cutoff_time (datetime): The cutoff datetime to filter jobs.

        Returns:
            list[MonitoringJob]: A list of MonitoringJob entities to promote.

        """
        statement = select(MonitoringJob).where(
            MonitoringJob.scheduled_time <= cutoff_time,
            MonitoringJob.scheduled_time >= datetime.now(timezone.utc),
            MonitoringJob.status == JobStatus.PENDING,
        )
        results = self._session.exec(statement)
        return list(results.all())

    def delete_by_booking_id(self, booking_id: UUID) -> MonitoringJob | None:
        """Delete a MonitoringJob by its associated booking ID.

        Args:
            booking_id (UUID): The booking ID associated with the MonitoringJob.

        Returns:
            MonitoringJob | None: The deleted MonitoringJob entity if found, else None.

        """
        job = self.get_job_by_booking_id(booking_id)
        if job is None:
            return None
        job_copy = MonitoringJob.model_copy(
            job
        )  # Detached copy to return after deletion
        self._session.delete(job)
        self._session.commit()
        return job_copy

    def mark_scheduled(self, job: MonitoringJob) -> None:
        """Mark a MonitoringJob as scheduled.

        Args:
            job (MonitoringJob): The MonitoringJob entity to mark as scheduled.

        """
        job.status = JobStatus.SCHEDULED
        merged_job = self._session.merge(job)
        self._save_and_refresh(merged_job)

    def mark_executing(self, job: MonitoringJob) -> None:
        """Mark a MonitoringJob as executing.

        Args:
            job (MonitoringJob): The MonitoringJob entity to mark as executing.

        """
        job.status = JobStatus.EXECUTING
        merged_job = self._session.merge(job)
        self._save_and_refresh(merged_job)

    def mark_completed(self, job: MonitoringJob) -> None:
        """Mark a MonitoringJob as completed.

        Args:
            job (MonitoringJob): The MonitoringJob entity to mark as completed.

        """
        job.status = JobStatus.COMPLETED
        merged_job = self._session.merge(job)
        self._save_and_refresh(merged_job)

    def mark_failed(self, job: MonitoringJob) -> None:
        """Mark a MonitoringJob as failed.

        Args:
            job (MonitoringJob): The MonitoringJob entity to mark as failed.

        """
        job.status = JobStatus.FAILED
        merged_job = self._session.merge(job)
        self._save_and_refresh(merged_job)

    def cleanup_old_jobs(self, older_than: datetime) -> None:
        """Delete MonitoringJobs older than a specified datetime.

        Args:
            older_than (datetime): The datetime threshold to delete old jobs.

        """
        statement = select(MonitoringJob).where(
            MonitoringJob.scheduled_time < older_than
        )
        results = self._session.exec(statement)
        old_jobs = results.all()
        for job in old_jobs:
            self._session.delete(job)
        self._session.commit()

    def _save_and_refresh(self, instance: MonitoringJob) -> None:
        """Save and refresh an instance in the database.

        Args:
            instance (MonitoringJob): The MonitoringJob instance to save and refresh.

        """
        self._session.commit()
        self._session.refresh(instance)

    @staticmethod
    def _update_fields(
        job: MonitoringJob, update: BookingMessage
    ) -> MonitoringJob | None:
        """Update fields of an existing MonitoringJob.

        Args:
            job (MonitoringJob): The existing MonitoringJob entity.
            update (BookingMessage): The BookingMessage containing updated details.

        Returns:
            MonitoringJob | None: The updated MonitoringJob entity, or None if no updates were made.

        """  # noqa: E501
        job.desk_id = update.desk_id
        job.scheduled_time = update.start_time
        return job
