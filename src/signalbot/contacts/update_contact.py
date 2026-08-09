from __future__ import annotations

from pydantic import BaseModel

from signalbot._generated import UpdateContactRequest


class UpdateContact(BaseModel):
    """The fields to change on a contact, passed to `bot.contacts.update`."""

    expiration_in_seconds: int | None = None
    name: str | None = None
    recipient: str | None = None

    def to_generated(self) -> UpdateContactRequest:
        if self.recipient is None:
            error_msg = "Recipient must be set in UpdateContact"
            raise ValueError(error_msg)
        return UpdateContactRequest(
            expiration_in_seconds=self.expiration_in_seconds,
            name=self.name,
            recipient=self.recipient,
        )
