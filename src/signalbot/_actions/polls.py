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
    ) -> CreatedPoll:
        """Create a poll.

        Args:
            create_poll_request: The fields to create the poll with.

        Returns:
            A CreatedPoll instance.
        """
        create_poll_request.recipient = self._recipients.resolve(
            create_poll_request.recipient
        )

        created_poll = await self._signal.polls.create(create_poll_request)
        timestamp = int(created_poll.timestamp)
        self._logger.info("[Bot] New poll created:\n%s", create_poll_request.question)

        return CreatedPoll.from_create_poll_request(create_poll_request, timestamp)
