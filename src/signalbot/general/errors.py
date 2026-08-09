from __future__ import annotations

from signalbot.errors import SignalAPIError


class HealthCheckError(SignalAPIError):
    """Raised when the `signal-cli-rest-api` health check endpoint fails."""


class AboutError(SignalAPIError):
    """Raised when fetching `signal-cli-rest-api` version/capability info fails."""


__all__ = [
    "AboutError",
    "HealthCheckError",
]
