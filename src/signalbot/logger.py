import logging

LOGGER_NAME = "signalbot"
"""
The logger name used by signalbot.
"""


def enable_console_logging(level: int = logging.WARNING) -> None:
    """Enable console logging for the signalbot logger.

    Args:
        level: Logging level for the logger.
    """
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s %(name)s [%(levelname)s] - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(handler)
    logger.setLevel(level)
