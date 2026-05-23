from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from signalbot.api.generated import MessageMention
from signalbot.context.context_data_message import ContextDataMessage

if TYPE_CHECKING:
    from signalbot.api.generated import Mention
    from signalbot.api.receive_messages import EditMessage
    from signalbot.api.requests import SendMessage, SentMessage
    from signalbot.bot import SignalBot


class ContextEditMessage(ContextDataMessage):
    def __init__(self, bot: SignalBot, message: EditMessage) -> None:
        super().__init__(bot, message)
        self.message: EditMessage = message
