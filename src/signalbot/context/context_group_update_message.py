from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.context.context import Context

if TYPE_CHECKING:
    from signalbot.api.receive_messages import GroupUpdateMessage
    from signalbot.bot import SignalBot


class ContextGroupUpdateMessage(Context):
    def __init__(self, bot: SignalBot, message: GroupUpdateMessage) -> None:
        self.bot = bot
        self.message = message
