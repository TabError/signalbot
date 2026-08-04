from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.actions.base import BotActionsBase
from signalbot.api.outgoing import CreatedPoll

if TYPE_CHECKING:
    from signalbot.api.generated import CreatePollRequest


class PollActions(BotActionsBase):
    async def create(
        self,
        create_poll_request: CreatePollRequest,
    ) -> CreatedPoll:
        """Create a poll.

        Args:
            create_poll_request: Request payload for poll creation.

        Returns:
            A CreatedPoll instance.
        """
        create_poll_request.recipient = self._recipients.resolve(
            create_poll_request.recipient
        )

        created_poll = await self._signal.polls.create_poll(create_poll_request)
        timestamp = int(created_poll.timestamp)
        self._logger.info("[Bot] New poll created:\n%s", create_poll_request.question)

        return CreatedPoll.from_create_poll_request(create_poll_request, timestamp)
