from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import logging

    from signalbot._client import SignalAPI
    from signalbot._recipients import RecipientResolver


class BotActionsBase:
    """Shared dependencies for a `SignalBot` action namespace (e.g. `bot.messages`)."""

    def __init__(
        self,
        signal: SignalAPI,
        recipients: RecipientResolver,
        logger: logging.Logger,
    ) -> None:
        self._signal = signal
        self._recipients = recipients
        self._logger = logger
