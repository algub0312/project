"""Repository for managing Schedule entities in the database."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Session, select

from src.models.db.schedule import Schedule


class DeskPositionScheduleRepository:
    """Repository for managing Schedule entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create(self, schedule: Schedule) -> Schedule:
        """Create a new Schedule in the database.

        Args:
            schedule (Schedule): The Schedule entity to create.

        Returns:
            Schedule: The created Schedule entity with updated fields.

        """
        self._save_and_refresh(schedule)
        return schedule

    def get_by_id(self, schedule_id: UUID) -> Schedule | None:
        """Retrieve a Schedule by its ID.

        Args:
            schedule_id (UUID): The ID of the Schedule to retrieve.

        Returns:
            Schedule | None: The Schedule entity if found, else None.

        """
        return self._session.get(Schedule, schedule_id)

    def get_by_job_id(self, job_id: str) -> Schedule | None:
        """Retrieve a Schedule by its job_id.

        Args:
            job_id (str): The job_id of the Schedule to retrieve.

        Returns:
            Schedule | None: The Schedule entity if found, else None.

        """
        statement = select(Schedule).where(Schedule.job_id == job_id)
        return self._session.exec(statement).first()

    def get_all(self) -> list[Schedule]:
        """Retrieve all Schedule entities from the database.

        Returns:
            list[Schedule]: A list of all Schedule entities.

        """
        return list(self._session.exec(select(Schedule)).all())

    def get_active(self) -> list[Schedule]:
        """Retrieve all active Schedule entities.

        Returns:
            list[Schedule]: A list of active Schedule entities.

        """
        statement = select(Schedule).where(Schedule.is_active == True)  # noqa: E712
        return list(self._session.exec(statement).all())

    def update(self, schedule: Schedule) -> Schedule | None:
        """Update an existing Schedule in the database.

        Args:
            schedule (Schedule): The Schedule entity to update.

        Returns:
            Schedule | None: The updated Schedule entity or None if not found.

        """
        existing = self.get_by_id(schedule.id)
        if existing is None:
            return None

        # Update fields
        existing.name = schedule.name
        existing.action = schedule.action
        existing.position_mm = schedule.position_mm
        existing.hour = schedule.hour
        existing.minute = schedule.minute
        existing.day_of_week = schedule.day_of_week
        existing.is_active = schedule.is_active
        existing.updated_at = datetime.utcnow()

        self._save_and_refresh(existing)
        return existing

    def delete(self, schedule_id: UUID) -> bool:
        """Delete a Schedule by its ID.

        Args:
            schedule_id (UUID): The ID of the Schedule to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """
        schedule = self.get_by_id(schedule_id)
        if schedule is None:
            return False

        self._session.delete(schedule)
        self._session.commit()
        return True

    def delete_by_job_id(self, job_id: str) -> bool:
        """Delete a Schedule by its job_id.

        Args:
            job_id (str): The job_id of the Schedule to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        """
        schedule = self.get_by_job_id(job_id)
        if schedule is None:
            return False

        self._session.delete(schedule)
        self._session.commit()
        return True

    def _save_and_refresh(self, instance: Schedule) -> None:
        """Save and refresh an instance in the database.

        Args:
            instance (Schedule): The Schedule instance to save and refresh.

        """
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)
