from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase
from signalbot.api.generated.api.send_reaction_request import SendReactionRequest
from signalbot.api.outgoing import SentMessage

if TYPE_CHECKING:
    import logging

    from signalbot.api import SignalAPI
    from signalbot.api.incoming import DataMessage
    from signalbot.recipients import RecipientResolver


class ReactionActions(BotActionsBase):
    def __init__(
        self,
        signal: SignalAPI,
        recipients: RecipientResolver,
        logger: logging.Logger,
        phone_number: str,
    ) -> None:
        super().__init__(signal, recipients, logger)
        self._phone_number = phone_number

    async def react(self, message: SentMessage | DataMessage, emoji: str) -> None:
        """React to a message with an emoji.

        Args:
            message: The message to react to.
            emoji: Emoji reaction value.
        """
        if isinstance(message, SentMessage):
            if message.recipient is None:
                error_msg = "Recipient must be set in SendMessage"
                raise ValueError(error_msg)
            recipient = message.recipient
            target_author = self._phone_number
        else:
            recipient = message.source_or_group_id()
            target_author = message.source_uuid or message.source_number

            if message.is_group():
                recipient = self._recipients.resolve(recipient)

                if target_author is None:
                    error_msg = "Cannot react to group message without source uuid"
                    raise ValueError(error_msg)
            elif target_author is None:
                error_msg = "Message does not contain a source"
                raise ValueError(error_msg)

        reaction_request = SendReactionRequest(
            recipient=recipient,
            reaction=emoji,
            target_author=target_author,
            timestamp=message.timestamp,
        )
        await self._signal.reactions.react(reaction_request)
        self._logger.info(f"[Bot] New reaction: {emoji}")  # noqa: G004
