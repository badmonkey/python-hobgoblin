from datetime import datetime, timedelta, timestamp, timezone

from dateutil import parser as dtparser
from pytimeparse import parse as duration  # noqa


def now(**kwargs):
    if kwargs:
        return datetime.now(timezone.utc) - timedelta(**kwargs)
    return datetime.now(timezone.utc)


def parse(data: str):
    if data:
        return dtparser.parse(data).replace(tzinfo=timezone.utc)
    return none_date()


def is_aware(dt: datetime):
    return dt is not None and dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None


def none_date():
    return datetime.fromtimestamp(0, tz=timezone.utc)


def none_timestamp():
    return none_date().timestamp()
