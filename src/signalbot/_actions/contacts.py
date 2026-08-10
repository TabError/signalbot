from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase

if TYPE_CHECKING:
    from signalbot.contacts import UpdateContact


class ContactActions(BotActionsBase):
    async def update(
        self,
        update_contact: UpdateContact,
        recipient: str,
    ) -> None:
        """Update a contact's metadata.

        Args:
            update_contact: Contact update payload.
            recipient: The contact to update.
        """
        recipient = self._recipients.resolve(recipient)
        wire_request = update_contact.to_generated(recipient)
        await self._signal.contacts.update(wire_request)
