import src.logger_config  # noqa: F401, I001 initialize logging configuration
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.desk_integration import router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control flow for startup and shutdown phases.

    """
    # Startup: Initialize RabbitMQ publisher
    logger.info("=" * 60)
    logger.info("Starting Desk Integration Service...")
    logger.info("=" * 60)

    yield

    # Shutdown: Clean up messaging
    logger.info("=" * 60)
    logger.info("Shutting down Desk Integration Service...")
    logger.info("=" * 60)


app = FastAPI(
    title="Desk Integration Service",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def get_root() -> dict[str, str]:
    """Root endpoint providing basic service information."""
    return {
        "service": "Desk Integration Service",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
