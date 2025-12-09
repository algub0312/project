from datetime import datetime, timedelta, timezone
from typing import Any, Generator
from uuid import uuid4

import pytest
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine, delete
from testcontainers.postgres import PostgresContainer

from src.models.db.monitoring_job import JobStatus, MonitoringJob
from src.models.msg.booking_message import BookingMessage
from src.repositories.monitoring_job_repository import MonitoringJobRepository

EXPECTED_JOBS_LENGTH = 2

TEST_DESK_ID = 999


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime to UTC timezone for comparison.

    PostgreSQL may strip timezone info, so we ensure both datetimes
    have UTC timezone for accurate comparison.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@pytest.fixture(scope="module")
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    """Create and start a PostgreSQL test container."""
    with PostgresContainer("postgres:17-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def engine(postgres_container: PostgresContainer) -> Generator[Engine, None, None]:
    """Create a SQLModel engine connected to the test database."""
    connection_url = postgres_container.get_connection_url()
    engine = create_engine(connection_url, echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    with Session(engine) as session:
        yield session
        # Clean up all jobs after each test to ensure isolation
        session.exec(delete(MonitoringJob))
        session.commit()


@pytest.fixture
def repository(session: Session) -> MonitoringJobRepository:
    """Create a MonitoringJobRepository instance."""
    return MonitoringJobRepository(session)


@pytest.fixture
def sample_booking_message() -> BookingMessage:
    """Create a sample BookingMessage for testing."""
    return BookingMessage(
        booking_id=uuid4(),
        desk_id=101,
        start_time=datetime.now(timezone.utc) + timedelta(hours=2),
    )


@pytest.fixture
def sample_job() -> MonitoringJob:
    """Create a sample MonitoringJob for testing."""
    return MonitoringJob(
        booking_id=uuid4(),
        desk_id=101,
        scheduled_time=datetime.now(timezone.utc) + timedelta(hours=2),
        status=JobStatus.PENDING,
    )


class TestMonitoringJobRepositoryCreate:
    """Tests for the create operation."""

    def test_create_job_success(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test successfully creating a new monitoring job."""
        created_job = repository.create(sample_job)

        assert created_job.job_id is not None
        assert created_job.booking_id == sample_job.booking_id
        assert created_job.desk_id == sample_job.desk_id
        assert created_job.status == JobStatus.PENDING
        assert created_job.created_at is not None
        assert created_job.updated_at is not None

    def test_create_job_persists_to_database(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test that created job is actually persisted to the database."""
        created_job = repository.create(sample_job)

        retrieved_job = repository.get_by_id(created_job.job_id)
        assert retrieved_job is not None
        assert retrieved_job.job_id == created_job.job_id
        assert retrieved_job.booking_id == created_job.booking_id

    def test_create_multiple_jobs(self, repository: MonitoringJobRepository) -> None:
        """Test creating multiple jobs with different booking IDs."""
        job1 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=101,
            scheduled_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        job2 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=102,
            scheduled_time=datetime.now(timezone.utc) + timedelta(hours=2),
        )

        created_job1 = repository.create(job1)
        created_job2 = repository.create(job2)

        assert created_job1.job_id != created_job2.job_id
        assert created_job1.booking_id != created_job2.booking_id


class TestMonitoringJobRepositoryUpdate:
    """Tests for the update operation."""

    def test_update_existing_job(
        self,
        repository: MonitoringJobRepository,
        sample_job: MonitoringJob,
        sample_booking_message: BookingMessage,
    ) -> None:
        """Test updating an existing monitoring job."""
        created_job = repository.create(sample_job)

        # Update with new values
        sample_booking_message.booking_id = created_job.booking_id
        sample_booking_message.desk_id = TEST_DESK_ID
        sample_booking_message.start_time = datetime.now(timezone.utc) + timedelta(
            hours=5
        )

        updated_job = repository.update(sample_booking_message)

        assert updated_job is not None
        assert updated_job.job_id == created_job.job_id
        assert updated_job.desk_id == TEST_DESK_ID
        assert normalize_datetime(updated_job.scheduled_time) == normalize_datetime(
            sample_booking_message.start_time
        )

    def test_update_nonexistent_job(
        self,
        repository: MonitoringJobRepository,
        sample_booking_message: BookingMessage,
    ) -> None:
        """Test updating a job that doesn't exist returns None."""
        sample_booking_message.booking_id = uuid4()  # Non-existent booking ID

        result = repository.update(sample_booking_message)

        assert result is None

    def test_update_preserves_status(
        self,
        repository: MonitoringJobRepository,
        sample_job: MonitoringJob,
        sample_booking_message: BookingMessage,
    ) -> None:
        """Test that update preserves the job status."""
        created_job = repository.create(sample_job)
        repository.mark_scheduled(created_job)

        sample_booking_message.booking_id = created_job.booking_id
        sample_booking_message.desk_id = TEST_DESK_ID

        updated_job = repository.update(sample_booking_message)

        assert updated_job.status == JobStatus.SCHEDULED
        assert updated_job.desk_id == TEST_DESK_ID


class TestMonitoringJobRepositoryGet:
    """Tests for get operations."""

    def test_get_by_id_success(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test retrieving a job by its ID."""
        created_job = repository.create(sample_job)

        retrieved_job = repository.get_by_id(created_job.job_id)

        assert retrieved_job is not None
        assert retrieved_job.job_id == created_job.job_id

    def test_get_by_id_nonexistent(self, repository: MonitoringJobRepository) -> None:
        """Test retrieving a non-existent job returns None."""
        result = repository.get_by_id(uuid4())

        assert result is None

    def test_get_job_by_booking_id_success(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test retrieving a job by its booking ID."""
        created_job = repository.create(sample_job)

        retrieved_job = repository.get_job_by_booking_id(created_job.booking_id)

        assert retrieved_job is not None
        assert retrieved_job.booking_id == created_job.booking_id

    def test_get_job_by_booking_id_nonexistent(
        self, repository: MonitoringJobRepository
    ) -> None:
        """Test retrieving by non-existent booking ID returns None."""
        result = repository.get_job_by_booking_id(uuid4())

        assert result is None


class TestMonitoringJobRepositoryGetJobsInWindow:
    """Tests for get_jobs_in_window operation."""

    def test_get_jobs_in_window(self, repository: MonitoringJobRepository) -> None:
        """Test retrieving jobs within a specific time window."""
        now = datetime.now(timezone.utc)

        # Create jobs at different times
        job1 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=101,
            scheduled_time=now + timedelta(hours=1),
            status=JobStatus.PENDING,
        )
        job2 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=102,
            scheduled_time=now + timedelta(hours=3),
            status=JobStatus.PENDING,
        )
        job3 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=103,
            scheduled_time=now + timedelta(hours=10),
            status=JobStatus.PENDING,
        )

        repository.create(job1)
        repository.create(job2)
        repository.create(job3)

        # Query for jobs between 30 minutes and 5 hours from now
        start_time = now + timedelta(minutes=30)
        end_time = now + timedelta(hours=5)

        jobs = repository.get_jobs_in_window(start_time, end_time, JobStatus.PENDING)

        assert len(jobs) == EXPECTED_JOBS_LENGTH
        assert all(job.status == JobStatus.PENDING for job in jobs)

    def test_get_jobs_in_window_filters_by_status(
        self, repository: MonitoringJobRepository
    ) -> None:
        """Test that get_jobs_in_window filters by status correctly."""
        now = datetime.now(timezone.utc)

        job1 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=101,
            scheduled_time=now + timedelta(hours=1),
            status=JobStatus.PENDING,
        )
        job2 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=102,
            scheduled_time=now + timedelta(hours=2),
            status=JobStatus.SCHEDULED,
        )

        repository.create(job1)
        repository.create(job2)

        start_time = now
        end_time = now + timedelta(hours=5)

        pending_jobs = repository.get_jobs_in_window(
            start_time, end_time, JobStatus.PENDING
        )
        scheduled_jobs = repository.get_jobs_in_window(
            start_time, end_time, JobStatus.SCHEDULED
        )

        assert len(pending_jobs) == 1
        assert len(scheduled_jobs) == 1

    def test_get_jobs_in_window_empty_result(
        self, repository: MonitoringJobRepository
    ) -> None:
        """Test that empty window returns empty list."""
        now = datetime.now(timezone.utc)
        start_time = now + timedelta(hours=100)
        end_time = now + timedelta(hours=200)

        jobs = repository.get_jobs_in_window(start_time, end_time, JobStatus.PENDING)

        assert jobs == []


class TestMonitoringJobRepositoryGetJobsToPromote:
    """Tests for get_jobs_to_promote operation."""

    def test_get_jobs_to_promote(self, repository: MonitoringJobRepository) -> None:
        """Test retrieving jobs that are due for promotion."""
        now = datetime.now(timezone.utc)

        # Job in the past (should not be returned - before now)
        job1 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=101,
            scheduled_time=now - timedelta(hours=1),
            status=JobStatus.PENDING,
        )

        # Job due soon (should be returned)
        job2 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=102,
            scheduled_time=now + timedelta(minutes=30),
            status=JobStatus.PENDING,
        )

        # Job far in the future (should not be returned)
        job3 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=103,
            scheduled_time=now + timedelta(hours=10),
            status=JobStatus.PENDING,
        )

        # Job already scheduled (should not be returned)
        job4 = MonitoringJob(
            booking_id=uuid4(),
            desk_id=104,
            scheduled_time=now + timedelta(minutes=45),
            status=JobStatus.SCHEDULED,
        )

        repository.create(job1)
        repository.create(job2)
        repository.create(job3)
        repository.create(job4)

        cutoff_time = now + timedelta(hours=1)
        jobs_to_promote = repository.get_jobs_to_promote(cutoff_time)

        assert len(jobs_to_promote) == 1
        assert jobs_to_promote[0].booking_id == job2.booking_id


class TestMonitoringJobRepositoryDelete:
    """Tests for delete operations."""

    def test_delete_by_booking_id_success(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test deleting a job by its booking ID."""
        created_job = repository.create(sample_job)

        deleted_job = repository.delete_by_booking_id(created_job.booking_id)

        assert deleted_job is not None
        assert deleted_job.booking_id == created_job.booking_id

        # Verify deletion
        result = repository.get_job_by_booking_id(created_job.booking_id)
        assert result is None

    def test_delete_by_booking_id_nonexistent(
        self, repository: MonitoringJobRepository
    ) -> None:
        """Test deleting a non-existent job returns None."""
        result = repository.delete_by_booking_id(uuid4())

        assert result is None


class TestMonitoringJobRepositoryStatusUpdates:
    """Tests for status update operations."""

    def test_mark_scheduled(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test marking a job as scheduled."""
        created_job = repository.create(sample_job)

        repository.mark_scheduled(created_job)

        updated_job = repository.get_by_id(created_job.job_id)
        assert updated_job.status == JobStatus.SCHEDULED

    def test_mark_executing(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test marking a job as executing."""
        created_job = repository.create(sample_job)

        repository.mark_executing(created_job)

        updated_job = repository.get_by_id(created_job.job_id)
        assert updated_job.status == JobStatus.EXECUTING

    def test_mark_completed(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test marking a job as completed."""
        created_job = repository.create(sample_job)

        repository.mark_completed(created_job)

        updated_job = repository.get_by_id(created_job.job_id)
        assert updated_job.status == JobStatus.COMPLETED

    def test_mark_failed(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test marking a job as failed."""
        created_job = repository.create(sample_job)

        repository.mark_failed(created_job)

        updated_job = repository.get_by_id(created_job.job_id)
        assert updated_job.status == JobStatus.FAILED

    def test_status_transition_workflow(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test a complete status transition workflow."""
        created_job = repository.create(sample_job)
        assert created_job.status == JobStatus.PENDING

        repository.mark_scheduled(created_job)
        job = repository.get_by_id(created_job.job_id)
        assert job.status == JobStatus.SCHEDULED

        repository.mark_executing(job)
        job = repository.get_by_id(created_job.job_id)
        assert job.status == JobStatus.EXECUTING

        repository.mark_completed(job)
        job = repository.get_by_id(created_job.job_id)
        assert job.status == JobStatus.COMPLETED


class TestMonitoringJobRepositoryCleanup:
    """Tests for cleanup operations."""

    def test_cleanup_old_jobs(self, repository: MonitoringJobRepository) -> None:
        """Test cleaning up old jobs."""
        now = datetime.now(timezone.utc)

        # Old job (should be deleted)
        old_job = MonitoringJob(
            booking_id=uuid4(), desk_id=101, scheduled_time=now - timedelta(days=10)
        )

        # Recent job (should not be deleted)
        recent_job = MonitoringJob(
            booking_id=uuid4(), desk_id=102, scheduled_time=now - timedelta(hours=1)
        )

        repository.create(old_job)
        repository.create(recent_job)

        # Cleanup jobs older than 2 days
        cutoff = now - timedelta(days=2)
        repository.cleanup_old_jobs(cutoff)

        # Verify old job is deleted
        assert repository.get_by_id(old_job.job_id) is None

        # Verify recent job still exists
        assert repository.get_by_id(recent_job.job_id) is not None

    def test_cleanup_old_jobs_no_deletions(
        self, repository: MonitoringJobRepository, sample_job: MonitoringJob
    ) -> None:
        """Test cleanup when no jobs meet the criteria."""
        created_job = repository.create(sample_job)

        # Cleanup with cutoff far in the past
        cutoff = datetime.now(timezone.utc) - timedelta(days=365)
        repository.cleanup_old_jobs(cutoff)

        # Verify job still exists
        assert repository.get_by_id(created_job.job_id) is not None


class TestMonitoringJobFromDTO:
    """Tests for the from_dto class method."""

    def test_from_dto_creates_job(self, sample_booking_message: BookingMessage) -> None:
        """Test creating a MonitoringJob from a BookingMessage DTO."""
        job = MonitoringJob.from_dto(sample_booking_message)

        assert job.booking_id == sample_booking_message.booking_id
        assert job.desk_id == sample_booking_message.desk_id
        assert job.scheduled_time == sample_booking_message.start_time
        assert job.status == JobStatus.PENDING
        assert job.job_id is not None
