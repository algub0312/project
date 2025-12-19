import logging
import os
from typing import Generator

from dotenv import load_dotenv
from fastapi.params import Depends
from sqlmodel import Session, create_engine

from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set.")
    raise ValueError("DATABASE_URL is not set.")

engine = create_engine(DATABASE_URL, echo=True)


def get_db_session() -> Generator[Session]:
    """Dependency injection for database session."""
    with Session(engine) as session:
        yield session


def get_user_repository(
    session: Session = Depends(get_db_session),
) -> UserRepository:
    """Dependency injection for UserRepository."""
    return UserRepository(session)


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Dependency injection for UserService."""
    return UserService(repo)
