from __future__ import annotations

from signalbot.context.context import Context
from signalbot.groups import GroupUpdate


class GroupUpdateContext(Context[GroupUpdate]):
    """Context passed to `GroupUpdateHandler.handle_group_update`."""
