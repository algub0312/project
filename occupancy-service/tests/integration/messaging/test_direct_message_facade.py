import asyncio
from asyncio import AbstractEventLoop
from typing import Generator

import pytest

from src.messaging.direct_message_facade import DirectMessageFacade
from tests.integration.messaging.utils.rabbitmq_container import (
    EXCHANGE_NAME,
    QUEUE_NAME,
    ROUTING_KEY,
    DummyMessage,
    RabbitMqContainer,
    get_amqp_url,
)
from tests.integration.messaging.utils.rabbitmq_container import (
    rabbitmq_container as _rabbitmq_container,  # noqa: F401
)


@pytest.fixture(scope="module")
def event_loop() -> Generator[AbstractEventLoop]:
    """Create an instance of the event loop for the module scope."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_is_connected_property(
    _rabbitmq_container: RabbitMqContainer,  # noqa: PT019, F811
) -> None:
    """Integration test for the is_connected property of DirectMessageFacade."""
    amqp_url = get_amqp_url(_rabbitmq_container)
    facade = DirectMessageFacade(amqp_url, EXCHANGE_NAME)

    assert not facade.is_connected
    await facade.connect()
    assert facade.is_connected


@pytest.mark.asyncio
async def test_integration_send_and_receive(
    _rabbitmq_container: RabbitMqContainer,  # noqa: PT019, F811
) -> None:
    """Integration test for sending and receiving messages using DirectMessageFacade."""
    message_to_send, received_messages, _, _ = await _send_and_receive_message(
        _rabbitmq_container
    )
    assert len(received_messages) == 1
    assert received_messages[0].content == message_to_send.content


@pytest.mark.asyncio
async def test_integration_reconnect_and_send(
    _rabbitmq_container: RabbitMqContainer,  # noqa: PT019, F811
) -> None:
    """Integration test for reconnecting and sending messages using DirectMessageFacade."""  # noqa: E501
    (
        message_to_send,
        received_messages,
        facade,
        message_received_event,
    ) = await _send_and_receive_message(_rabbitmq_container)
    await facade.connect()
    received_messages.clear()
    message_received_event.clear()
    await asyncio.sleep(2)

    async def on_message(message: DummyMessage) -> None:
        received_messages.append(message)
        message_received_event.set()

    facade.receive_messages(
        routing_key=ROUTING_KEY,
        queue_name=QUEUE_NAME,
        on_message=on_message,
        message_type=DummyMessage,
    )

    msg = DummyMessage(content="reconnect test")
    await facade.send_message(msg, ROUTING_KEY)

    try:
        await asyncio.wait_for(
            message_received_event.wait(), timeout=10
        )  # Increased timeout
    except asyncio.TimeoutError:
        print("Test failed to receive the message after reconnect.")
    await facade.close()

    assert len(received_messages) == 1, (
        f"Expected 1 message, got {len(received_messages)}"
    )
    assert received_messages[0].content == msg.content


async def _send_and_receive_message(
    _rabbitmq_container: RabbitMqContainer,  # noqa: F811
) -> tuple[DummyMessage, list[DummyMessage], DirectMessageFacade, asyncio.Event]:
    """Send and receive a message using DirectMessageFacade."""
    amqp_url = get_amqp_url(_rabbitmq_container)

    facade = DirectMessageFacade(amqp_url, EXCHANGE_NAME)
    await facade.connect()

    received_messages = []
    message_received_event = asyncio.Event()

    async def on_message(message: DummyMessage) -> None:
        received_messages.append(message)
        message_received_event.set()

    facade.receive_messages(
        routing_key=ROUTING_KEY,
        queue_name=QUEUE_NAME,
        on_message=on_message,
        message_type=DummyMessage,
    )

    await asyncio.sleep(1)

    message_to_send = DummyMessage(content="integration test payload")
    await facade.send_message(message_to_send, ROUTING_KEY)
    await asyncio.wait_for(message_received_event.wait(), timeout=5)
    await facade.close()
    return message_to_send, received_messages, facade, message_received_event
