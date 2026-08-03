from datetime import UTC, datetime


def local_datetime_str_from_timestamp(timestamp_ms: float) -> str:
    """Convert a Signal message timestamp (ms since epoch) to a local-time string."""
    local = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).astimezone()
    return local.strftime("%H:%M:%S %d-%m-%Y")
