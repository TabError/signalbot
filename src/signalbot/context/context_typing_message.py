from __future__ import annotations

from signalbot.api.receive_messages import TypingMessage
from signalbot.context.context import Context


class ContextTypingMessage(Context[TypingMessage]):
    pass
