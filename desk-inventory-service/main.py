"""Main application entry point for the Desk Inventory Service."""

import src.logger_config  # noqa: F401, I001 initialize logging configuration
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.api.routers.desk_inventory_routes import router as inventory_router
from src.messaging.messaging_manager import messaging_manager
from src.messaging.pubsub_exchanges import DESK_DATA_UPDATED, DESK_INVENTORY_UPDATED
from src.messaging.pubsub_facade import PubSubFacade
from src.services.desk_fetch_service import run_desks_fetching

FETCHING_TIMEOUT_SECONDS = 20

logger = logging.getLogger(__name__)

load_dotenv()
AMQP_URL = os.getenv("AMQP_URL")
if not AMQP_URL:
    logger.error("AMQP_URL is not set.")
    raise ValueError("AMQP_URL is not set.")

# Set up messaging facades
messaging_manager.add_pubsub(PubSubFacade(AMQP_URL, DESK_DATA_UPDATED))
messaging_manager.add_pubsub(PubSubFacade(AMQP_URL, DESK_INVENTORY_UPDATED))

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=run_desks_fetching,
    trigger=IntervalTrigger(seconds=FETCHING_TIMEOUT_SECONDS),
    id="fetch_data_job",
    name=f"Fetch API data every {FETCHING_TIMEOUT_SECONDS} seconds",
    replace_existing=True,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    """Lifespan context manager to handle startup and shutdown events."""
    logger.info("Starting up messaging manager...")
    await messaging_manager.start_all()
    logger.info("Messaging manager started.")
    scheduler.start()
    logger.info("Scheduler started.")
    yield
    logger.info("Shutting down messaging manager...")
    await messaging_manager.stop_all()
    logger.info("Messaging manager shut down.")
    scheduler.shutdown()
    logger.info("Scheduler shut down.")


app = FastAPI(lifespan=lifespan)
app.include_router(inventory_router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information."""
    return {"service": "Desk Inventory Service"}


@app.get("/health")
def get_health() -> dict[str, str]:
    """Health check endpoint to verify service status."""
    return {"status": "ok"}
