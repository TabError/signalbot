from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.api.incoming import Attachment


class AttachmentActions(BotActionsBase):
    async def delete(self, attachment: Attachment) -> None:
        """Delete an attachment from local storage.

        Args:
            attachment: Attachment to delete.
        """
        await self._signal.attachments.delete_attachment(attachment)
