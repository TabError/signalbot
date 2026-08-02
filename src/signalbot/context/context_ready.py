from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from signalbot.bot import SignalBot


class ContextReady:
    """
    Context passed to `ReadyHandler.handle_ready`. Unlike the other contexts, there
    is no originating message, so this only gives access to the bot.
    """

    def __init__(self, bot: SignalBot) -> None:
        self.bot = bot
