from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase
from signalbot._generated import RemoteDeleteRequest, TypingIndicatorRequest
from signalbot.messages import SentMessage

if TYPE_CHECKING:
    import logging

    from signalbot._recipients import RecipientResolver
    from signalbot.client import SignalAPI
    from signalbot.messages import SendMessage, SendMessageMultiple


class MessageActions(BotActionsBase):
    def __init__(
        self,
        signal: SignalAPI,
        recipients: RecipientResolver,
        logger: logging.Logger,
        phone_number: str,
    ) -> None:
        super().__init__(signal, recipients, logger)
        self._phone_number = phone_number

    async def send(
        self,
        message: SendMessage,
        recipient: str,
    ) -> SentMessage:
        """Send or edit a message.

        Args:
            message: The message to send.
            recipient: The contact or group to send the message to.

        Returns:
            A SentMessage instance.
        """
        recipient = self._recipients.resolve(recipient)

        send_message_v2 = await message.to_generated(self._phone_number, recipient)
        send_message_response = await self._signal.messages.send(send_message_v2)
        timestamp = int(send_message_response.timestamp)
        self._logger.info("[Bot] New message %s sent:\n%s", timestamp, message.text)

        return SentMessage.from_send_message(message, recipient, timestamp)

    async def send_multiple(
        self,
        message: SendMessageMultiple,
    ) -> list[SentMessage]:
        """Send one message to multiple recipients.

        Args:
            message: The message payload with multiple recipients.

        Returns:
            A list of SentMessage instances, one per recipient.
        """
        message.recipients = [
            self._recipients.resolve(recipient) for recipient in message.recipients
        ]

        send_message_v2 = await message.to_generated(self._phone_number)
        send_message_response = await self._signal.messages.send(send_message_v2)
        timestamp = int(send_message_response.timestamp)

        self._logger.info("[Bot] New message %s sent:\n%s", timestamp, message.text)

        return SentMessage.from_send_message_multiple(message, timestamp)

    async def edit(
        self, new_message: SendMessage, original_message: SentMessage, recipient: str
    ) -> SentMessage:
        """Edit a message.

        Args:
            new_message: The message to send.
            original_message: The original message to edit.
            recipient: The contact or group the original message was sent to.

        Returns:
            A SentMessage instance.
        """
        new_message.edit_timestamp = original_message.timestamp
        return await self.send(new_message, recipient)

    async def remote_delete(
        self,
        sent_message: SentMessage,
    ) -> int:
        """Delete a previously sent message.

        Args:
            sent_message: The message to delete.

        Returns:
            The timestamp of the delete action.
        """
        remote_delete_request = RemoteDeleteRequest(
            recipient=self._recipients.resolve(sent_message.recipient),
            timestamp=sent_message.timestamp,
        )

        remote_delete_response = await self._signal.messages.remote_delete(
            remote_delete_request
        )
        ret_timestamp = int(remote_delete_response.timestamp)
        self._logger.info(
            "[Bot] Deleted message with timestamp %s",
            sent_message.timestamp,
        )

        return ret_timestamp

    async def start_typing(self, recipient: str) -> None:
        """Send a typing indicator to a recipient.

        Args:
            recipient: Message recipient.
        """
        recipient = self._recipients.resolve(recipient)
        await self._signal.messages.start_typing(
            TypingIndicatorRequest(recipient=recipient)
        )

    async def stop_typing(self, recipient: str) -> None:
        """Stop a typing indicator for a recipient.

        Args:
            recipient: Message recipient.
        """
        recipient = self._recipients.resolve(recipient)
        await self._signal.messages.stop_typing(
            TypingIndicatorRequest(recipient=recipient)
        )
