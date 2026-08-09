from __future__ import annotations

from signalbot.errors import SignalAPIError


class GetGroupsError(SignalAPIError):
    """Raised when fetching group data from the API fails."""


class UpdateGroupError(SignalAPIError):
    """Raised when the API rejects a group metadata update."""


__all__ = [
    "GetGroupsError",
    "UpdateGroupError",
]
