"""Unit tests for desk_position_scheduler_service.py.

Tests the SchedulerService class in isolation with all dependencies mocked.
"""

import os
import sys
import unittest
from datetime import datetime
from typing import Callable
from unittest.mock import Mock, patch

# Add the project root to the path (go up from tests/unit to project root)
# This MUST happen before importing from src
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

# ruff: noqa: E402
import pytest

from src.services.position.desk_position_scheduler_service import (
    DeskPositionSchedulerService,
)

# -------------------- Test Constants --------------------
STATE_RUNNING = 1
STATE_STOPPED = 0

EXPECTED_JOBS_COUNT = 3
EXPECTED_JOBS_LEN = 2

RAISE_POSITION_MM = 1100
LOWER_POSITION_MM = 680

NEXT_RUN_RAISE = "2025-01-01T08:00:00"
NEXT_RUN_LOWER = "2025-01-01T17:00:00"
NEXT_RUN_JOB1 = "2025-01-01T10:00:00"

INVALID_POSITION_MSG = "position_mm must be a positive integer"


class TestSchedulerService(unittest.TestCase):
    """Unit tests for SchedulerService class."""

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        # Create a fresh instance for each test.
        self.service = DeskPositionSchedulerService()
        # Mock the scheduler.
        self.service.scheduler = Mock()
        self.service.scheduler.state = STATE_RUNNING

    def tearDown(self) -> None:
        """Clean up after each test."""
        self.service = None

    # ==================== Lifecycle Tests ====================

    def test_start_when_not_running(self) -> None:
        """Test starting the scheduler when it's not running."""
        self.service.scheduler.state = STATE_STOPPED

        self.service.start()

        self.service.scheduler.start.assert_called_once()

    def test_start_when_already_running(self) -> None:
        """Test starting the scheduler when it's already running."""
        self.service.scheduler.state = STATE_RUNNING

        self.service.start()

        self.service.scheduler.start.assert_not_called()

    def test_shutdown_when_running(self) -> None:
        """Test shutting down the scheduler when it's running."""
        self.service.scheduler.state = STATE_RUNNING

        self.service.shutdown()

        self.service.scheduler.shutdown.assert_called_once_with(wait=False)

    def test_shutdown_when_not_running(self) -> None:
        """Test shutting down the scheduler when it's not running."""
        self.service.scheduler.state = STATE_STOPPED

        self.service.shutdown()

        self.service.scheduler.shutdown.assert_not_called()

    def test_is_running_returns_true(self) -> None:
        """Test is_running returns True when scheduler is running."""
        self.service.scheduler.state = STATE_RUNNING

        result = self.service.is_running()

        assert result

    def test_is_running_returns_false(self) -> None:
        """Test is_running returns False when scheduler is not running."""
        self.service.scheduler.state = STATE_STOPPED

        result = self.service.is_running()

        assert not result

    # ==================== Info Tests ====================

    def test_get_jobs_count(self) -> None:
        """Test getting the number of scheduled jobs."""
        mock_jobs = [Mock(), Mock(), Mock()]
        self.service.scheduler.get_jobs.return_value = mock_jobs

        count = self.service.get_jobs_count()

        assert count == EXPECTED_JOBS_COUNT

    def test_get_all_jobs(self) -> None:
        """Test getting all scheduled jobs."""
        # Create mock jobs
        mock_job1 = Mock()
        mock_job1.id = "job1"
        mock_job1.name = "Test Job 1"
        mock_job1.next_run_time = datetime(2025, 1, 1, 10, 0)
        mock_job1.trigger = "cron[hour=10]"

        mock_job2 = Mock()
        mock_job2.id = "job2"
        mock_job2.name = "Test Job 2"
        mock_job2.next_run_time = None
        mock_job2.trigger = "cron[hour=20]"

        self.service.scheduler.get_jobs.return_value = [mock_job1, mock_job2]

        jobs = self.service.get_all_jobs()

        assert len(jobs) == EXPECTED_JOBS_LEN
        assert jobs[0]["id"] == "job1"
        assert jobs[0]["name"] == "Test Job 1"
        assert jobs[0]["next_run"] == NEXT_RUN_JOB1
        assert jobs[1]["next_run"] is None

    # ==================== Add Schedule Tests ====================

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_add_schedule_raise_action(self, mock_desk_service: Mock) -> None:
        """Test adding a schedule (position for raising)."""
        mock_job = Mock()
        mock_job.id = "test_raise"
        mock_job.next_run_time = datetime(2025, 1, 1, 8, 0)
        self.service.scheduler.add_job.return_value = mock_job

        result = self.service.add_schedule(
            job_id="test_raise",
            name="Morning Raise",
            position_mm=RAISE_POSITION_MM,
            hour=8,
            minute=0,
            day_of_week="mon-fri",
        )

        self.service.scheduler.add_job.assert_called_once()
        assert result["job_id"] == "test_raise"
        assert result["next_run"] == NEXT_RUN_RAISE

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_add_schedule_lower_action(self, mock_desk_service: Mock) -> None:
        """Test adding a schedule (position for lowering)."""
        mock_job = Mock()
        mock_job.id = "test_lower"
        mock_job.next_run_time = datetime(2025, 1, 1, 17, 0)
        self.service.scheduler.add_job.return_value = mock_job

        result = self.service.add_schedule(
            job_id="test_lower",
            name="Evening Lower",
            position_mm=LOWER_POSITION_MM,
            hour=17,
            minute=0,
            day_of_week="*",
        )

        self.service.scheduler.add_job.assert_called_once()
        assert result["job_id"] == "test_lower"

    def test_add_schedule_invalid_position_negative(self) -> None:
        """Test adding a schedule with negative position."""
        with pytest.raises(ValueError, match=INVALID_POSITION_MSG):
            self.service.add_schedule(
                job_id="invalid_pos",
                name="Invalid Position",
                position_mm=-100,
                hour=8,
                minute=0,
            )

    def test_add_schedule_invalid_position_zero(self) -> None:
        """Test adding a schedule with zero position."""
        with pytest.raises(ValueError, match=INVALID_POSITION_MSG):
            self.service.add_schedule(
                job_id="zero_pos",
                name="Zero Position",
                position_mm=0,
                hour=8,
                minute=0,
            )

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_add_schedule_replaces_existing(self, mock_desk_service: Mock) -> None:
        """Test that add_schedule replaces existing job with same ID."""
        mock_job = Mock()
        mock_job.id = "existing_job"
        mock_job.next_run_time = datetime(2025, 1, 1, 9, 0)
        self.service.scheduler.add_job.return_value = mock_job

        self.service.add_schedule(
            job_id="existing_job",
            name="Replaced Job",
            position_mm=RAISE_POSITION_MM,
            hour=9,
            minute=0,
        )

        # Verify replace_existing=True was passed
        call_kwargs = self.service.scheduler.add_job.call_args[1]
        assert call_kwargs.get("replace_existing")

    # ==================== Remove Schedule Tests ====================

    def test_remove_schedule_success(self) -> None:
        """Test successfully removing a schedule."""
        self.service.remove_schedule("test_job")

        self.service.scheduler.remove_job.assert_called_once_with("test_job")

    # ==================== Setup Default Schedules Tests ====================

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_setup_default_schedules(self, mock_desk_service: Mock) -> None:
        """Test setting up default schedules."""
        mock_job = Mock()
        mock_job.id = "mock_job"
        mock_job.next_run_time = datetime(2025, 1, 1, 20, 0)
        self.service.scheduler.add_job.return_value = mock_job

        self.service.setup_default_schedules()

        # Should create 3 default schedules:
        # cleaning_start, cleaning_end, morning_standup.
        assert self.service.scheduler.add_job.call_count == EXPECTED_JOBS_COUNT

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_setup_default_schedules_idempotent(self, mock_desk_service: Mock) -> None:
        """Test that setup_default_schedules is idempotent."""
        mock_job = Mock()
        mock_job.id = "mock_job"
        mock_job.next_run_time = datetime(2025, 1, 1, 20, 0)
        self.service.scheduler.add_job.return_value = mock_job

        # Call twice
        self.service.setup_default_schedules()
        first_call_count = self.service.scheduler.add_job.call_count

        self.service.scheduler.add_job.reset_mock()

        self.service.setup_default_schedules()
        second_call_count = self.service.scheduler.add_job.call_count

        # Should have same number of calls both times.
        assert first_call_count == second_call_count


class TestSchedulerServiceJobExecution(unittest.TestCase):
    """Test the actual job functions that get scheduled."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        self.service = DeskPositionSchedulerService()
        self.service.scheduler = Mock()

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_job_function_calls_raise_all_desks(self, mock_desk_service: Mock) -> None:
        """Test that scheduled job calls DeskService.raise_all_desks."""
        mock_job = Mock()
        mock_job.id = "test_raise"
        mock_job.next_run_time = datetime(2025, 1, 1, 8, 0)

        # Capture the job function
        captured_func: Callable[..., object] | None = None

        def capture_add_job(
            func: Callable[..., object],
            *args: object,
            **kwargs: object,
        ) -> Mock:
            nonlocal captured_func
            captured_func = func
            return mock_job

        self.service.scheduler.add_job.side_effect = capture_add_job

        # Add a schedule
        self.service.add_schedule(
            job_id="test_raise",
            name="Test Raise",
            position_mm=RAISE_POSITION_MM,
            hour=8,
            minute=0,
        )

        # Execute the captured function
        assert captured_func is not None
        captured_func()

        # Verify DeskService.raise_all_desks was called
        mock_desk_service.raise_all_desks.assert_called_once_with(
            RAISE_POSITION_MM,
            context={
                "trigger": "schedule",
                "job_id": "test_raise",
                "job_name": "Test Raise",
            },
        )

    @patch("src.services.position.desk_position_scheduler_service.DeskService")
    def test_job_function_calls_lower_position(self, mock_desk_service: Mock) -> None:
        """Test that scheduled job with lower position calls raise_all_desks.

        Note: Since we removed the action field, all schedules now use
        raise_all_desks to set the target position (whether high or low).
        """
        mock_job = Mock()
        mock_job.id = "test_lower"
        mock_job.next_run_time = datetime(2025, 1, 1, 17, 0)

        # Capture the job function
        captured_func: Callable[..., object] | None = None

        def capture_add_job(
            func: Callable[..., object],
            *args: object,
            **kwargs: object,
        ) -> Mock:
            nonlocal captured_func
            captured_func = func
            return mock_job

        self.service.scheduler.add_job.side_effect = capture_add_job

        # Add a schedule with lower position
        self.service.add_schedule(
            job_id="test_lower",
            name="Test Lower",
            position_mm=LOWER_POSITION_MM,
            hour=17,
            minute=0,
        )

        # Execute the captured function
        assert captured_func is not None
        captured_func()

        # Verify DeskService.raise_all_desks was called (not lower_all_desks)
        # Because we now always use raise_all_desks to set position
        mock_desk_service.raise_all_desks.assert_called_once_with(
            LOWER_POSITION_MM,
            context={
                "trigger": "schedule",
                "job_id": "test_lower",
                "job_name": "Test Lower",
            },
        )


if __name__ == "__main__":
    # Run the tests with verbose output.
    unittest.main(verbosity=2)
