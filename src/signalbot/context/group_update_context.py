from __future__ import annotations

from signalbot.api.incoming import GroupUpdate
from signalbot.context.context import Context


class GroupUpdateContext(Context[GroupUpdate]):
    """Context passed to `GroupUpdateHandler.handle_group_update`."""
