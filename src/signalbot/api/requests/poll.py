from __future__ import annotations

from copy import deepcopy

from signalbot.api.generated import CreatePollRequest


class Poll(CreatePollRequest):
    timestamp: int

    @classmethod
    def from_create_poll_request(
        cls, create_poll_request: CreatePollRequest, timestamp: int
    ) -> Poll:
        create_poll_request = deepcopy(create_poll_request)
        return cls(
            allow_multiple_selections=create_poll_request.allow_multiple_selections,
            answers=create_poll_request.answers,
            question=create_poll_request.question,
            recipient=create_poll_request.recipient,
            timestamp=timestamp,
        )
