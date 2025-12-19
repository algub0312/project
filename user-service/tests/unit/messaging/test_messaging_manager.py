import pytest

from src.messaging.direct_message_facade import DirectMessageFacade
from src.messaging.messaging_manager import MessagingManager
from src.messaging.pubsub_facade import PubSubFacade

AMQP_URL = "amqp://test:test@localhost/"
EXCHANGE_NAME = "test_exchange"


def test_add_pubsub() -> None:
    """Test adding a PubSubFacade to the MessagingManager."""
    manager = MessagingManager()
    facade = PubSubFacade(AMQP_URL, EXCHANGE_NAME)
    manager.add_pubsub(facade)
    assert manager.get_pubsub(EXCHANGE_NAME) == facade


def test_add_pubsub_duplicate() -> None:
    """Test adding a duplicate PubSubFacade to the MessagingManager raises ValueError."""  # noqa: E501
    manager = MessagingManager()
    facade = PubSubFacade(AMQP_URL, EXCHANGE_NAME)
    manager.add_pubsub(facade)
    with pytest.raises(ValueError):  # noqa: PT011
        manager.add_pubsub(facade)


def test_add_pubsubs() -> None:
    """Test adding multiple PubSubFacades to the MessagingManager."""
    manager = MessagingManager()
    facade1 = PubSubFacade(AMQP_URL, EXCHANGE_NAME + "_1")
    facade2 = PubSubFacade(AMQP_URL, EXCHANGE_NAME + "_2")
    manager.add_pubsubs([facade1, facade2])
    assert manager.get_pubsub(EXCHANGE_NAME + "_1") == facade1
    assert manager.get_pubsub(EXCHANGE_NAME + "_2") == facade2


def test_get_pubsub_not_found() -> None:
    """Test retrieving a non-existent PubSubFacade raises ValueError."""
    manager = MessagingManager()
    with pytest.raises(ValueError):  # noqa: PT011
        manager.get_pubsub("non_existent_exchange")


def test_add_direct() -> None:
    """Test adding a DirectMessageFacade to the MessagingManager."""
    manager = MessagingManager()
    facade = DirectMessageFacade(AMQP_URL, EXCHANGE_NAME)
    manager.add_direct(facade)
    assert manager.get_direct(EXCHANGE_NAME) == facade


def test_add_direct_duplicate() -> None:
    """Test adding a duplicate DirectMessageFacade to the MessagingManager raises ValueError."""  # noqa: E501
    manager = MessagingManager()
    facade = DirectMessageFacade(AMQP_URL, EXCHANGE_NAME)
    manager.add_direct(facade)
    with pytest.raises(ValueError):  # noqa: PT011
        manager.add_direct(facade)


def test_add_directs() -> None:
    """Test adding multiple DirectMessageFacades to the MessagingManager."""
    manager = MessagingManager()
    facade1 = DirectMessageFacade(AMQP_URL, EXCHANGE_NAME + "_1")
    facade2 = DirectMessageFacade(AMQP_URL, EXCHANGE_NAME + "_2")
    manager.add_directs([facade1, facade2])
    assert manager.get_direct(EXCHANGE_NAME + "_1") == facade1
    assert manager.get_direct(EXCHANGE_NAME + "_2") == facade2


def test_get_direct_not_found() -> None:
    """Test retrieving a non-existent DirectMessageFacade raises ValueError."""
    manager = MessagingManager()
    with pytest.raises(ValueError):  # noqa: PT011
        manager.get_direct("non_existent_exchange")
