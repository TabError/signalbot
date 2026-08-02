from __future__ import annotations

from signalbot.api.incoming import GroupUpdateMessage
from signalbot.context.context import Context


class GroupUpdateContext(Context[GroupUpdateMessage]):
    pass
