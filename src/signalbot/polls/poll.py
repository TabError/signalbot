from __future__ import annotations

from signalbot._generated import CreatePollRequest


class CreatedPoll(CreatePollRequest):
    """A poll after it was successfully created, with its send timestamp attached."""

    timestamp: int

    @classmethod
    def from_create_poll_request(
        cls, create_poll_request: CreatePollRequest, timestamp: int
    ) -> CreatedPoll:
        return cls.model_construct(
            **create_poll_request.model_dump(), timestamp=timestamp
        )
