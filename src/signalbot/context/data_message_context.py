from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

from signalbot.api.generated import MessageMention, RemoteDeleteRequest
from signalbot.api.incoming import DataMessage, EditMessage
from signalbot.context.context import Context

if TYPE_CHECKING:
    from signalbot.api.generated.api.receipt_type import ReceiptType
    from signalbot.api.generated.receive import Mention
    from signalbot.api.incoming import Attachment
    from signalbot.api.outgoing import SendMessage, SentMessage


class DataMessageContext(Context[DataMessage | EditMessage]):
    async def edit(
        self, new_message: SendMessage, original_message: SentMessage
    ) -> SentMessage:
        """Same as
         [signalbot.MessageActions.edit()](bot.md#signalbot.actions.MessageActions.edit)
        but with the original_message and recipient set to the message's."""
        new_message = deepcopy(new_message)
        new_message.recipient = self.message.source_or_group_id()
        return await self.bot.messages.edit(new_message, original_message)

    async def reply(
        self,
        message: SendMessage,
    ) -> SentMessage:
        """Same as
         [signalbot.MessageActions.send()](bot.md#signalbot.actions.MessageActions.send)
        but with the quote arguments set to the message's."""
        send_mentions = self._convert_receive_mentions_into_send_mentions(
            self.message.mentions,
        )
        message = deepcopy(message)
        message.recipient = self.message.source_or_group_id()
        message.quote_mentions = send_mentions
        message.quote_author = self.message.source_uuid or self.message.source_number
        message.quote_text = self.message.text
        message.quote_timestamp = self.message.timestamp

        return await self.bot.messages.send(message)

    async def react(self, emoji: str) -> None:
        """Same as
         [signalbot.ReactionActions.react()](bot.md#signalbot.actions.ReactionActions.react)
        but with the recipient set to the message's recipient."""
        await self.bot.reactions.react(self.message, emoji)

    async def remote_delete(self, timestamp: int) -> int:
        """Same as
        [signalbot.MessageActions.remote_delete()](bot.md#signalbot.actions.MessageActions.remote_delete)
        but with the recipient and timestamp set to the message's."""
        remote_delete_request = RemoteDeleteRequest(
            recipient=self.message.source_or_group_id(),
            timestamp=timestamp,
        )
        return await self.bot.messages.remote_delete(remote_delete_request)

    async def send_receipt(self, receipt_type: ReceiptType) -> None:
        """Same as
         [signalbot.ReceiptActions.send()](bot.md#signalbot.actions.ReceiptActions.send)
        but with the recipient set to the message's recipient."""
        await self.bot.receipts.send(self.message, receipt_type)

    async def delete_attachment(self, attachment: Attachment) -> None:
        """Same as
        [signalbot.AttachmentActions.delete()](bot.md#signalbot.actions.AttachmentActions.delete)."""
        await self.bot.attachments.delete(attachment)

    def _convert_receive_mentions_into_send_mentions(
        self,
        mentions: list[Mention] | None = None,
    ) -> list[MessageMention] | None:
        if mentions is None:
            return None

        send_mentions = []

        for mention in mentions:
            if mention.uuid is None:
                self._logger.warning(
                    "Received a mention with no uuid, skipping it.",
                )
                continue

            send_mentions.append(
                MessageMention(
                    author=mention.uuid,
                    length=mention.length,
                    start=mention.start,
                )
            )

        if len(send_mentions) == 0:
            return None

        return send_mentions
