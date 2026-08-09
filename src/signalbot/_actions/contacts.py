from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.contacts import UpdateContact


class ContactActions(BotActionsBase):
    async def update(
        self,
        update_contact: UpdateContact,
    ) -> None:
        """Update a contact's metadata.

        Args:
            update_contact: Contact update payload.
        """
        if update_contact.recipient is None:
            error_msg = "Recipient must be set in UpdateContact"
            raise ValueError(error_msg)
        update_contact.recipient = self._recipients.resolve(update_contact.recipient)
        await self._signal.contacts.update(update_contact)
