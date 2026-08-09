from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase
from signalbot._generated import Receipt

if TYPE_CHECKING:
    from signalbot.messages import DataMessage, EditMessage
    from signalbot.receipts import ReceiptType


class ReceiptActions(BotActionsBase):
    async def send(
        self,
        message: DataMessage | EditMessage,
        receipt_type: ReceiptType,
    ) -> None:
        """Send a read or viewed receipt for a message if supported.

        Args:
            message: The message to acknowledge.
            receipt_type: The receipt type to send.
        """
        if message.is_group():
            self._logger.warning("[Bot] Receipts are not supported for groups")
            return

        recipient = self._recipients.resolve(message.source_or_group_id())
        receipt_request = Receipt(
            recipient=recipient, receipt_type=receipt_type, timestamp=message.timestamp
        )
        await self._signal.receipts.send(receipt_request)
        self._logger.info("[Bot] Receipt: %s", receipt_type)
