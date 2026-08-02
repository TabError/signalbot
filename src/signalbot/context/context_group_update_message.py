from __future__ import annotations

from signalbot.api.receive_messages import GroupUpdateMessage
from signalbot.context.context import Context


class ContextGroupUpdateMessage(Context[GroupUpdateMessage]):
    pass
