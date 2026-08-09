from __future__ import annotations

from pydantic import BaseModel

from signalbot._generated import CreatePollRequest


class CreatePoll(BaseModel):
    """The fields to create a poll with, passed to `bot.polls.create`."""

    allow_multiple_selections: bool | None = None
    answers: list[str]
    question: str
    recipient: str | None = None

    def to_generated(self) -> CreatePollRequest:
        if self.recipient is None:
            error_msg = "Recipient must be set in CreatePoll"
            raise ValueError(error_msg)
        return CreatePollRequest(
            allow_multiple_selections=self.allow_multiple_selections,
            answers=self.answers,
            question=self.question,
            recipient=self.recipient,
        )


class CreatedPoll(CreatePoll):
    """A poll after it was successfully created, with its send timestamp attached."""

    timestamp: int

    @classmethod
    def from_create_poll_request(
        cls, create_poll_request: CreatePoll, timestamp: int
    ) -> CreatedPoll:
        return cls.model_construct(
            **create_poll_request.model_dump(), timestamp=timestamp
        )
