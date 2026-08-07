from __future__ import annotations


class SignalBotError(Exception):
    @classmethod
    def cannot_resolve_recipient(cls) -> SignalBotError:
        """Raised when a phone number, UUID, username, or group id/name can't
        be resolved to a UUID or group id.
        """
        return cls("Cannot resolve recipient.")


class SignalAPIError(SignalBotError):
    """Base for errors raised by requests to `signal-cli-rest-api`."""
