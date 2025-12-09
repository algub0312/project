import logging
from typing import Annotated, Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.api.dependencies import get_db_session
from src.models.scheduler import (
    DeskActionResult,
    DeskPositionRequest,
    HealthResponse,
    Schedule,
    ScheduleCreate,
    ScheduleResponse,
)
from src.services.desk_service import DeskService
from src.services.position.desk_position_scheduler_service import scheduler_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scheduler/api/v1", tags=["scheduler"])


@router.get("/health")
def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        running = scheduler_service.is_running()
        jobs_count = scheduler_service.get_jobs_count()
    except Exception as e:
        logger.exception("Health check failure: %s", e)
        return HealthResponse(status="degraded", scheduler_running=False, jobs_count=0)

    return HealthResponse(
        status="healthy", scheduler_running=running, jobs_count=jobs_count
    )


@router.get("/schedules")
def get_schedules() -> List[Schedule]:
    """Get all scheduled jobs."""
    try:
        jobs = scheduler_service.get_all_jobs()
        return jobs
    except Exception as e:
        logger.exception("Error fetching schedules: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch schedules") from e


@router.post("/schedules", status_code=201)
def create_schedule(
    schedule: ScheduleCreate,
    session: Annotated[Session, Depends(get_db_session)],
) -> ScheduleResponse:
    """Create a new schedule and persist to database.

    Example body:
    {
        "name": "Morning desk setup",
        "position_mm": 1000,
        "cron": {"hour": 8, "minute": 0, "day_of_week": "mon-fri"},
        "id": "morning_raise"
    }
    """
    try:
        job_id = schedule.id or schedule.name.lower().replace(" ", "_")

        # Add to scheduler and save to database (action removed)
        result = scheduler_service.add_schedule(
            job_id=job_id,
            name=schedule.name,
            position_mm=schedule.position_mm,
            hour=schedule.cron.hour,
            minute=schedule.cron.minute,
            day_of_week=schedule.cron.day_of_week,
            session=session,  # Pass session for DB persistence
        )

        return ScheduleResponse(
            message="Schedule created successfully",
            job_id=result["job_id"],
            next_run=result.get("next_run"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Error creating schedule: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create schedule") from e


@router.delete("/schedules/{job_id}")
def delete_schedule(
    job_id: str,
    session: Annotated[Session, Depends(get_db_session)],
) -> dict[str, str]:
    """Delete a scheduled job from APScheduler and database."""
    try:
        # Remove from scheduler and database
        scheduler_service.remove_schedule(job_id, session=session)
        return {"message": f"Schedule {job_id} deleted successfully"}
    except KeyError as e:
        detail = f"Schedule {job_id} not found"
        raise HTTPException(status_code=404, detail=detail) from e
    except Exception as e:
        logger.exception("Error deleting schedule %s: %s", job_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete schedule") from e


@router.post("/desks/position")
def set_position(request: DeskPositionRequest) -> List[DeskActionResult]:
    """Set all desks to a specific height (in millimeters)."""
    try:
        # Prefer unified service method if present; otherwise fall back.
        if hasattr(DeskService, "set_all_desks_position"):
            return DeskService.set_all_desks_position(
                request.position_mm,
                context={"trigger": "manual", "endpoint": "position"},
            )
        return DeskService.raise_all_desks(
            request.position_mm,
            context={"trigger": "manual", "endpoint": "position"},
        )
    except Exception as e:
        logger.exception("Set position error: %s", e)
        raise HTTPException(
            status_code=500, detail="Failed to set desk position"
        ) from e


@router.get("/desks")
def get_desks() -> List[dict[str, Any]]:
    """Get all desks and their current status."""
    try:
        desk_ids = DeskService.get_all_desks()
        desks_info: List[dict[str, Any]] = []
        for desk_id in desk_ids:
            state = DeskService.get_desk_state(desk_id)
            if state:
                desks_info.append({"id": desk_id, "state": state})
        return desks_info
    except Exception as e:
        logger.exception("Error fetching desks: %s", e)
        raise HTTPException(status_code=500, detail="Failed to fetch desks") from e
