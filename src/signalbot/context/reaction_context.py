from __future__ import annotations

from signalbot.api.incoming import Reaction
from signalbot.context.context import Context


class ReactionContext(Context[Reaction]):
    pass
