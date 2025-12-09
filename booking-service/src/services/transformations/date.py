from datetime import datetime, timezone


def normalize_to_utc(date: datetime) -> datetime:
    """Normalize a datetime object to UTC timezone.

    Args:
        date (datetime): The datetime object to normalize.

    Returns:
        datetime: The normalized datetime object in UTC timezone.

    """
    return (
        date.astimezone(timezone.utc)
        if date.tzinfo
        else date.replace(tzinfo=timezone.utc)
    )
