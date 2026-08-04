from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.api.outgoing import UpdateContact


class ContactActions(BotActionsBase):
    async def update(
        self,
        update_contact: UpdateContact,
    ) -> None:
        """Update a contact's metadata.

        Args:
            update_contact: Contact update payload.
        """
        update_contact.recipient = self._recipients.resolve(update_contact.recipient)
        await self._signal.contacts.update_contact(update_contact)
