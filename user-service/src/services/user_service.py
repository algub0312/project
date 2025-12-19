from src.models.db.user import User
from src.models.dto.user_create_request import UserCreateRequest
from src.models.dto.user_dto import UserDTO
from src.models.dto.user_update_request import UserUpdateRequest
from src.repositories.user_repository import UserRepository


class UserService:
    """Service for managing users."""

    def __init__(self, repo: UserRepository) -> None:
        """Initialize the UserService."""
        self._repo = repo

    def create_user(self, request: UserCreateRequest) -> UserDTO:
        """Create a new user if it doesn't exist."""
        existing_user = self._repo.get_by_id(request.user_id)
        if existing_user is not None:
            raise ValueError("User already exists")

        user = User(
            user_id=request.user_id,
            preferred_standing_height_cm=request.preferred_standing_height_cm,
            preferred_sitting_height_cm=request.preferred_sitting_height_cm,
            user_height_cm=request.user_height_cm,
        )
        created = self._repo.create(user)
        return UserDTO(
            user_id=str(created.user_id),
            preferred_standing_height_cm=created.preferred_standing_height_cm,
            preferred_sitting_height_cm=created.preferred_sitting_height_cm,
            user_height_cm=created.user_height_cm,
        )

    def get_user(self, user_id: str) -> UserDTO | None:
        """Get a user by user_id."""
        user = self._repo.get_by_id(user_id)
        return (
            UserDTO(
                user_id=str(user.user_id),
                preferred_standing_height_cm=user.preferred_standing_height_cm,
                preferred_sitting_height_cm=user.preferred_sitting_height_cm,
                user_height_cm=user.user_height_cm,
            )
            if user
            else None
        )

    def update_preferences(
        self, user_id: str, request: UserUpdateRequest
    ) -> UserDTO | None:
        """Update user height preferences."""
        user = self._repo.get_by_id(user_id)
        if user is None:
            user = self._repo.create(User(user_id=user_id))

        if request.preferred_standing_height_cm is not None:
            user.preferred_standing_height_cm = request.preferred_standing_height_cm
        if request.preferred_sitting_height_cm is not None:
            user.preferred_sitting_height_cm = request.preferred_sitting_height_cm
        if request.user_height_cm is not None:
            user.user_height_cm = request.user_height_cm

        updated = self._repo.update(user)
        return UserDTO(
            user_id=str(updated.user_id),
            preferred_standing_height_cm=updated.preferred_standing_height_cm,
            preferred_sitting_height_cm=updated.preferred_sitting_height_cm,
            user_height_cm=updated.user_height_cm,
        )

    def list_users(self) -> list[UserDTO]:
        """List all users."""
        users = self._repo.get_all()
        return [
            UserDTO(
                user_id=str(user.user_id),
                preferred_standing_height_cm=user.preferred_standing_height_cm,
                preferred_sitting_height_cm=user.preferred_sitting_height_cm,
                user_height_cm=user.user_height_cm,
            )
            for user in users
        ]

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self._repo.delete(user_id)
