from src.models.db.desk import Desk
from src.models.dto.desk_inventory_dto import DeskInventoryDTO
from src.models.dto.desk_inventory_update_request import DeskInventoryUpdateRequest
from src.repositories.desk_inventory_repository import (
    DeskInventoryRepository,
)


class DeskInventoryService:
    """Service for managing desk inventory."""

    def __init__(self, repo: DeskInventoryRepository) -> None:
        """Initialize the DeskInventoryService.

        Args:
            repo (DeskInventoryRepository): The repository for desk inventory.

        """
        self._repo = repo

    async def create_or_update_desk(
        self, request: DeskInventoryDTO
    ) -> DeskInventoryDTO:
        """Create or update a desk in inventory.

        Args:
            request (DeskInventoryDTO): The request containing desk details.

        Returns:
            DeskInventoryDTO: The created or updated desk data.

        """
        desk = Desk.from_dto(request)
        created_or_updated_desk = self._repo.create_or_update(desk)
        return DeskInventoryDTO.from_entity(created_or_updated_desk)

    async def get_desk(self, desk_id: int) -> DeskInventoryDTO | None:
        """Get a specific desk by its ID.

        Args:
            desk_id (int): The ID of the desk to retrieve.

        Returns:
            DeskInventoryDTO | None: The desk data if found, else None.

        """
        desk = self._repo.get_by_id(desk_id)
        return DeskInventoryDTO.from_entity(desk) if desk else None

    async def list_desks(self) -> list[DeskInventoryDTO]:
        """List all desks in inventory.

        Returns:
            list[DeskInventoryDTO]: A list of all desks.

        """
        desks = self._repo.get_all()
        return [DeskInventoryDTO.from_entity(desk) for desk in desks]

    async def update_desk(
        self, desk_id: int, update: DeskInventoryUpdateRequest
    ) -> DeskInventoryDTO | None:
        """Update an existing desk.

        Args:
            desk_id (int): The ID of the desk to update.
            update (DeskInventoryUpdateRequest): The update data.

        Returns:
            DeskInventoryDTO | None: The updated desk data if found,
                else None.

        """
        desk = self._repo.get_by_id(desk_id)
        if not desk:
            return None
        updated_desk = self._repo.update_desk(desk_id, update)
        return DeskInventoryDTO.from_entity(updated_desk)
