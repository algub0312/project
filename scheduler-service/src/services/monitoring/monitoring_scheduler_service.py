import logging

from src.messaging.messaging_manager import MessagingManager
from src.repositories.monitoring_job_repository import MonitoringJobRepository
from src.services.monitoring.job_cleanup_service import JobCleanupService
from src.services.monitoring.job_promotion_service import JobPromotionService
from src.services.monitoring.job_recovery_service import JobRecoveryService
from src.services.monitoring.monitoring_scheduler_manager import (
    MonitoringSchedulerManager,
)

logger = logging.getLogger(__name__)


class MonitoringSchedulerService:
    """Service for managing the monitoring job scheduler."""

    def __init__(
        self,
        repo: MonitoringJobRepository,
        manager: MonitoringSchedulerManager,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the MonitoringSchedulerService.

        Args:
            repo (MonitoringJobRepository): The repository for monitoring jobs.
            manager (MonitoringSchedulerManager): The scheduler manager for scheduling jobs.
            messaging (MessagingManager): The messaging manager for pub/sub communication.

        """  # noqa: E501
        self._scheduler_manager = manager

        self._recovery_service = JobRecoveryService(
            repo, self._scheduler_manager, messaging
        )
        self._job_promotion_service = JobPromotionService(
            repo, self._scheduler_manager, messaging
        )
        self._cleanup_service = JobCleanupService(repo)

    def start(self) -> None:
        """Start the monitoring scheduler service."""
        self._scheduler_manager.start()
        self._recovery_service.recover_on_startup()
        self._job_promotion_service.start()
        self._cleanup_service.start()
        logger.info("MonitoringSchedulerService started successfully.")

    def stop(self) -> None:
        """Stop the monitoring scheduler service."""
        self._job_promotion_service.stop()
        self._cleanup_service.stop()
        self._scheduler_manager.shutdown()
        logger.info("MonitoringSchedulerService stopped successfully.")
