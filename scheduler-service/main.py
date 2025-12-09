import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.logger_config  # noqa: F401, I001 initialize logging configuration
from src.api.dependencies import (
    get_db_session,
    get_monitoring_repository,
)
from src.messaging.booking_message_handler import BookingMessageHandler
from src.messaging.direct_exchanges import DESK_MONITORING
from src.messaging.direct_message_facade import DirectMessageFacade
from src.messaging.messaging_manager import MessagingManager
from src.messaging.pubsub_exchanges import (
    DESK_BOOKING_CREATED,
    DESK_BOOKING_DELETED,
    DESK_BOOKING_UPDATED,
)
from src.messaging.pubsub_facade import PubSubFacade
from src.routers import scheduler as scheduler_router
from src.services.monitoring.monitoring_scheduler_manager import (
    MonitoringSchedulerManager,
)
from src.services.monitoring.monitoring_scheduler_service import (
    MonitoringSchedulerService,
)
from src.services.position.desk_position_scheduler_service import scheduler_service

logger = logging.getLogger(__name__)

load_dotenv()
AMQP_URL = os.getenv("AMQP_URL")
if not AMQP_URL:
    logger.error("AMQP_URL is not set. Please set it in the environment variables.")
    raise ValueError("AMQP_URL is not set.")

messaging_manager = MessagingManager.get_instance()
messaging_manager.add_pubsubs(
    [
        PubSubFacade(AMQP_URL, DESK_BOOKING_CREATED),
        PubSubFacade(AMQP_URL, DESK_BOOKING_UPDATED),
        PubSubFacade(AMQP_URL, DESK_BOOKING_DELETED),
    ]
)
messaging_manager.add_direct(DirectMessageFacade(AMQP_URL, DESK_MONITORING))

monitoring_scheduler_service = MonitoringSchedulerService(
    repo=get_monitoring_repository(next(get_db_session())),
    manager=MonitoringSchedulerManager.get_instance(),
    messaging=messaging_manager,
)

booking_message_handler = BookingMessageHandler(
    repo=get_monitoring_repository(next(get_db_session())),
    manager=MonitoringSchedulerManager.get_instance(),
    messaging=messaging_manager,
)


# ----------------------------
# Lifespan (startup / shutdown)
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 60)

    await activate_monitoring()

    try:
        if (
            hasattr(scheduler_service, "is_running")
            and not scheduler_service.is_running()
            and hasattr(scheduler_service, "start")
        ):
            logger.info("Starting desk position scheduler service...")
            scheduler_service.start()

        # Load schedules from database
        logger.info("Loading desk position schedules from database...")
        db_session = next(get_db_session())
        try:
            scheduler_service.load_schedules_from_db(db_session)
        finally:
            db_session.close()

        # Check if any schedules were loaded
        jobs = scheduler_service.get_all_jobs()
        logger.info("Total jobs after database load: %d", len(jobs))

        # If no schedules exist, create defaults
        if len(jobs) == 0:
            logger.info("No schedules found in database. Creating defaults...")
            db_session = next(get_db_session())
            try:
                scheduler_service.setup_default_schedules(db_session)
            finally:
                db_session.close()

            # Verify defaults were created
            jobs = scheduler_service.get_all_jobs()
            logger.info("Total jobs after creating defaults: %d", len(jobs))

        # Log all schedules
        if jobs:
            logger.info("Active schedules:")
            for job in jobs:
                jid = job.get("id") or job.get("job_id")
                jname = job.get("name") or job.get("job_name") or "<unnamed>"
                next_run = job.get("next_run") or "not scheduled"
                logger.info("  ✓ %s: %s (next: %s)", jid, jname, next_run)
        else:
            logger.warning("No jobs were created!")

    except Exception as e:
        logger.exception("ERROR during startup: %s", e)

    # Yield to serve requests
    yield

    # Shutdown
    logger.info("=" * 60)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 60)

    await stop_monitoring()

    try:
        if hasattr(scheduler_service, "shutdown"):
            scheduler_service.shutdown()
    except Exception as e:  # noqa: BLE001
        logger.exception("Error during shutdown: %s", e)


async def activate_monitoring() -> None:
    """Activate monitoring."""
    await messaging_manager.start_all()
    logger.info("Messaging manager started.")
    booking_message_handler.start()
    logger.info("Booking message handler started. Listening to incoming messages")
    monitoring_scheduler_service.start()
    logger.info("Monitoring scheduler service started.")


async def stop_monitoring() -> None:
    """Deactivate monitoring."""
    monitoring_scheduler_service.stop()
    logger.info("Monitoring scheduler service stopped.")
    await messaging_manager.stop_all()
    logger.info("Messaging manager stopped.")


# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI(
    title="Desk Scheduler Service",
    version="1.1.0",
    lifespan=lifespan,
)

# CORS (tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(scheduler_router.router)


# ----------------------------
# Debug / Utility endpoints
# ----------------------------
@app.get("/")
def get_root() -> dict[str, str]:
    """Health endpoint for the Scheduler Service."""
    return {
        "service": "Desk Scheduler Service",
        "status": "running",
        "version": "1.1.0",
    }


@app.get("/debug/setup")
def debug_setup() -> dict[str, object]:
    """Manually trigger default schedule setup."""
    try:
        db_session = next(get_db_session())
        try:
            scheduler_service.setup_default_schedules(db_session)
        finally:
            db_session.close()

        jobs = scheduler_service.get_all_jobs()
        return {
            "status": "success",
            "message": f"Setup called, {len(jobs)} jobs exist",
            "jobs": jobs,
        }
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "message": str(e)}


@app.get("/debug/jobs")
def debug_jobs() -> dict[str, object]:
    """Inspect current jobs."""
    jobs = scheduler_service.get_all_jobs()
    running = getattr(scheduler_service, "is_running", lambda: None)()
    return {
        "scheduler_running": running,
        "jobs_count": len(jobs),
        "jobs": jobs,
    }
