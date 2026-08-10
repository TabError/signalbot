from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._actions.base import BotActionsBase
from signalbot.polls import CreatedPoll

if TYPE_CHECKING:
    from signalbot.polls import CreatePoll


class PollActions(BotActionsBase):
    async def create(
        self,
        create_poll_request: CreatePoll,
        recipient: str,
    ) -> CreatedPoll:
        """Create a poll.

        Args:
            create_poll_request: The fields to create the poll with.
            recipient: The contact or group to send the poll to.

        Returns:
            A CreatedPoll instance.
        """
        recipient = self._recipients.resolve(recipient)

        wire_request = create_poll_request.to_generated(recipient)
        created_poll = await self._signal.polls.create(wire_request)
        timestamp = int(created_poll.timestamp)
        self._logger.info("[Bot] New poll created:\n%s", create_poll_request.question)

        return CreatedPoll.from_create_poll_request(
            create_poll_request, recipient, timestamp
        )
