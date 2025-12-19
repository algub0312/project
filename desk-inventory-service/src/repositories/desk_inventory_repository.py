from dataclasses import dataclass
from datetime import UTC, datetime

from sqlmodel import Session, select

from src.models.db.desk import Desk
from src.models.dto.desk_inventory_update_request import DeskInventoryUpdateRequest


@dataclass
class DeskStateParams:
    """Parameters for creating or updating desk state."""

    desk_id: int
    position_mm: int | None = None
    speed_mms: int | None = None
    status: str | None = None
    is_position_lost: bool = False
    is_overload_protection_up: bool = False
    is_overload_protection_down: bool = False
    is_anti_collision: bool = False


class DeskInventoryRepository:
    """Repository for managing Desk entities in the database."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self._session = session

    def create_or_update(self, desk: Desk) -> Desk:
        """Create or update a Desk in the database.

        Args:
            desk (Desk): The Desk entity to create or update.

        Returns:
            Desk: The created or updated Desk entity with updated fields.

        """
        desk.updated_at = datetime.now(UTC)
        merged_desk = self._session.merge(desk)
        self._session.commit()
        self._session.refresh(merged_desk)
        return merged_desk

    def get_by_id(self, desk_id: int) -> Desk | None:
        """Retrieve a Desk by its ID with all relationships loaded.

        Args:
            desk_id (int): The ID of the Desk to retrieve.

        Returns:
            Desk | None: The Desk entity if found, else None.

        """
        statement = select(Desk).where(Desk.id == desk_id)
        desk = self._session.exec(statement).first()
        return desk

    def get_all(self) -> list[Desk]:
        """Retrieve all Desk entities from the database.

        Returns:
            list[Desk]: A list of all Desk entities.

        """
        return list(self._session.exec(select(Desk)).all())

    def update_desk(self, desk_id: int, update: DeskInventoryUpdateRequest) -> Desk:
        """Update an existing Desk in the database.

        Args:
            desk_id(int): The ID of the Desk to update.
            update (Desk): The Desk entity to update.

        Returns:
            Desk: The updated Desk entity.

        """
        desk = self.get_by_id(desk_id)
        desk.orientation = update.orientation
        desk.pos_x = update.pos_x
        desk.pos_y = update.pos_y
        desk.updated_at = datetime.now(UTC)
        self._save_and_refresh(desk)
        return desk

    def _save_and_refresh(self, instance: Desk) -> None:
        """Save and refresh an instance in the database.

        Args:
            instance: The instance to save and refresh.

        """
        self._session.add(instance)
        self._session.commit()
        self._session.refresh(instance)
