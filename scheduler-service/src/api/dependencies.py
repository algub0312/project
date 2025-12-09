"""Dependency injection module for FastAPI application."""

import logging
import os
from typing import Generator

from dotenv import load_dotenv
from fastapi.params import Depends
from sqlmodel import Session, create_engine

from src.repositories.desk_position_schedule_repository import (
    DeskPositionScheduleRepository,
)
from src.repositories.monitoring_job_repository import MonitoringJobRepository

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set. Please set it in the environment variables.")
    raise ValueError("DATABASE_URL is not set.")

# Get echo setting from environment
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)


def get_db_session() -> Generator[Session, None, None]:
    """Dependency injection for database session.

    Yields:
        Session: A SQLModel Session instance.

    """
    with Session(engine) as session:
        yield session


def get_monitoring_repository(
    session: Session = Depends(get_db_session),
) -> MonitoringJobRepository:
    """Dependency injection for MonitoringRepository.

    Args:
        session: Database session from dependency injection.

    Returns:
        MonitoringJobRepository: An instance of MonitoringRepository.

    """
    return MonitoringJobRepository(session)


def get_desk_position_schedule_repository(
    session: Session = Depends(get_db_session),
) -> DeskPositionScheduleRepository:
    """Dependency injection for ScheduleRepository.

    Args:
        session: Database session from dependency injection.

    Returns:
        DeskPositionScheduleRepository: An instance of ScheduleRepository.

    """
    return DeskPositionScheduleRepository(session)
