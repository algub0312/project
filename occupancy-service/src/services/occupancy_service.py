from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from src.messaging.messaging_manager import MessagingManager
from src.messaging.pubsub_exchanges import DESK_OCCUPANCY_UPDATED
from src.models.db.occupancy_record import OccupancyRecord
from src.models.dto.current_occupancy_response import CurrentOccupancyResponse
from src.models.dto.occupancy_response import OccupancyResponse
from src.models.dto.occupancy_update_request import OccupancyUpdateRequest
from src.models.msg.occupancy_updated_message import OccupancyUpdatedMessage
from src.repositories.occupancy_repository import OccupancyRepository


class OccupancyService:
    """Service for managing desk occupancy."""

    def __init__(
        self,
        repo: OccupancyRepository,
        messaging: MessagingManager,
    ) -> None:
        """Initialize the OccupancyService.

        Args:
            repo (OccupancyRepository): The repository for occupancy records.
            messaging (MessagingManager): The messaging manager for handling messages.

        """
        self._repo = repo
        self._messaging = messaging
        self._denmark_tz = ZoneInfo("Europe/Copenhagen")

    async def process_mqtt_update(
        self, desk_id: str, occupied: bool, timestamp: Optional[datetime] = None
    ) -> OccupancyResponse:
        """Process an occupancy update from MQTT.

        Args:
            desk_id (str): The desk identifier.
            occupied (bool): Whether the desk is occupied.
            timestamp (Optional[datetime]): When the occupancy state was recorded.
                                          If None, current time will be used.

        Returns:
            OccupancyResponse: The response DTO containing created record details.

        """
        # Always use current time for consistency
        # (ignore any passed timestamp from MQTT)
        current_time = datetime.now().astimezone(self._denmark_tz)

        request = OccupancyUpdateRequest(
            desk_id=desk_id,
            occupied=occupied,
            timestamp=current_time,  # Always use current server time
        )

        # Create record in database
        record = self._repo.create(OccupancyRecord.from_dto(request))

        # Publish to RabbitMQ
        await self._publish_occupancy_update(record)

        print(f"Processed MQTT update for {desk_id}: {occupied} at {current_time}")
        return OccupancyResponse.from_entity(record)

    async def _publish_occupancy_update(self, record: OccupancyRecord) -> None:
        """Publish occupancy update to RabbitMQ.

        Args:
            record (OccupancyRecord): The occupancy record to publish.

        """
        try:
            message = OccupancyUpdatedMessage(
                desk_id=record.desk_id,
                occupied=record.occupied,
                timestamp=record.timestamp,
            )

            pubsub = self._messaging.get_pubsub(DESK_OCCUPANCY_UPDATED)
            await pubsub.publish(message)

        except Exception as e:
            print(f"Failed to publish occupancy update: {e}")

    def get_current_occupancy(self, desk_id: str) -> Optional[CurrentOccupancyResponse]:
        """Get current occupancy status for a desk.

        Args:
            desk_id (str): The desk identifier.

        Returns:
            CurrentOccupancyResponse | None:
            Current occupancy status if found, else None.

        """
        record = self._repo.get_latest_by_desk(desk_id)
        if record:
            return CurrentOccupancyResponse(
                desk_id=record.desk_id,
                occupied=record.occupied,
                last_updated=record.timestamp,
            )
        return None

    def get_all_current_occupancy(self) -> list[CurrentOccupancyResponse]:
        """Get current occupancy status for all desks.

        Returns:
            list[CurrentOccupancyResponse]: A list of current occupancy statuses.

        """
        records = self._repo.get_all_latest()
        return [
            CurrentOccupancyResponse(
                desk_id=record.desk_id,
                occupied=record.occupied,
                last_updated=record.timestamp,
            )
            for record in records
        ]

    def get_occupancy_history(
        self,
        desk_id: str,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[OccupancyResponse]:
        """Get occupancy history for a desk.

        Args:
            desk_id (str): The desk identifier.
            limit (int): Maximum number of records to return.
            start_date (datetime | None): Optional start date filter.
            end_date (datetime | None): Optional end date filter.

        Returns:
            list[OccupancyResponse]: A list of occupancy records.

        """
        if start_date is None and end_date is None:
            records = self._repo.get_history_by_desk(desk_id, limit)
        else:
            records = self._repo.get_history_by_desk(
                desk_id, limit, start_date, end_date
            )
        return [OccupancyResponse.from_entity(record) for record in records]
