from datetime import datetime, timedelta
from random import randint
from typing import Generator
from uuid import uuid4

import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from testcontainers.postgres import PostgresContainer

from src.models.db.desk_booking import DeskBooking
from src.models.dto.desk_booking_create_request import DeskBookingCreateRequest
from src.models.dto.desk_booking_update_request import DeskBookingUpdateRequest
from src.repositories.booking_repository import DeskBookingRepository
from src.services.desk_booking_service import DeskBookingService

MAX_INT = 2**31 - 1


class DummyMessaging:
    """Minimal stub for MessagingManager dependency used by the service."""

    @staticmethod
    def get_pubsub(exchange_name: str) -> "DummyPubSub":
        """Return a dummy pubsub exchange."""
        return DummyPubSub()


class DummyPubSub:
    """Minimal stub for PubSub exchange used by the messaging manager."""

    async def publish(self, message: object) -> None:
        """Return a dummy publish method that does nothing."""
        pass


@pytest.fixture(scope="module")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start a Postgres testcontainer for the module and stop it at the end."""
    container = PostgresContainer("postgres:17-alpine")
    container.start()
    try:
        yield container
    finally:
        container.stop()


@pytest.fixture
def db_session(postgres_container: PostgresContainer) -> Generator[Session, None, None]:
    """Create SQLModel tables on the test Postgres and yield a Session."""
    db_url = postgres_container.get_connection_url()
    engine = create_engine(db_url, echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.mark.asyncio
async def test_create_booking_flow(db_session: Session) -> None:
    """Integration test: create a booking and verify it is persisted and returned correctly."""  # noqa: E501
    repo = DeskBookingRepository(db_session)
    service = DeskBookingService(repo, DummyMessaging())

    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=2)
    create_req = DeskBookingCreateRequest(
        user_id=uuid4(),
        desk_id=randint(0, MAX_INT),
        start_time=start,
        end_time=end,
    )

    created_dto = await service.create_booking(create_req)

    assert created_dto.user_id == create_req.user_id
    assert created_dto.desk_id == create_req.desk_id

    # Verify persisted in DB
    persisted = db_session.exec(
        select(DeskBooking).where(DeskBooking.id == created_dto.id)
    ).one()
    assert persisted.id == created_dto.id
    assert persisted.user_id == create_req.user_id
    assert persisted.desk_id == create_req.desk_id


@pytest.mark.asyncio
async def test_update_booking_flow(db_session: Session) -> None:
    """Integration test: create then update a booking and verify changes persist."""
    repo = DeskBookingRepository(db_session)
    service = DeskBookingService(repo, DummyMessaging())

    # Create initial booking via repository (could use service as well)
    initial_start = datetime.now() + timedelta(hours=1)
    initial_end = initial_start + timedelta(hours=2)
    booking = DeskBooking(
        user_id=uuid4(),
        desk_id=randint(0, MAX_INT),
        start_time=initial_start,
        end_time=initial_end,
    )
    repo.create(booking)

    # Prepare update request with new times and possibly new user/desk
    new_start = initial_start + timedelta(days=1)
    new_end = new_start + timedelta(hours=3)
    update_req = DeskBookingUpdateRequest(
        user_id=uuid4(),
        desk_id=randint(0, MAX_INT),
        start_time=new_start,
        end_time=new_end,
    )

    updated_dto = await service.update_booking(booking.id, update_req)
    assert updated_dto is not None
    assert updated_dto.id == booking.id
    assert updated_dto.user_id == update_req.user_id
    assert updated_dto.desk_id == update_req.desk_id

    # Verify persisted changes
    persisted = db_session.exec(
        select(DeskBooking).where(DeskBooking.id == booking.id)
    ).one()
    assert persisted.user_id == update_req.user_id
    assert persisted.desk_id == update_req.desk_id


@pytest.mark.asyncio
async def test_create_booking_overlapping_rejected(db_session: Session) -> None:
    """Integration test: creating a booking that overlaps an existing booking should be rejected."""  # noqa: E501
    repo = DeskBookingRepository(db_session)
    service = DeskBookingService(repo, DummyMessaging())

    desk_id = randint(0, MAX_INT)
    existing_start = datetime.now() + timedelta(hours=5)
    existing_end = existing_start + timedelta(hours=2)
    existing = DeskBooking(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=existing_start,
        end_time=existing_end,
    )
    repo.create(existing)

    # new booking overlaps existing (starts during existing)
    new_start = existing_start + timedelta(minutes=30)
    new_end = new_start + timedelta(hours=1)
    create_req = DeskBookingCreateRequest(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=new_start,
        end_time=new_end,
    )

    with pytest.raises(ValueError):  # noqa: PT011
        await service.create_booking(create_req)


@pytest.mark.asyncio
async def test_create_booking_overlapping_rejected_with_tolerance(
    db_session: Session,
) -> None:
    """Integration test: creating a booking that overlaps an existing booking with tolerance should be rejected."""  # noqa: E501
    repo = DeskBookingRepository(db_session)
    service = DeskBookingService(repo, DummyMessaging())

    desk_id = randint(0, MAX_INT)
    existing_start = datetime.now() + timedelta(hours=5)
    existing_end = existing_start + timedelta(hours=2)
    existing = DeskBooking(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=existing_start,
        end_time=existing_end,
    )
    repo.create(existing)

    # new booking overlaps existing start time within tolerance
    new_start = existing_start - timedelta(hours=1)
    new_end = new_start + timedelta(minutes=51)
    create_req = DeskBookingCreateRequest(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=new_start,
        end_time=new_end,
    )

    with pytest.raises(ValueError):  # noqa: PT011
        await service.create_booking(create_req)

    # new booking overlaps existing end time within tolerance
    new_start = existing_end + timedelta(minutes=9)
    new_end = new_start + timedelta(hours=1)
    create_req = DeskBookingCreateRequest(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=new_start,
        end_time=new_end,
    )

    with pytest.raises(ValueError):  # noqa: PT011
        await service.create_booking(create_req)


@pytest.mark.asyncio
async def test_update_booking_overlapping_rejected(db_session: Session) -> None:
    """Integration test: updating a booking to overlap another booking on the same desk should be rejected."""  # noqa: E501
    repo = DeskBookingRepository(db_session)
    service = DeskBookingService(repo, DummyMessaging())

    desk_id = randint(0, MAX_INT)
    # booking A occupies a time window
    a_start = datetime.now() + timedelta(days=2)
    a_end = a_start + timedelta(hours=3)
    booking_a = DeskBooking(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=a_start,
        end_time=a_end,
    )
    repo.create(booking_a)

    # booking B initially non-overlapping on same desk
    b_start = a_end + timedelta(hours=1)
    b_end = b_start + timedelta(hours=2)
    booking_b = DeskBooking(
        user_id=uuid4(),
        desk_id=desk_id,
        start_time=b_start,
        end_time=b_end,
    )
    repo.create(booking_b)

    # attempt to update booking_b to overlap booking_a
    update_start = a_start + timedelta(hours=1)
    update_end = update_start + timedelta(hours=1)
    update_req = DeskBookingUpdateRequest(
        user_id=booking_b.user_id,
        desk_id=desk_id,
        start_time=update_start,
        end_time=update_end,
    )

    with pytest.raises(ValueError):  # noqa: PT011
        await service.update_booking(booking_b.id, update_req)
