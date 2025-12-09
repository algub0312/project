"""Dependency injection module for FastAPI application."""

import logging
import os
from typing import Generator

from dotenv import load_dotenv
from fastapi.params import Depends
from sqlmodel import Session, create_engine

from src.messaging.messaging_manager import MessagingManager, messaging_manager
from src.repositories.occupancy_repository import OccupancyRepository
from src.services.occupancy_service import OccupancyService

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set. Please set it in the environment variables.")
    raise ValueError("DATABASE_URL is not set.")

engine = create_engine(DATABASE_URL, echo=True)


def get_db_session() -> Generator[Session]:
    """Dependency injection for database session.

    Returns:
        Session: Yields a SQLModel Session instance.

    """
    with Session(engine) as session:
        yield session


def get_occupancy_repository(
    session: Session = Depends(get_db_session),
) -> OccupancyRepository:
    """Dependency injection for OccupancyRepository.

    Returns:
        OccupancyRepository: An instance of OccupancyRepository.

    """
    return OccupancyRepository(session)


def get_occupancy_service(
    repo: OccupancyRepository = Depends(get_occupancy_repository),
    messaging: MessagingManager = Depends(lambda: messaging_manager),
) -> OccupancyService:
    """Dependency injection for OccupancyService.

    Args:
        repo (OccupancyRepository): The occupancy repository instance.
        messaging (MessagingManager): The messaging manager instance.

    Returns:
        OccupancyService: An instance of OccupancyService.

    """
    return OccupancyService(repo, messaging)
