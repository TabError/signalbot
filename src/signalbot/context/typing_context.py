from __future__ import annotations

from signalbot.api.incoming import TypingMessage
from signalbot.context.context import Context


class TypingContext(Context[TypingMessage]):
    pass
