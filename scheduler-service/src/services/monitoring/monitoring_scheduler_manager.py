from functools import lru_cache
from typing import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class MonitoringSchedulerManager:
    """Manager for scheduling monitoring jobs using APScheduler."""

    def __init__(self) -> None:
        """Initialize the MonitoringSchedulerManager with a scheduler instance."""
        self._scheduler = AsyncIOScheduler()

    def start(self) -> None:
        """Start the scheduler."""
        self._scheduler.start()

    def shutdown(self) -> None:
        """Shut down the scheduler."""
        self._scheduler.shutdown()

    def schedule_job(
        self, func: Callable, trigger: CronTrigger, job_id: str, args: tuple
    ) -> None:
        """Schedule a job with the given parameters.

        Args:
            func (Callable): The function to be scheduled.
            trigger (CronTrigger): The type of trigger to use (e.g., 'interval', 'date', 'cron').
            job_id (str): The unique identifier for the job.
            args (tuple): The arguments to pass to the scheduled function.

        """  # noqa: E501
        self._scheduler.add_job(
            func=func, trigger=trigger, id=job_id, replace_existing=True, args=args
        )

    def reschedule_job(
        self,
        job_id: str,
        new_trigger: CronTrigger,
    ) -> None:
        """Reschedule an existing job with a new trigger.

        Args:
            job_id (str): The unique identifier for the job to be rescheduled.
            new_trigger (CronTrigger): The new trigger to use for the job.

        """
        job = self._scheduler.get_job(job_id)
        if job is None:
            raise ValueError(f"Job with ID {job_id} does not exist.")
        job.reschedule(new_trigger)

    def remove_job(self, job_id: str) -> None:
        """Remove a job from the scheduler.

        Args:
            job_id (str): The unique identifier for the job to be removed.

        """
        self._scheduler.remove_job(job_id)

    def job_exists(self, job_id: str) -> bool:
        """Check if a job exists in the scheduler.

        Args:
            job_id (str): The unique identifier for the job.

        Returns:
            bool: True if the job exists, False otherwise.

        """
        return self._scheduler.get_job(job_id) is not None

    @staticmethod
    @lru_cache(maxsize=1)
    def get_instance() -> "MonitoringSchedulerManager":
        """Get a singleton instance of MonitoringSchedulerManager.

        Returns:
            MonitoringSchedulerManager: The singleton instance.

        """
        return MonitoringSchedulerManager()
