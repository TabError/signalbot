from __future__ import annotations

from signalbot.api.incoming import GroupUpdate
from signalbot.context.context import Context


class GroupUpdateContext(Context[GroupUpdate]):
    pass
