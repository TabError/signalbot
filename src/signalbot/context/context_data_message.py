from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from signalbot.api.generated import MessageMention, RemoteDeleteRequest
from signalbot.context.context import Context

if TYPE_CHECKING:
    from signalbot.api.generated.api.receipt_type import ReceiptType
    from signalbot.api.generated.receive import Mention
    from signalbot.api.receive_messages import ReceiveDataMessage
    from signalbot.api.requests import SendMessage, SentMessage
    from signalbot.bot import SignalBot


class ContextDataMessage(Context):
    def __init__(self, bot: SignalBot, message: ReceiveDataMessage) -> None:
        self.bot = bot
        self.message = message

    async def edit(
        self, new_message: SendMessage, original_message: SentMessage
    ) -> SentMessage:
        """Same as
         [signalbot.SignalBot.send()](bot.md#signalbot.SignalBot.send)
        but with the original_message and recipient set to the message's."""
        new_message = deepcopy(new_message)
        new_message.recipient = self.message.source_or_group_uuid()
        return await self.bot.edit(new_message, original_message)

    async def reply(
        self,
        message: SendMessage,
    ) -> SentMessage:
        """Same as
         [signalbot.SignalBot.send()](bot.md#signalbot.SignalBot.send)
        but with the quote arguments set to the message's."""
        send_mentions = self._convert_receive_mentions_into_send_mentions(
            self.message.mentions,
        )
        message = deepcopy(message)
        message.recipient = self.message.source_or_group_uuid()
        message.quote_mentions = send_mentions
        message.quote_author = self.message.source
        message.quote_message = self.message.text
        message.quote_timestamp = self.message.timestamp

        return await self.bot.send(message)

    async def react(self, emoji: str) -> None:
        """Same as
         [signalbot.SignalBot.react()](bot.md#signalbot.SignalBot.react)
        but with the recipient set to the message's recipient."""
        await self.bot.react(self.message, emoji)

    async def remote_delete(self, timestamp: int) -> int:
        """Same as
        [signalbot.SignalBot.remote_delete()](bot.md#signalbot.SignalBot.remote_delete)
        but with the recipient and timestamp set to the message's."""
        remote_delete_request = RemoteDeleteRequest(
            recipient=self.message.source_or_group_uuid(),
            timestamp=timestamp,
        )
        return await self.bot.remote_delete(remote_delete_request)

    async def receipt(self, receipt_type: ReceiptType) -> None:
        """Same as
         [signalbot.SignalBot.receipt()](bot.md#signalbot.SignalBot.receipt)
        but with the recipient set to the message's recipient."""
        await self.bot.receipt(self.message, receipt_type)

    def _convert_receive_mentions_into_send_mentions(
        self,
        mentions: list[Mention] | None = None,
    ) -> list[MessageMention] | None:
        if mentions is None:
            return None

        return [
            MessageMention(
                author=mention.uuid,
                length=mention.length,
                start=mention.start,
            )
            for mention in mentions
        ]
