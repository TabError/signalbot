from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase
from signalbot.api.generated import TypingIndicatorRequest
from signalbot.api.outgoing import SentMessage

if TYPE_CHECKING:
    import logging

    from signalbot.api import SignalAPI
    from signalbot.api.generated import RemoteDeleteRequest
    from signalbot.api.outgoing import SendMessage, SendMessageMultiple
    from signalbot.recipients import RecipientResolver


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
    ) -> SentMessage:
        """Send or edit a message.

        Args:
            message: The message to send.

        Returns:
            A SentMessage instance.
        """
        if message.recipient is None:
            error_msg = "Recipient must be set in SendMessage"
            raise ValueError(error_msg)
        message.recipient = self._recipients.resolve(message.recipient)

        send_message_v2 = await message.to_generated(self._phone_number)
        send_message_response = await self._signal.messages.send(send_message_v2)
        timestamp = int(send_message_response.timestamp)
        self._logger.info(
            f"[Bot] New message {timestamp} sent:\n{message.text}"  # noqa: G004
        )

        return SentMessage.from_send_message(message, timestamp)

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

        self._logger.info(
            f"[Bot] New message {timestamp} sent:\n{message.text}"  # noqa: G004
        )

        return SentMessage.from_send_message_multiple(message, timestamp)

    async def edit(
        self, new_message: SendMessage, original_message: SentMessage
    ) -> SentMessage:
        """Edit a message.

        Args:
            new_message: The message to send.
            original_message: The original message to edit.

        Returns:
            A SentMessage instance.
        """
        new_message.edit_timestamp = original_message.timestamp
        return await self.send(new_message)

    async def remote_delete(
        self,
        remote_delete_request: RemoteDeleteRequest,
    ) -> int:
        """Delete a previously sent message.

        Args:
            remote_delete_request: Request payload for remote delete.

        Returns:
            The timestamp of the delete action.
        """
        remote_delete_request.recipient = self._recipients.resolve(
            remote_delete_request.recipient
        )

        remote_delete_response = await self._signal.messages.remote_delete(
            remote_delete_request
        )
        ret_timestamp = int(remote_delete_response.timestamp)
        self._logger.info(
            f"[Bot] Deleted message with timestamp {remote_delete_request.timestamp}"  # noqa: G004
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
