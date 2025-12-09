import logging
from typing import Any, Dict, List

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session

from src.models.db.schedule import Schedule as DBSchedule
from src.repositories.desk_position_schedule_repository import (
    DeskPositionScheduleRepository,
)
from src.services.desk_service import DeskService

logger = logging.getLogger(__name__)


class DeskPositionSchedulerService:
    """Service for managing scheduled desk operations with database persistence."""

    def __init__(self) -> None:
        # In-memory scheduler
        self.scheduler = BackgroundScheduler()
        logger.info("Scheduler service initialized (not started yet)")

    # -------- lifecycle --------
    def start(self) -> None:
        """Start the scheduler if not already running."""
        if self.scheduler.state != STATE_RUNNING:
            self.scheduler.start()
            logger.info("Scheduler started")
        else:
            logger.info("Scheduler already running; start() skipped")

    def shutdown(self) -> None:
        """Shutdown the scheduler if running."""
        if self.scheduler.state == STATE_RUNNING:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler service shut down")
        else:
            logger.info("Scheduler not running; shutdown() skipped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.scheduler.state == STATE_RUNNING

    # -------- info --------
    def get_jobs_count(self) -> int:
        """Get the number of scheduled jobs."""
        return len(self.scheduler.get_jobs())

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat()
                if job.next_run_time
                else None,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]

    # -------- database operations --------
    def load_schedules_from_db(self, session: Session) -> None:
        """Load all active schedules from the database.

        Args:
            session: Database session for querying schedules.

        """
        logger.info("Loading schedules from database...")
        repo = DeskPositionScheduleRepository(session)
        schedules = repo.get_active()

        loaded_count = 0
        for schedule in schedules:
            try:
                self._add_schedule_to_apscheduler(
                    job_id=schedule.job_id,
                    name=schedule.name,
                    position_mm=schedule.position_mm,
                    hour=schedule.hour,
                    minute=schedule.minute,
                    day_of_week=schedule.day_of_week,
                )
                loaded_count += 1
                logger.info("✓ Loaded schedule from DB: %s", schedule.job_id)
            except Exception as e:
                logger.error("✗ Failed to load schedule %s: %s", schedule.job_id, e)

        logger.info(
            "Loaded %s/%s schedules from database", loaded_count, len(schedules)
        )

    def _save_schedule_to_db(  # noqa: PLR0913
        self,
        session: Session,
        job_id: str,
        name: str,
        position_mm: int,
        hour: int,
        minute: int,
        day_of_week: str,
    ) -> DBSchedule:
        """Save or update a schedule in the database.

        Args:
            session: Database session.
            job_id: Unique job identifier.
            name: Schedule name.
            position_mm: Target position in millimeters.
            hour: Hour to execute (0-23).
            minute: Minute to execute (0-59).
            day_of_week: Days to run.

        Returns:
            DBSchedule: The saved schedule entity.

        """
        repo = DeskPositionScheduleRepository(session)
        existing = repo.get_by_job_id(job_id)

        if existing:
            # Update existing
            existing.name = name
            existing.position_mm = position_mm
            existing.hour = hour
            existing.minute = minute
            existing.day_of_week = day_of_week
            existing.is_active = True
            updated = repo.update(existing)
            logger.info("Updated schedule in database: %s", job_id)
            return updated
        else:
            # Create new
            db_schedule = DBSchedule(
                job_id=job_id,
                name=name,
                position_mm=position_mm,
                hour=hour,
                minute=minute,
                day_of_week=day_of_week,
                is_active=True,
            )
            created = repo.create(db_schedule)
            logger.info("Created schedule in database: %s", job_id)
            return created

    def _delete_schedule_from_db(self, session: Session, job_id: str) -> bool:
        """Delete a schedule from the database.

        Args:
            session: Database session.
            job_id: Job identifier to delete.

        Returns:
            bool: True if deleted, False if not found.

        """
        repo = DeskPositionScheduleRepository(session)
        deleted = repo.delete_by_job_id(job_id)
        if deleted:
            logger.info("Deleted schedule from database: %s", job_id)
        return deleted

    # -------- actions --------
    def add_schedule(  # noqa: PLR0913
        self,
        job_id: str,
        name: str,
        position_mm: int,
        hour: int,
        minute: int,
        day_of_week: str = "*",
        session: Session | None = None,
    ) -> Dict[str, Any]:
        """Add a new scheduled job and persist to database.

        Args:
            job_id: Unique job identifier.
            name: Human-readable name.
            position_mm: Target position in millimeters.
            hour: Hour to execute (0-23).
            minute: Minute to execute (0-59).
            day_of_week: Days to run (e.g., '*', 'mon-fri').
            session: Optional database session for persistence.

        Returns:
            Dict containing job_id and next_run time.

        """
        if not isinstance(position_mm, int) or position_mm <= 0:
            raise ValueError("position_mm must be a positive integer (millimeters).")

        # Add to APScheduler
        job = self._add_schedule_to_apscheduler(
            job_id=job_id,
            name=name,
            position_mm=position_mm,
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
        )

        # Save to database if session provided
        if session:
            try:
                self._save_schedule_to_db(
                    session=session,
                    job_id=job_id,
                    name=name,
                    position_mm=position_mm,
                    hour=hour,
                    minute=minute,
                    day_of_week=day_of_week,
                )
            except Exception as e:
                logger.error("Failed to persist schedule to database: %s", e)
                # Don't fail the whole operation if DB save fails
                # The schedule is still in APScheduler

        return {
            "job_id": job.id,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
        }

    def _add_schedule_to_apscheduler(  # noqa: PLR0913
        self,
        job_id: str,
        name: str,
        position_mm: int,
        hour: int,
        minute: int,
        day_of_week: str,
    ) -> Job:
        """Add a schedule to APScheduler only (no database).

        Args:
            job_id: Unique job identifier.
            name: Schedule name.
            position_mm: Target position.
            hour: Hour to execute.
            minute: Minute to execute.
            day_of_week: Days to run.

        Returns:
            APScheduler Job object.

        """

        def _job_func() -> None:
            context = {
                "trigger": "schedule",
                "job_id": job_id,
                "job_name": name,
            }

            # Always use raise_all_desks (or use position to determine action)
            # Since we removed "action", we'll always raise to the specified position
            DeskService.raise_all_desks(position_mm, context=context)

        # Build cron trigger
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            day_of_week=day_of_week,
        )

        # Add (or replace) job
        job = self.scheduler.add_job(
            _job_func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        logger.info(
            "Added/updated schedule in APScheduler: id=%s name=%s "
            "pos=%smm cron=%s next=%s",
            job.id,
            name,
            position_mm,
            str(trigger),
            job.next_run_time.isoformat() if job.next_run_time else None,
        )

        return job

    def remove_schedule(self, job_id: str, session: Session | None = None) -> None:
        """Remove a scheduled job from APScheduler and database.

        Args:
            job_id: Job identifier to remove.
            session: Optional database session for deletion.

        """
        # Remove from APScheduler
        try:
            self.scheduler.remove_job(job_id)
            logger.info("Removed schedule from APScheduler: %s", job_id)
        except Exception as e:
            logger.warning("Failed to remove job from APScheduler: %s", e)

        # Remove from database if session provided
        if session:
            try:
                self._delete_schedule_from_db(session, job_id)
            except Exception as e:
                logger.error("Failed to delete schedule from database: %s", e)

    # -------- defaults --------
    def setup_default_schedules(self, session: Session | None = None) -> None:
        """Set up default schedules (idempotent via replace_existing=True).

        Args:
            session: Optional database session for persistence.

        """
        logger.info("Setting up default schedules...")
        try:
            # Cleaning mode: raise desks at 20:00 every day
            self.add_schedule(
                job_id="cleaning_start",
                name="Start Cleaning Mode",
                position_mm=1200,
                hour=20,
                minute=0,
                day_of_week="*",
                session=session,
            )

            # End cleaning mode: lower desks at 21:00 every day
            self.add_schedule(
                job_id="cleaning_end",
                name="End Cleaning Mode",
                position_mm=680,
                hour=21,
                minute=0,
                day_of_week="*",
                session=session,
            )

            # Morning standup on weekdays
            self.add_schedule(
                job_id="morning_standup",
                name="Morning Standup",
                position_mm=1100,
                hour=9,
                minute=0,
                day_of_week="mon-fri",
                session=session,
            )

            logger.info("✓ Default schedules initialized")
        except Exception as e:
            logger.exception("Error setting up default schedules: %s", e)


# Global scheduler instance
scheduler_service = DeskPositionSchedulerService()
