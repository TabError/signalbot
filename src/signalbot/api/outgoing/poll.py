from __future__ import annotations

from signalbot.api.generated import CreatePollRequest


class CreatedPoll(CreatePollRequest):
    timestamp: int

    @classmethod
    def from_create_poll_request(
        cls, create_poll_request: CreatePollRequest, timestamp: int
    ) -> CreatedPoll:
        return cls.model_construct(
            **create_poll_request.model_dump(), timestamp=timestamp
        )
