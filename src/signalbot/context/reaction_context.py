from __future__ import annotations

from signalbot.context.context import Context
from signalbot.reactions import Reaction


class ReactionContext(Context[Reaction]):
    """Context passed to `ReactionHandler.handle_reaction`."""
