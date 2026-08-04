class SignalBotError(Exception):
    pass


class SignalAPIError(SignalBotError):
    """Base for errors raised by requests to `signal-cli-rest-api`."""
