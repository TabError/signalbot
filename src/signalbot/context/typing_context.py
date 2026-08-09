from __future__ import annotations

from signalbot.context.context import Context
from signalbot.messages import TypingMessage


class TypingContext(Context[TypingMessage]):
    """Context passed to `TypingHandler.handle_typing`."""
