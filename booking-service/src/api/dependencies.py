"""Dependency injection module for FastAPI application."""

import logging
import os
from typing import Generator

from dotenv import load_dotenv
from fastapi.params import Depends
from sqlmodel import Session, create_engine

from src.messaging.messaging_manager import MessagingManager, messaging_manager
from src.repositories.booking_repository import DeskBookingRepository
from src.services.desk_booking_service import DeskBookingService

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


def get_booking_repository(
    session: Session = Depends(get_db_session),
) -> DeskBookingRepository:
    """Dependency injection for BookingRepository.

    Returns:
        DeskBookingRepository: An instance of BookingRepository.

    """
    return DeskBookingRepository(session)


def get_booking_service(
    repo: DeskBookingRepository = Depends(get_booking_repository),
    messaging: MessagingManager = Depends(lambda: messaging_manager),
) -> DeskBookingService:
    """Dependency injection for DeskBookingService.

    Args:
        repo (DeskBookingRepository): The booking repository instance.
        messaging (MessagingManager): The messaging manager instance.

    Returns:
        DeskBookingService: An instance of DeskBookingService.

    """
    return DeskBookingService(repo, messaging)
