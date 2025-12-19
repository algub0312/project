import asyncio
import logging
import os
import time

import httpx
from dotenv import load_dotenv
from sqlmodel import Session

from src.api.dependencies import engine
from src.models.dto.desk_inventory_dto import DeskInventoryDTO
from src.repositories.desk_inventory_repository import DeskInventoryRepository
from src.services.converters.mac_to_int_converter import convert_mac_to_int
from src.services.desk_inventory_service import DeskInventoryService

logger = logging.getLogger(__name__)
load_dotenv()

DESK_INTEGRATION_SERVICE_URL = os.getenv("DESK_INTEGRATION_SERVICE_URL")
if DESK_INTEGRATION_SERVICE_URL is None:
    raise ValueError(
        "DESK_INTEGRATION_SERVICE_URL is not set in environment variables."
    )


async def fetch_initial_ids(client: httpx.AsyncClient) -> list[str]:
    """Fetch list of all desk IDs from the desk integration service.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the request.

    Returns:
        list[str]: A list of desk IDs.

    """
    logger.info("Fetching desk IDs from %s", DESK_INTEGRATION_SERVICE_URL)
    response = await client.get(DESK_INTEGRATION_SERVICE_URL)
    response.raise_for_status()
    desk_ids = response.json()
    logger.info("Found %d desk IDs: %s", len(desk_ids), desk_ids)
    return desk_ids


async def fetch_data(client: httpx.AsyncClient, desk_id: str) -> tuple[str, dict]:
    """Fetch data for a specific desk ID.

    Args:
        client (httpx.AsyncClient): The HTTP client to use for the request.
        desk_id (str): The desk ID to fetch data for.

    Returns:
        tuple[str, dict]: The desk ID and its corresponding data.

    """
    logger.debug("Fetching data for desk ID: %s", desk_id)
    response = await client.get(f"{DESK_INTEGRATION_SERVICE_URL}/{desk_id}")
    response.raise_for_status()
    return desk_id, response.json()


async def fetch_and_save_all_data(service: DeskInventoryService) -> list:
    """Fetch data for all desks and save to database.

    Args:
        service (DeskInventoryService): The desk inventory service instance.

    Returns:
        list: A list of results from the fetch operations.

    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        desk_ids = await fetch_initial_ids(client)
        tasks = [fetch_data(client, desk_id) for desk_id in desk_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successful = 0
        failed = 0

        for result in results:
            if isinstance(result, Exception):
                logger.error("Failed to fetch desk data: %s", result)
                failed += 1
            else:
                failed, successful = await save_desk(
                    service, result, successful, failed
                )
        logger.info("Fetch job completed: %d successful, %d failed", successful, failed)
        return results


async def save_desk(
    service: DeskInventoryService,
    result: tuple[str, dict],
    successful: int,
    failed: int,
) -> tuple[int, int]:
    """Save a single desk's data to the database.

    Args:
        service (DeskInventoryService): The desk inventory service instance.
        result (tuple[str, dict]): The desk ID and its corresponding data.
        successful (int): The current count of successful saves.
        failed (int): The current count of failed saves.

    Returns:
        tuple[int, int]: Updated counts of failed and successful saves.

    """
    desk_id, data = result
    logger.info("Processing desk ID: %s", desk_id)
    logger.debug("Desk data: %s", data)

    try:
        desk_id = convert_mac_to_int(desk_id)
        dto = DeskInventoryDTO.from_dict(desk_id, data)
        await service.create_or_update_desk(dto)
        logger.info("Successfully updated desk: %s", desk_id)
        successful += 1

    except Exception as e:
        logger.exception("Failed to save desk %s: %s", desk_id, e)
        failed += 1
    return failed, successful


def run_desks_fetching() -> None:
    """Run the desk fetching job."""
    logger.info("Fetch job started at %s", time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        with Session(engine) as session:
            repo = DeskInventoryRepository(session)
            service = DeskInventoryService(repo)

            results = asyncio.run(fetch_and_save_all_data(service))
            logger.info("Fetch job completed. Processed %d items", len(results))

    except Exception as e:
        logger.exception("Fetch job failed: %s", e)
