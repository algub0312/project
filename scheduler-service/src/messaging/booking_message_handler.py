import logging
from datetime import datetime

from src.messaging.messaging_manager import MessagingManager
from src.messaging.pubsub_exchanges import (
    DESK_BOOKING_CREATED,
    DESK_BOOKING_DELETED,
    DESK_BOOKING_UPDATED,
)
from src.models.db.monitoring_job import MonitoringJob
from src.models.msg.booking_message import BookingMessage
from src.repositories.monitoring_job_repository import MonitoringJobRepository
from src.services.monitoring.job_executor import MonitoringJobExecutor
from src.services.monitoring.monitoring_scheduler_manager import (
    MonitoringSchedulerManager,
)
from src.services.monitoring.utils.create_cron_trigger_from_datetime import (
    create_cron_trigger_from_datetime,
)

logger = logging.getLogger(__name__)

SCHEDULER_DESK_BOOKING_CREATED_QUEUE = "scheduler.desk.booking.created.queue"
SCHEDULER_DESK_BOOKING_UPDATED_QUEUE = "scheduler.desk.booking.updated.queue"
SCHEDULER_DESK_BOOKING_DELETED_QUEUE = "scheduler.desk.booking.deleted.queue"


class BookingMessageHandler:
    """Handler for booking-related messages from pub/sub topics."""

    def __init__(
        self,
        repo: MonitoringJobRepository,
        manager: MonitoringSchedulerManager,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the BookingMessageHandler.

        Args:
            repo (MonitoringJobRepository): The repository for monitoring jobs.
            manager (MonitoringSchedulerManager): The scheduler manager for scheduling jobs.
            messaging (MessagingManager): The messaging manager for pub/sub communication.

        """  # noqa: E501
        self._repository = repo
        self._scheduler_manager = manager
        self._messaging = messaging
        self._job_executor = MonitoringJobExecutor(self._repository, self._messaging)

    def start(self) -> None:
        """Start the booking message handler by initializing subscriptions."""
        self._initialize_subscription()

    def _initialize_subscription(self) -> None:
        """Initialize subscriptions to booking-related pub/sub topics."""
        self._messaging.get_pubsub(DESK_BOOKING_CREATED).subscribe(
            SCHEDULER_DESK_BOOKING_CREATED_QUEUE, self._handle_create, BookingMessage
        )
        self._messaging.get_pubsub(DESK_BOOKING_UPDATED).subscribe(
            SCHEDULER_DESK_BOOKING_UPDATED_QUEUE, self._handle_update, BookingMessage
        )
        self._messaging.get_pubsub(DESK_BOOKING_DELETED).subscribe(
            SCHEDULER_DESK_BOOKING_DELETED_QUEUE, self._handle_delete, BookingMessage
        )

    async def _handle_create(self, message: BookingMessage) -> None:
        """Handle booking creation messages.

        Args:
            message (BookingMessage): The booking message containing booking details.

        """
        job = self._repository.create(MonitoringJob.from_dto(message))
        if self._is_today(job.scheduled_time):
            self._schedule_job(job, message)

    async def _handle_update(self, message: BookingMessage) -> None:
        """Handle booking update messages.

        Args:
            message (BookingMessage): The booking message containing updated booking details.

        """  # noqa: E501
        job = self._repository.update(message)
        if self._is_today(job.scheduled_time):
            self._schedule_job(job, message)

    async def _handle_delete(self, message: BookingMessage) -> None:
        """Handle booking deletion messages.

        Args:
            message (BookingMessage): The booking message containing booking details.

        """
        job = self._repository.delete_by_booking_id(message.booking_id)
        if job and self._is_today(job.scheduled_time):
            self._scheduler_manager.remove_job(str(job.job_id))
            logger.info(
                "Removed scheduled job %s for booking %s as the booking was deleted.",
                job.job_id,
                message.booking_id,
            )

    def _schedule_job(self, job: MonitoringJob, message: BookingMessage) -> None:
        """Schedule a monitoring job for execution.

        Args:
            job (MonitoringJob): The monitoring job to be scheduled.
            message (BookingMessage): The booking message associated with the job.

        """
        trigger = create_cron_trigger_from_datetime(job.scheduled_time)
        self._scheduler_manager.schedule_job(
            func=self._job_executor.execute_job,
            trigger=trigger,
            job_id=str(job.job_id),
            args=(job.job_id,),
        )
        logger.info(
            "Scheduled job %s for booking %s as the booking is today.",
            job.job_id,
            message.booking_id,
        )

    @staticmethod
    def _is_today(scheduled_time: datetime) -> bool:
        """Check if the scheduled_time is today.

        Args:
            scheduled_time (datetime): The scheduled time to check.

        Returns:
            bool: True if scheduled_time is today, False otherwise.

        """
        today = datetime.today()
        return scheduled_time.date() == today.date()
