"""Unit tests for desk_service.py.

Tests the DeskService class in isolation with all dependencies mocked.
"""

import os
import sys
import unittest
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
import requests

from src.services.desk_service import DeskService, DeskServiceError

# === Test constants to avoid magic values ===
DEFAULT_DESK_COUNT = 3
TWO_DESKS_COUNT = 2
EXPECTED_POSITION_MM = 800
RAISE_POSITION_MM = 1100
HTTP_NOT_FOUND = 404
LOWER_POSITION_MM = 680


# Add the project root to the path (go up from tests/unit to project root)
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)


class TestDeskService(unittest.TestCase):
    """Unit tests for DeskService class."""

    def setUp(self) -> None:
        """Set up test fixtures before each test method."""
        # Nothing to set up right now.
        return None

    def tearDown(self) -> None:
        """Clean up after each test."""
        # Nothing to tear down right now.
        return None

    # ==================== URL Building Tests ====================

    def test_build_url_with_single_segment(self) -> None:
        """Test building URL with single segment."""
        url = DeskService._build_url("desks")

        assert "desks" in url
        assert DeskService._config.api_key in url

    def test_build_url_with_multiple_segments(self) -> None:
        """Test building URL with multiple segments."""
        url = DeskService._build_url("desks", "test-desk-id")

        assert "desks" in url
        assert "test-desk-id" in url
        assert DeskService._config.api_key in url

    def test_build_url_strips_slashes(self) -> None:
        """Test that URL building strips leading/trailing slashes."""
        url = DeskService._build_url("/desks/", "/test-id/")

        # Should not have double slashes
        assert "//desks" not in url
        assert "//test-id" not in url

    # ==================== Get All Desks Tests ====================

    @patch("src.services.desk_service.requests.request")
    def test_get_all_desks_success(self, mock_request: Mock) -> None:
        """Test successfully getting all desks."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = ["desk1", "desk2", "desk3"]
        mock_request.return_value = mock_response

        desks = DeskService.get_all_desks()

        assert len(desks) == DEFAULT_DESK_COUNT
        assert "desk1" in desks
        mock_request.assert_called_once()

    @patch("src.services.desk_service.requests.request")
    def test_get_all_desks_empty_list(self, mock_request: Mock) -> None:
        """Test getting all desks when list is empty."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_request.return_value = mock_response

        desks = DeskService.get_all_desks()

        assert len(desks) == 0

    @patch("src.services.desk_service.requests.request")
    def test_get_all_desks_api_error(self, mock_request: Mock) -> None:
        """Test getting all desks when API returns error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response

        with pytest.raises(DeskServiceError) as ctx:
            DeskService.get_all_desks()

        assert "500" in str(ctx.value)

    @patch("src.services.desk_service.requests.request")
    def test_get_all_desks_network_error(self, mock_request: Mock) -> None:
        """Test getting all desks when network error occurs."""
        mock_request.side_effect = requests.RequestException("Network error")

        with pytest.raises(DeskServiceError) as ctx:
            DeskService.get_all_desks()

        assert "Failed to communicate" in str(ctx.value)

    @patch("src.services.desk_service.requests.request")
    def test_get_all_desks_unexpected_format(self, mock_request: Mock) -> None:
        """Test getting all desks with unexpected response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        mock_request.return_value = mock_response

        with pytest.raises(DeskServiceError) as ctx:
            DeskService.get_all_desks()

        assert "unexpected response format" in str(ctx.value)

    # ==================== Set Desk Position Tests ====================

    @patch("src.services.desk_service.requests.request")
    def test_set_desk_position_success(self, mock_request: Mock) -> None:
        """Test successfully setting desk position."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        result: Dict[str, Any] = DeskService.set_desk_position("desk1", 1100)

        assert result["status"] == "success"
        mock_request.assert_called_once()

        # Verify the request was made with correct method and payload
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "PUT"
        assert call_args.kwargs["json"] == {"position_mm": 1100}

    @patch("src.services.desk_service.requests.request")
    def test_set_desk_position_empty_desk_id(self, mock_request: Mock) -> None:
        """Test setting desk position with empty desk ID."""
        with pytest.raises(DeskServiceError) as ctx:
            DeskService.set_desk_position("", 1100)

        assert "Desk identifier is required" in str(ctx.value)
        mock_request.assert_not_called()

    @patch("src.services.desk_service.requests.request")
    def test_set_desk_position_api_error(self, mock_request: Mock) -> None:
        """Test setting desk position when API returns error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Desk not found"
        mock_request.return_value = mock_response

        with pytest.raises(DeskServiceError) as ctx:
            DeskService.set_desk_position("nonexistent", 1100)

        assert "404" in str(ctx.value)

    # ==================== Get Desk State Tests ====================

    @patch("src.services.desk_service.requests.request")
    def test_get_desk_state_success(self, mock_request: Mock) -> None:
        """Test successfully getting desk state."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "config": {"name": "Test Desk"},
            "state": {"position_mm": 800, "status": "idle"},
        }
        mock_request.return_value = mock_response

        state = DeskService.get_desk_state("desk1")

        assert state is not None
        assert state["config"]["name"] == "Test Desk"
        assert state["state"]["position_mm"] == EXPECTED_POSITION_MM

    @patch("src.services.desk_service.requests.request")
    def test_get_desk_state_empty_desk_id(self, mock_request: Mock) -> None:
        """Test getting desk state with empty desk ID."""
        state = DeskService.get_desk_state("")

        assert state is None
        mock_request.assert_not_called()

    @patch("src.services.desk_service.requests.request")
    def test_get_desk_state_api_error(self, mock_request: Mock) -> None:
        """Test getting desk state when API returns error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request.return_value = mock_response

        state = DeskService.get_desk_state("nonexistent")

        # Should return None instead of raising
        assert state is None

    # ==================== Raise All Desks Tests ====================

    @patch("src.services.desk_service.DeskService.set_desk_position")
    @patch("src.services.desk_service.DeskService.get_all_desks")
    def test_raise_all_desks_success(
        self,
        mock_get_all: Mock,
        mock_set_pos: Mock,
    ) -> None:
        """Test successfully raising all desks."""
        mock_get_all.return_value = ["desk1", "desk2", "desk3"]
        mock_set_pos.return_value = {"status": "success"}

        results = DeskService.raise_all_desks(1100)

        assert len(results) == DEFAULT_DESK_COUNT
        assert all(r["success"] for r in results)
        assert mock_set_pos.call_count == DEFAULT_DESK_COUNT

    @patch("src.services.desk_service.DeskService.set_desk_position")
    @patch("src.services.desk_service.DeskService.get_all_desks")
    def test_raise_all_desks_partial_failure(
        self, mock_get_all: Mock, mock_set_pos: Mock
    ) -> None:
        """Test raising all desks with some failures."""
        mock_get_all.return_value = ["desk1", "desk2", "desk3"]

        # desk2 will fail
        def set_position_side_effect(desk_id: str, position: int) -> Dict[str, Any]:
            if desk_id == "desk2":
                raise DeskServiceError("Desk unreachable")
            return {"status": "success"}

        mock_set_pos.side_effect = set_position_side_effect

        results = DeskService.raise_all_desks(1100)

        assert len(results) == DEFAULT_DESK_COUNT
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        assert len(successful) == TWO_DESKS_COUNT
        assert len(failed) == 1
        assert failed[0]["desk_id"] == "desk2"

    @patch("src.services.desk_service.DeskService.set_desk_position")
    @patch("src.services.desk_service.DeskService.get_all_desks")
    def test_raise_all_desks_with_context(
        self, mock_get_all: Mock, mock_set_pos: Mock
    ) -> None:
        """Test raising all desks with context information."""
        mock_get_all.return_value = ["desk1"]
        mock_set_pos.return_value = {"status": "success"}

        context = {"trigger": "test", "test_id": "123"}
        DeskService.raise_all_desks(1100, context=context)

    # ==================== Lower All Desks Tests ====================

    @patch("src.services.desk_service.DeskService.set_desk_position")
    @patch("src.services.desk_service.DeskService.get_all_desks")
    def test_lower_all_desks_success(
        self, mock_get_all: Mock, mock_set_pos: Mock
    ) -> None:
        """Test successfully lowering all desks."""
        mock_get_all.return_value = ["desk1", "desk2"]
        mock_set_pos.return_value = {"status": "success"}

        results = DeskService.lower_all_desks(680)

        assert len(results) == TWO_DESKS_COUNT
        assert all(r["success"] for r in results)


class TestDeskServiceError(unittest.TestCase):
    """Test the DeskServiceError exception class."""

    def test_error_with_message_only(self) -> None:
        """Test creating error with message only."""
        error = DeskServiceError("Test error")

        assert str(error) == "Test error"
        assert error.status_code is None

    def test_error_with_status_code(self) -> None:
        """Test creating error with status code."""
        error = DeskServiceError("API error", status_code=404)

        assert str(error) == "API error"
        assert error.status_code == HTTP_NOT_FOUND

    def test_error_is_runtime_error(self) -> None:
        """Test that DeskServiceError is a RuntimeError."""
        error = DeskServiceError("Test")
        assert isinstance(error, RuntimeError)


class TestDeskServiceIntegration(unittest.TestCase):
    """Integration-style tests for DeskService operations."""

    @patch("src.services.desk_service.requests.request")
    def test_full_raise_workflow(self, mock_request: Mock) -> None:
        """Test full workflow of raising all desks."""
        # Mock getting all desks
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = ["desk1", "desk2"]

        # Mock setting positions
        mock_set_response = Mock()
        mock_set_response.status_code = 200
        mock_set_response.json.return_value = {"status": "success"}

        # Return appropriate response based on call
        def request_side_effect(*args: object, **kwargs: object) -> Mock:
            if kwargs.get("method") == "GET":
                return mock_get_response
            return mock_set_response

        mock_request.side_effect = request_side_effect

        results = DeskService.raise_all_desks(1100)

        assert len(results) == TWO_DESKS_COUNT
        assert all(r["success"] for r in results)
        # 1 GET + 2 PUTs
        assert mock_request.call_count == DEFAULT_DESK_COUNT


if __name__ == "__main__":
    # Allow running this file directly for quick checks.
    unittest.main(verbosity=2)
