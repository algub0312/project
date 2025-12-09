from datetime import datetime

from apscheduler.triggers.cron import CronTrigger


def create_cron_trigger_from_datetime(time: datetime) -> CronTrigger:
    """Create a CronTrigger from a given datetime object.

    Args:
        time (datetime): The datetime object to create the trigger from.

    Returns:
        CronTrigger: The created CronTrigger instance.

    """
    return CronTrigger(
        year=time.year,
        month=time.month,
        day=time.day,
        hour=time.hour,
        minute=time.minute,
        second=time.second,
    )
