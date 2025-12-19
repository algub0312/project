"""Dependency injection module for FastAPI application."""

import logging
import os
from typing import Generator

from dotenv import load_dotenv
from fastapi.params import Depends
from sqlmodel import Session, create_engine

from src.repositories.desk_inventory_repository import DeskInventoryRepository
from src.services.desk_inventory_service import DeskInventoryService

logger = logging.getLogger(__name__)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL is not set.")
    raise ValueError("DATABASE_URL is not set.")

engine = create_engine(DATABASE_URL, echo=False)


def get_db_session() -> Generator[Session]:
    """Dependency injection for database session."""
    with Session(engine) as session:
        yield session


def get_desk_inventory_repository(
    session: Session = Depends(get_db_session),
) -> DeskInventoryRepository:
    """Dependency injection for DeskInventoryRepository."""
    return DeskInventoryRepository(session)


def get_desk_inventory_service(
    repo: DeskInventoryRepository = Depends(get_desk_inventory_repository),
) -> DeskInventoryService:
    """Dependency injection for DeskInventoryService."""
    return DeskInventoryService(repo)
