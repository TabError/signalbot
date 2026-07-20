import logging

LOGGER_NAME = "signalbot"
"""
The logger name used by signalbot.
"""


def initialize_logger(level: int = logging.WARNING) -> logging.Logger:
    """Creates a logger that outputs to console.

    Args:
        level: Logging level for the logger.

    Returns:
        The logger instance.
    """
    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s %(name)s [%(levelname)s] - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger
