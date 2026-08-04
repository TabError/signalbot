from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from signalbot.actions import (
        AttachmentActions,
        ContactActions,
        MessageActions,
        ReactionActions,
        ReceiptActions,
    )
    from signalbot.groups import GroupRegistry


class BotProtocol(Protocol):
    """The bot action surface used by `Context` and `MessagePipeline`.

    Used to avoid circular imports between them.
    """

    messages: MessageActions
    contacts: ContactActions
    groups: GroupRegistry
    reactions: ReactionActions
    receipts: ReceiptActions
    attachments: AttachmentActions

    def request_stop(self) -> None: ...
