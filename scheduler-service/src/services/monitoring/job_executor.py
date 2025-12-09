import logging
from uuid import UUID

from src.messaging.direct_exchanges import DESK_MONITORING, ROUTING_KEY
from src.messaging.messaging_manager import MessagingManager
from src.models.msg.monitoring_requested_message import MonitoringRequestedMessage
from src.repositories.monitoring_job_repository import MonitoringJobRepository

logger = logging.getLogger(__name__)


class MonitoringJobExecutor:
    """Executor for monitoring jobs."""

    def __init__(
        self, repository: MonitoringJobRepository, messaging: MessagingManager
    ) -> None:
        """Initialize the JobExecutor with a MonitoringJobRepository instance.

        Args:
            repository (MonitoringJobRepository): The repository for monitoring jobs.
            messaging (MessagingManager): The messaging manager for pub/sub communication.

        """  # noqa: E501
        self._repository = repository
        self._messaging = messaging

    async def execute_job(self, job_id: UUID) -> None:
        """Execute the job with the given ID.

        Args:
            job_id (UUID): The ID of the job to execute.

        """
        job = self._repository.get_by_id(job_id)
        if job is None:
            raise ValueError(f"Job with ID {job_id} does not exist.")
        self._repository.mark_executing(job)
        await self._send_message(job.desk_id)
        self._repository.mark_completed(job)

    async def _send_message(self, desk_id: int) -> None:
        """Send a message to the occupancy service.

        Args:
            desk_id (int): The ID of the desk to monitor.

        """
        await self._messaging.get_direct(DESK_MONITORING).send_message(
            MonitoringRequestedMessage(desk_id=desk_id),
            ROUTING_KEY,
        )
