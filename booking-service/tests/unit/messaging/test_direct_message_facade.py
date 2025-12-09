from unittest.mock import AsyncMock, MagicMock, patch

import aio_pika
import pytest
from pydantic import Field

from src.messaging.direct_message_facade import (
    DirectMessageFacade,
)
from src.models.msg.abstract_message import AbstractMessage


class DummyMessage(AbstractMessage):
    """A dummy message class for testing purposes."""

    content: str = Field(...)

    def to_bytes(self) -> bytes:
        """Serialize the message to bytes."""
        return self.content.encode()

    @classmethod
    def from_bytes(cls, body: bytes) -> "DummyMessage":
        """Deserialize bytes to an instance of DummyMessage."""
        return cls(content=body.decode())


@pytest.fixture
def facade() -> DirectMessageFacade:
    """Fixture to create a DirectMessageFacade instance for testing."""
    return DirectMessageFacade("amqp://test", "test_exchange")


@pytest.mark.asyncio
@patch("aio_pika.connect_robust", new_callable=AsyncMock)
async def test_connect_initializes_attributes(
    mock_connect: AsyncMock, facade: DirectMessageFacade
) -> None:
    """Test that connect method initializes connection, channel, and exchange."""
    mock_connection = AsyncMock()
    mock_channel = AsyncMock()
    mock_exchange = AsyncMock()
    mock_connect.return_value = mock_connection
    mock_connection.channel.return_value = mock_channel
    mock_channel.declare_exchange.return_value = mock_exchange

    await facade.connect()

    mock_connect.assert_awaited_once_with(facade._amqp_url, loop=facade._loop)
    mock_connection.channel.assert_awaited_once()
    mock_channel.declare_exchange.assert_awaited_once_with(
        facade._exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
    )
    assert facade._connection == mock_connection
    assert facade._channel == mock_channel
    assert facade._exchange == mock_exchange


@pytest.mark.asyncio
@patch("aio_pika.Message")
@patch("aio_pika.Exchange.publish", new_callable=AsyncMock)
@patch.object(DirectMessageFacade, "connect", new_callable=AsyncMock)
async def test_send_message_publishes(
    mock_connect: AsyncMock,
    mock_publish: AsyncMock,
    mock_message_cls: MagicMock,
    facade: DirectMessageFacade,
) -> None:
    """Test that send_message publishes a message to the exchange."""
    mock_connect.return_value = None
    facade._exchange = MagicMock()
    facade._connection = MagicMock()
    facade._channel = MagicMock()
    facade._exchange.publish = mock_publish

    message_content = "Test message"
    routing_key = "test_routing_key"

    await facade.connect()
    dummy_message = DummyMessage(content=message_content)

    mock_message_instance = MagicMock()
    mock_message_cls.return_value = mock_message_instance

    await facade.send_message(dummy_message, routing_key)

    mock_message_cls.assert_called_once_with(
        body=dummy_message.to_bytes(),
        content_type="application/json",
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )

    mock_publish.assert_awaited_once_with(
        mock_message_instance, routing_key=routing_key
    )


@pytest.mark.asyncio
async def test_send_message_raises_if_no_exchange(facade: DirectMessageFacade) -> None:
    """Test that send_message raises RuntimeError if exchange is not initialized."""
    with pytest.raises(RuntimeError):
        await facade.send_message(DummyMessage(content="content"), "rk")


@pytest.mark.asyncio
async def test_close_closes_channel_and_connection(facade: DirectMessageFacade) -> None:
    """Test that close method closes channel and connection."""
    facade._consumer_task = AsyncMock()
    facade._consumer_task.done.return_value = False
    facade._consumer_task.cancel = AsyncMock()
    facade._cancel_consumer_task = AsyncMock()

    facade._channel = AsyncMock()
    facade._channel.is_closed = False
    facade._channel.close = AsyncMock()

    facade._connection = AsyncMock()
    facade._connection.is_closed = False
    facade._connection.close = AsyncMock()

    await facade.close()

    facade._cancel_consumer_task.assert_awaited_once()
    facade._channel.close.assert_awaited_once()
    facade._connection.close.assert_awaited_once()
