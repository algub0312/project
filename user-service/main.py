"""Main application entry point for the Desk Booking Service.

This sets up the FastAPI application, configures messaging, and includes API routes.
It also defines startup and shutdown procedures for the messaging manager.
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from src.api.routes.user_routes import router as user_router

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


app = FastAPI()
app.include_router(user_router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information.

    Returns:
        dict: A dictionary with service information.

    """
    return {"service": "User Service"}


@app.get("/health")
def get_health() -> dict[str, str]:
    """Health check endpoint to verify service status.

    Returns:
        dict: A dictionary indicating service health status.

    """
    return {"status": "ok"}
