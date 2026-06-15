from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.context.context import Context

if TYPE_CHECKING:
    from signalbot.api.receive_messages import Reaction
    from signalbot.bot import SignalBot


class ContextReaction(Context):
    def __init__(self, bot: SignalBot, message: Reaction) -> None:
        self.bot = bot
        self.message = message
