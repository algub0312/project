import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.messaging.messaging_manager import MessagingManager
from src.models.db.monitoring_job import MonitoringJob
from src.repositories.monitoring_job_repository import MonitoringJobRepository
from src.services.monitoring.job_executor import MonitoringJobExecutor
from src.services.monitoring.monitoring_scheduler_manager import (
    MonitoringSchedulerManager,
)
from src.services.monitoring.utils.create_cron_trigger_from_datetime import (
    create_cron_trigger_from_datetime,
)

logger = logging.getLogger(__name__)

PROMOTION_INTERVAL_MINUTES = 5
PROMOTION_LOOKAHEAD_MINUTES = 15


class JobPromotionService:
    """Service for periodically moving far-future jobs into active scheduling."""

    def __init__(
        self,
        repository: MonitoringJobRepository,
        scheduler_manager: MonitoringSchedulerManager,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the JobPromotionService.

        Args:
            repository (MonitoringJobRepository): The repository for monitoring jobs.
            scheduler_manager (MonitoringSchedulerManager): The scheduler manager for scheduling jobs.
            messaging (MessagingManager): The messaging manager for pub/sub communication.

        """  # noqa: E501
        self._repository = repository
        self._scheduler_manager = scheduler_manager
        self._job_executor = MonitoringJobExecutor(self._repository, messaging)
        self._promotion_scheduler = BackgroundScheduler()

    def start(self) -> None:
        """Start periodic promotion task."""
        self._promotion_scheduler.add_job(
            func=self._promote_jobs,
            trigger=IntervalTrigger(minutes=PROMOTION_INTERVAL_MINUTES),
            id="job_promotion_task",
            replace_existing=True,
        )

    def stop(self) -> None:
        """Stop periodic promotion task."""
        self._promotion_scheduler.shutdown()

    def _promote_jobs(self) -> None:
        """Promote far-future jobs into active scheduling."""
        lookahead_time = datetime.now() + timedelta(minutes=PROMOTION_LOOKAHEAD_MINUTES)
        jobs_to_promote = self._repository.get_jobs_to_promote(lookahead_time)
        non_existent_jobs = self._get_non_existent_jobs(jobs_to_promote)
        self._schedule_new_jobs(non_existent_jobs)

    def _get_non_existent_jobs(
        self, jobs_to_promote: list[MonitoringJob]
    ) -> list[MonitoringJob]:
        """Filter out jobs that already exist in the scheduler.

        Args:
            jobs_to_promote (list[MonitoringJob]): List of jobs to check.

        Returns:
            list[MonitoringJob]: List of jobs that do not exist in the scheduler.

        """
        return [
            job
            for job in jobs_to_promote
            if not self._scheduler_manager.job_exists(str(job.job_id))
        ]

    def _schedule_new_jobs(self, non_existent_jobs: list[MonitoringJob]) -> None:
        """Schedule new jobs that do not exist in the scheduler.

        Args:
            non_existent_jobs (list[MonitoringJob]): List of jobs to schedule.

        """
        for job in non_existent_jobs:
            trigger = create_cron_trigger_from_datetime(job.scheduled_time)
            self._scheduler_manager.schedule_job(
                func=self._job_executor.execute_job,
                trigger=trigger,
                job_id=str(job.job_id),
                args=(job.job_id,),
            )
            logger.info(
                "Promoted job %s scheduled for %s into active scheduling.",
                job.job_id,
                job.scheduled_time,
            )
            self._repository.mark_scheduled(job)
