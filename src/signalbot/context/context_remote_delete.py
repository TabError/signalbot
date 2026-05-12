from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.context.context import Context

if TYPE_CHECKING:
    from signalbot.api.receive_messages import RemoteDelete
    from signalbot.bot import SignalBot


class ContextRemoteDelete(Context):
    def __init__(self, bot: SignalBot, message: RemoteDelete) -> None:
        self.bot = bot
        self.message = message
