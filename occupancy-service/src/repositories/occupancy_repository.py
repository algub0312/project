from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlmodel import Session, desc, select

from src.models.db.occupancy_record import OccupancyRecord


class OccupancyRepository:
    """Repository for managing OccupancyRecord entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create(self, record: OccupancyRecord) -> OccupancyRecord:
        """Create a new OccupancyRecord in the database.

        Args:
            record (OccupancyRecord): The OccupancyRecord entity to create.

        Returns:
            OccupancyRecord: The created OccupancyRecord entity with updated fields.

        """
        self._session.add(record)
        self._session.commit()
        self._session.refresh(record)
        return record

    def get_latest_by_desk(self, desk_id: str) -> Optional[OccupancyRecord]:
        """Retrieve the latest OccupancyRecord for a specific desk.

        Args:
            desk_id (str): The desk identifier.

        Returns:
            OccupancyRecord | None: The latest OccupancyRecord for the desk if found,
            else None.

        """
        statement = (
            select(OccupancyRecord)
            .where(OccupancyRecord.desk_id == desk_id)
            .order_by(desc(OccupancyRecord.timestamp))
            .limit(1)
        )
        return self._session.exec(statement).first()

    def get_all_latest(self) -> list[OccupancyRecord]:
        """Retrieve the latest OccupancyRecord for each desk.

        Returns:
            list[OccupancyRecord]: A list of the latest OccupancyRecord for each desk.

        """
        # Use PostgreSQL DISTINCT ON for getting latest record per desk
        statement = text("""
            SELECT DISTINCT ON (desk_id) id, desk_id, occupied, timestamp, created_at
            FROM occupancyrecord
            ORDER BY desk_id, timestamp DESC
        """)

        result = self._session.exec(statement)
        records = []
        for row in result:
            record = OccupancyRecord(
                id=row.id,
                desk_id=row.desk_id,
                occupied=row.occupied,
                timestamp=row.timestamp,
                created_at=row.created_at,
            )
            records.append(record)

        return records

    def get_history_by_desk(
        self,
        desk_id: str,
        limit: int = 100,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[OccupancyRecord]:
        """Retrieve occupancy history for a specific desk.

        Args:
            desk_id (str): The desk identifier.
            limit (int): Maximum number of records to return.
            start_date (datetime | None): Optional start date filter.
            end_date (datetime | None): Optional end date filter.

        Returns:
            list[OccupancyRecord]: A list of OccupancyRecord
            entities ordered by timestamp desc.

        """
        statement = select(OccupancyRecord).where(OccupancyRecord.desk_id == desk_id)

        # 🔧 Adaugă filtering pe date:
        if start_date:
            statement = statement.where(OccupancyRecord.timestamp >= start_date)
        if end_date:
            statement = statement.where(OccupancyRecord.timestamp <= end_date)

        statement = statement.order_by(desc(OccupancyRecord.timestamp)).limit(limit)

        return list(self._session.exec(statement).all())
