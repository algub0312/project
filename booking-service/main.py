"""Main application entry point for the Desk Booking Service.

This sets up the FastAPI application, configures messaging, and includes API routes.
It also defines startup and shutdown procedures for the messaging manager.
"""

import src.logger_config  # noqa: F401, I001 initialize logging configuration
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.routes.booking_routes import router as booking_router
from src.messaging.messaging_manager import messaging_manager
from src.messaging.pubsub_exchanges import (
    DESK_BOOKING_CREATED,
    DESK_BOOKING_DELETED,
    DESK_BOOKING_UPDATED,
)
from src.messaging.pubsub_facade import PubSubFacade

logger = logging.getLogger(__name__)

load_dotenv()
AMQP_URL = os.getenv("AMQP_URL")
if not AMQP_URL:
    logger.error("AMQP_URL is not set. Please set it in the environment variables.")
    raise ValueError("AMQP_URL is not set.")

messaging_manager.add_pubsubs(
    [
        PubSubFacade(AMQP_URL, DESK_BOOKING_CREATED),
        PubSubFacade(AMQP_URL, DESK_BOOKING_UPDATED),
        PubSubFacade(AMQP_URL, DESK_BOOKING_DELETED),
    ]
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    """Lifespan context manager to handle startup and shutdown events.

    Args:
        _: FastAPI: The FastAPI application instance.

    Returns:
        AsyncGenerator[None, Any]: Yields an async generator for lifespan management.

    """
    logger.info("Starting up messaging manager...")
    await messaging_manager.start_all()
    logger.debug("Messaging manager started.")
    yield
    logger.info("Shutting down messaging manager...")
    await messaging_manager.stop_all()
    logger.info("Messaging manager shut down.")


app = FastAPI(lifespan=lifespan)
app.include_router(booking_router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information.

    Returns:
        dict: A dictionary with service information.

    """
    return {"service": "Desk Booking Service"}


@app.get("/health")
def get_health() -> dict[str, str]:
    """Health check endpoint to verify service status.

    Returns:
        dict: A dictionary indicating service health status.

    """
    return {"status": "ok"}
