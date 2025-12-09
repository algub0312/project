"""Main application entry point for the Occupancy Service.

This sets up the FastAPI application, configures messaging, MQTT,
and includes API routes.
It also defines startup and shutdown procedures for the messaging
and MQTT managers.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from src.api.dependencies import engine, get_occupancy_repository
from src.api.routes.occupancy_routes import router as occupancy_router
from src.messaging.messaging_manager import messaging_manager
from src.messaging.pubsub_exchanges import DESK_OCCUPANCY_UPDATED
from src.messaging.pubsub_facade import PubSubFacade
from src.services.mqtt_service import mqtt_service
from src.services.occupancy_service import OccupancyService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv()
AMQP_URL = os.getenv("AMQP_URL")
if not AMQP_URL:
    logger.error("AMQP_URL is not set. Please set it in the environment variables.")
    raise ValueError("AMQP_URL is not set.")

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "occupancy/state")

messaging_manager.add_pubsub(PubSubFacade(AMQP_URL, DESK_OCCUPANCY_UPDATED))


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, Any]:
    """Manage the application lifespan.

    Handles startup and shutdown procedures for the messaging and MQTT managers.

    Args:
        _: The FastAPI application instance.

    Yields:
        None: Control returns during the application's active phase.

    """
    logger.info("Starting up occupancy service...")

    # Start messaging manager
    await messaging_manager.start_all()
    logger.debug("Messaging manager started.")

    with Session(engine) as session:
        repository = get_occupancy_repository(session)
        mqtt_occupancy_service = OccupancyService(repository, messaging_manager)

    mqtt_service.set_occupancy_service(mqtt_occupancy_service)

    # Start MQTT service
    mqtt_service.start(MQTT_HOST, MQTT_PORT, MQTT_TOPIC)
    logger.debug("MQTT service started and configured.")

    yield

    logger.info("Shutting down occupancy service...")

    # Stop MQTT service
    mqtt_service.stop()
    logger.debug("MQTT service stopped.")

    # Stop messaging manager
    await messaging_manager.stop_all()
    logger.info("Occupancy service shut down.")


app = FastAPI(
    title="Occupancy Service",
    description="Handles desk occupancy data from IoT devices",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://localhost:8080",  # Gateway
        "*",  # Allow all origins (for development)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✅ CORS middleware configured")


app.include_router(occupancy_router)


@app.get("/")
def get_root() -> dict:
    """Root endpoint providing basic service information.

    Returns:
        dict: A dictionary with service information.

    """
    return {"service": "Occupancy Service"}


@app.get("/health")
def get_health() -> dict:
    """Health check endpoint to verify service status.

    Returns:
        dict: A dictionary indicating service health status.

    """
    return {
        "status": "ok",
        "mqtt_connected": mqtt_service.is_connected,
        "mqtt_topic": MQTT_TOPIC,
    }
