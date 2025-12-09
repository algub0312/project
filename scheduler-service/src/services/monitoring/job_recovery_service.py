import logging
from datetime import datetime

from src.messaging.messaging_manager import MessagingManager
from src.models.db.monitoring_job import JobStatus, MonitoringJob
from src.repositories.monitoring_job_repository import MonitoringJobRepository
from src.services.monitoring.job_executor import MonitoringJobExecutor
from src.services.monitoring.monitoring_scheduler_manager import (
    MonitoringSchedulerManager,
)
from src.services.monitoring.utils.create_cron_trigger_from_datetime import (
    create_cron_trigger_from_datetime,
)

logger = logging.getLogger(__name__)


class JobRecoveryService:
    """Service for recovering pending and executing jobs on startup."""

    def __init__(
        self,
        repository: MonitoringJobRepository,
        scheduler_manager: MonitoringSchedulerManager,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the JobRecoveryService with a MonitoringJobRepository instance.

        Args:
            repository (MonitoringJobRepository): The repository for monitoring jobs.
            scheduler_manager (MonitoringSchedulerManager): The scheduler manager for scheduling jobs.
            messaging (MessagingManager): The messaging manager for pub/sub communication.

        """  # noqa: E501
        self._repository = repository
        self._scheduler_manager = scheduler_manager
        self._job_executor = MonitoringJobExecutor(self._repository, messaging)

    def recover_on_startup(self) -> None:
        """Recover pending and executing jobs on service startup for the current day."""
        window_start, window_end = self._get_active_window_from_today()
        pending_jobs = self._repository.get_jobs_in_window(
            window_end, window_start, JobStatus.PENDING
        )
        failed_during_execution = self._repository.get_jobs_in_window(
            window_end, window_start, JobStatus.EXECUTING
        )
        self._mark_failed(failed_during_execution)
        recovered_jobs = self._get_recoverable_jobs(pending_jobs)
        self._schedule_jobs(recovered_jobs)

        logger.info(
            "Job recovery complete. Recovered %d jobs, marked %d as failed during execution, %d as missed.",  # noqa: E501
            len(recovered_jobs),
            len(failed_during_execution),
            len(pending_jobs) - len(recovered_jobs),
        )

    @staticmethod
    def _get_active_window_from_today() -> tuple[datetime, datetime]:
        """Get the active window for today from start to end of the day.

        Returns:
            tuple[datetime, datetime]: The start and end datetime of today's active window.

        """  # noqa: E501
        active_window_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        active_window_end = datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        return active_window_end, active_window_start

    def _mark_failed(self, jobs: list[MonitoringJob]) -> None:
        """Mark jobs that failed during execution as failed.

        Args:
            jobs (list[MonitoringJob]): List of jobs that failed during execution.

        """
        for job in jobs:
            self._repository.mark_failed(job)

    def _get_recoverable_jobs(self, jobs: list[MonitoringJob]) -> list[MonitoringJob]:
        """Filter out jobs that are scheduled in the past and mark them as failed.

        Args:
            jobs (list[MonitoringJob]): List of jobs to filter.

        Returns:
            list[MonitoringJob]: List of recoverable jobs.

        """
        recovered_jobs = []
        for job in jobs:
            if job.scheduled_time < datetime.now():
                self._repository.mark_failed(job)
            else:
                recovered_jobs.append(job)
        return recovered_jobs

    def _schedule_jobs(self, jobs: list[MonitoringJob]) -> None:
        """Schedule recovered jobs in the scheduler manager.

        Args:
            jobs (list[MonitoringJob]): List of jobs to schedule.

        """
        for job in jobs:
            self._scheduler_manager.schedule_job(
                func=self._job_executor.execute_job,
                trigger=create_cron_trigger_from_datetime(job.scheduled_time),
                job_id=str(job.job_id),
                args=(job.job_id,),
            )
