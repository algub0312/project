"""Test script for desk_service.py.

Verifies connection to WiFi2BLE Box Simulator.
Run this from the backend/scheduler-service directory.
"""

import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from src.services.desk_service import DeskService, DeskServiceError

# Set environment variables for testing
os.environ["DESK_API_BASE_URL"] = "http://localhost:8000/api/v2"
os.environ["DESK_API_KEY"] = "E9Y2LxT4g1hQZ7aD8nR3mWx5P0qK6pV7"
os.environ["DESK_API_TIMEOUT_SECONDS"] = "10"

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def desk_id() -> str:
    """Fixture to provide a valid desk ID for testing."""
    return "3a:6e:93:18:3f:5f"


@pytest.fixture
def position_mm() -> int:
    """Fixture to provide a test position in mm."""
    return 700


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_get_all_desks() -> List[str]:
    """Test 1: Fetch all desks."""
    print_header("TEST 1: Get All Desks")

    try:
        desks = DeskService.get_all_desks()
        print(f"✓ SUCCESS! Found {len(desks)} desks:")
        for i, desk_id in enumerate(desks, 1):
            print(f"  {i}. {desk_id}")
        return desks

    except DeskServiceError as e:
        print(f"✗ FAILED: {e}")
        if getattr(e, "status_code", None):
            print(f"  HTTP Status: {e.status_code}")
        return []

    except Exception as e:  # pragma: no cover - debug aid
        print(f"✗ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return []


def test_get_desk_state(desk_id: str) -> Optional[Dict[str, Any]]:
    """Test 2: Get desk state."""
    print_header(f"TEST 2: Get Desk State for {desk_id}")

    try:
        state = DeskService.get_desk_state(desk_id)

        if state:
            print("✓ SUCCESS! Desk state:")
            config = state.get("config", {})
            desk_state = state.get("state", {})

            print(f"  Name: {config.get('name', 'N/A')}")
            print(f"  Manufacturer: {config.get('manufacturer', 'N/A')}")
            print(f"  Position: {desk_state.get('position_mm', 'N/A')}mm")
            print(f"  Speed: {desk_state.get('speed_mms', 'N/A')}mm/s")
            print(f"  Status: {desk_state.get('status', 'N/A')}")
            return state

        print(f"✗ No state returned for desk {desk_id}")
        return None

    except Exception as e:  # pragma: no cover - debug aid
        print(f"✗ ERROR: {e}")
        traceback.print_exc()
        return None


def test_set_desk_position(desk_id: str, position_mm: int) -> bool:
    """Test 3: Set desk position."""
    print_header(f"TEST 3: Set Desk Position to {position_mm}mm")

    try:
        result = DeskService.set_desk_position(desk_id, position_mm)
        print(f"✓ SUCCESS! Desk commanded to move to {position_mm}mm")
        print(f"  Response: {result}")
        return True

    except DeskServiceError as e:
        print(f"✗ FAILED: {e}")
        if getattr(e, "status_code", None):
            print(f"  HTTP Status: {e.status_code}")
        return False

    except Exception as e:  # pragma: no cover - debug aid
        print(f"✗ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return False


def test_raise_all_desks(position_mm: int) -> List[Dict[str, Any]]:
    """Test 4: Raise all desks."""
    print_header(f"TEST 4: Raise All Desks to {position_mm}mm")

    try:
        results = DeskService.raise_all_desks(
            position_mm, context={"trigger": "test_script", "test": True}
        )

        successful = sum(1 for r in results if r["success"])
        print(f"✓ Operation complete: {successful}/{len(results)} desks successful")

        for result in results:
            status = "✓" if result["success"] else "✗"
            print(f"  {status} {result['desk_id']}")

        return results

    except DeskServiceError as e:
        print(f"✗ FAILED: {e}")
        return []

    except Exception as e:  # pragma: no cover - debug aid
        print(f"✗ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return []


def main() -> int:
    """Run all tests."""
    print_header("WiFi2BLE Box Simulator - Desk Service Test")

    print("\nConfiguration:")
    print(f"  Base URL: {os.environ.get('DESK_API_BASE_URL')}")
    print(f"  API Key: {os.environ.get('DESK_API_KEY', '')[:20]}...")
    print(f"  Timeout: {os.environ.get('DESK_API_TIMEOUT_SECONDS')}s")
    print(f"  Running from: {Path(__file__).parent}")

    # Test 1: Get all desks
    desks = test_get_all_desks()

    if not desks:
        print("\n" + "=" * 70)
        print("❌ CANNOT CONTINUE - No desks found!")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("1. Is the WiFi2BLE Box Simulator running?")
        print("   Check with: docker ps")
        print("\n2. Is it accessible?")
        print(
            "   Try: curl http://localhost:8000/api/v2/"
            "E9Y2LxT4g1hQZ7aD8nR3mWx5P0qK6pV7/desks/"
        )
        print("\n3. Check the API key matches your simulator configuration")
        return 1

    # Test 2: Get state of first desk
    first_desk = desks[0]
    state = test_get_desk_state(first_desk)

    if state:
        current_position = state.get("state", {}).get("position_mm", 680)
        print(f"\nCurrent position: {current_position}mm")

    # Test 3: Move first desk to a test position
    test_position = 750  # Safe middle position
    success = test_set_desk_position(first_desk, test_position)

    # Test 4: Raise all desks (only if previous test succeeded)
    if success and len(desks) > 0:
        print("\nWaiting 2 seconds before testing raise all...")
        time.sleep(2)
        test_raise_all_desks(800)  # Moderate test position

    print_header("All Tests Complete!")
    print("\n✓ If all tests passed, your desk service is configured correctly!")
    print("✓ You can now deploy the scheduler service\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
