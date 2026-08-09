from __future__ import annotations

from pydantic import BaseModel, Field

from signalbot._generated import UpdateContactRequest


class UpdateContact(BaseModel):
    """The fields to change on a contact, passed to `bot.contacts.update`."""

    expiration_in_seconds: int | None = Field(
        default=None,
        description="The new disappearing message timer in seconds. "
        "`None` leaves it unchanged, `0` disables it.",
    )
    name: str | None = Field(default=None, description="The new name of the contact.")
    recipient: str | None = Field(
        default=None, description="The recipient of the contact to update."
    )

    def to_generated(self) -> UpdateContactRequest:
        if self.recipient is None:
            error_msg = "Recipient must be set in UpdateContact"
            raise ValueError(error_msg)
        return UpdateContactRequest(
            expiration_in_seconds=self.expiration_in_seconds,
            name=self.name,
            recipient=self.recipient,
        )
