import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.repositories.monitoring_job_repository import MonitoringJobRepository

logger = logging.getLogger(__name__)

CLEANUP_INTERVAL_HOURS = 24
CUT_OFF_DAYS = 30


class JobCleanupService:
    """Service for periodically cleaning up old monitoring jobs."""

    def __init__(self, repository: MonitoringJobRepository) -> None:
        """Initialize the JobCleanupService with a MonitoringJobRepository instance.

        Args:
            repository (MonitoringJobRepository): The repository for monitoring jobs.

        """
        self._repository = repository
        self._scheduler = BackgroundScheduler()

    def start(self) -> None:
        """Start the cleanup scheduler."""
        self._scheduler.start()
        self._scheduler.add_job(
            func=self.cleanup_old_jobs,
            trigger=IntervalTrigger(hours=CLEANUP_INTERVAL_HOURS),
            id="job_cleanup_task",
            replace_existing=True,
        )

    def stop(self) -> None:
        """Stop the cleanup scheduler."""
        self._scheduler.shutdown()

    def cleanup_old_jobs(self) -> None:
        """Cleanup old monitoring jobs from the repository."""
        try:
            older_than = datetime.now() - timedelta(days=CUT_OFF_DAYS)
            self._repository.cleanup_old_jobs(older_than)
            logger.info("Old monitoring jobs cleanup completed successfully.")
        except Exception as e:
            logger.exception("Error during old monitoring jobs cleanup: %s", e)
