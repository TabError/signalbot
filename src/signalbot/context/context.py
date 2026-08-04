from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Generic, TypeVar

from signalbot.logger import LOGGER_NAME

if TYPE_CHECKING:
    from signalbot.api.incoming import ReceivedMessage
    from signalbot.api.outgoing import (
        SendMessage,
        SentMessage,
        UpdateContact,
        UpdateGroup,
    )
    from signalbot.bot_protocol import BotProtocol

MessageT = TypeVar("MessageT", bound="ReceivedMessage")


class Context(Generic[MessageT]):
    """
    Context is a helper class that provides methods to reply, edit, react, etc. to a
    message. This is useful to avoid having to pass the recipient and other arguments to
    the bot's methods manually.
    """

    def __init__(self, bot: BotProtocol, message: MessageT) -> None:
        self.bot = bot
        self.message = message
        self._logger = logging.getLogger(LOGGER_NAME)

    async def send(
        self,
        message: SendMessage,
    ) -> SentMessage:
        """Same as
         [signalbot.MessageActions.send()](bot.md#signalbot.actions.MessageActions.send)
        but with the recipient set to the message's recipient."""
        message.recipient = self.message.source_or_group_uuid()
        return await self.bot.messages.send(message)

    async def start_typing(self) -> None:
        """Same as
        [signalbot.MessageActions.start_typing()](bot.md#signalbot.actions.MessageActions.start_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.messages.start_typing(self.message.source_or_group_uuid())

    async def stop_typing(self) -> None:
        """Same as
        [signalbot.MessageActions.stop_typing()](bot.md#signalbot.actions.MessageActions.stop_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.messages.stop_typing(self.message.source_or_group_uuid())

    async def update_contact(self, update_contact: UpdateContact) -> None:
        """Same as
        [signalbot.ContactActions.update()](bot.md#signalbot.actions.ContactActions.update)
         but with the recipient set to the message's recipient."""
        if self.message.is_group():
            error_msg = "Cannot update contact for a group message"
            raise ValueError(error_msg)
        update_contact.recipient = self.message.source_or_group_uuid()
        await self.bot.contacts.update(update_contact)

    async def update_group(
        self,
        update_group: UpdateGroup,
    ) -> None:
        """Same as
        [signalbot.GroupRegistry.update()](bot.md#signalbot.groups.GroupRegistry.update)
         but with the group id or name set to the message's recipient."""
        if self.message.is_private():
            error_msg = "Cannot update group for a private message"
            raise ValueError(error_msg)
        update_group.group_id_or_name = self.message.source_or_group_uuid()
        await self.bot.groups.update(update_group)
