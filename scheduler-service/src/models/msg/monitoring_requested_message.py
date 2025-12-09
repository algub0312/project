from src.models.msg.abstract_message import AbstractMessage


class MonitoringRequestedMessage(AbstractMessage):
    """Message class for monitoring requested events.

    Attributes:
        desk_id (int): Identifier of the desk to be monitored.

    """

    desk_id: int
