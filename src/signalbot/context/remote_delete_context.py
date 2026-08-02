from __future__ import annotations

from signalbot.api.incoming import RemoteDelete
from signalbot.context.context import Context


class RemoteDeleteContext(Context[RemoteDelete]):
    pass
