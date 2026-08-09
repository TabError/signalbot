from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.attachments import Attachment


class AttachmentActions(BotActionsBase):
    async def delete(self, attachment: Attachment) -> None:
        """Delete an attachment from local storage.

        Args:
            attachment: Attachment to delete.
        """
        await self._signal.attachments.delete(attachment)
