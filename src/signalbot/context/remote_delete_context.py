from __future__ import annotations

from signalbot.context.context import Context
from signalbot.messages import RemoteDelete


class RemoteDeleteContext(Context[RemoteDelete]):
    """Context passed to `RemoteDeleteHandler.handle_remote_delete`."""
