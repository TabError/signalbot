from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from signalbot.api.receive_messages import ReceivedMessageType
    from signalbot.api.requests import (
        SendMessage,
        SentMessage,
        UpdateContactRequest,
        UpdateGroupRequest,
    )
    from signalbot.bot import SignalBot


class Context:
    """
    Context is a helper class that provides methods to reply, edit, react, etc. to a
    message. This is useful to avoid having to pass the recipient and other arguments to
    the bot's methods manually.
    """

    def __init__(self, bot: SignalBot, message: ReceivedMessageType) -> None:
        self.bot = bot
        self.message = message

    async def send(
        self,
        data_message: SendMessage,
    ) -> SentMessage:
        """Same as
         [signalbot.SignalBot.send()](bot.md#signalbot.SignalBot.send)
        but with the recipient set to the message's recipient."""
        data_message.recipient = self.message.source_or_group_uuid()
        return await self.bot.send(data_message)

    async def start_typing(self) -> None:
        """Same as
        [signalbot.SignalBot.start_typing()](bot.md#signalbot.SignalBot.start_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.start_typing(self.message.source_or_group_uuid())

    async def stop_typing(self) -> None:
        """Same as
        [signalbot.SignalBot.stop_typing()](bot.md#signalbot.SignalBot.stop_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.stop_typing(self.message.source_or_group_uuid())

    async def update_contact(
        self, update_contact_request: UpdateContactRequest
    ) -> None:
        """Same as
        [signalbot.SignalBot.update_contact()](bot.md#signalbot.SignalBot.update_contact)
         but with the recipient set to the message's recipient."""
        if self.message.is_group():
            error_msg = "Cannot update contact for a group message"
            raise ValueError(error_msg)
        update_contact_request.recipient = self.message.source_or_group_uuid()
        await self.bot.update_contact(update_contact_request)

    async def update_group(
        self,
        update_group_request: UpdateGroupRequest,
    ) -> None:
        """Same as
        [signalbot.SignalBot.update_group()](bot.md#signalbot.SignalBot.update_group)
         but with the group id or name set to the message's recipient."""
        if self.message.is_private():
            error_msg = "Cannot update group for a private message"
            raise ValueError(error_msg)
        update_group_request.group_id_or_name = self.message.source_or_group_uuid()
        await self.bot.update_group(update_group_request)
