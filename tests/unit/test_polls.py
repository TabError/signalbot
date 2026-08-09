from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from signalbot._generated import CreatePollRequest
from signalbot.polls import CreatedPoll
from tests.conftest import GROUP_ID
from tests.unit.conftest import TestCommon


@dataclass
class PollCase:
    recipient: str
    question: str
    answers: list[str]
    allow_multiple: bool
    timestamp: int


class TestPoll(TestCommon):
    @pytest.mark.parametrize(
        "case",
        [
            PollCase(
                recipient="+49987654321",
                question="What's your favorite color?",
                answers=["Red", "Blue", "Green"],
                allow_multiple=False,
                timestamp=1633169000000,
            ),
            PollCase(
                recipient=GROUP_ID,
                question="What should we do?",
                answers=["Option A", "Option B"],
                allow_multiple=False,
                timestamp=1633169000001,
            ),
            PollCase(
                recipient="+49987654321",
                question="Which colors do you like?",
                answers=["Red", "Blue", "Green", "Yellow"],
                allow_multiple=True,
                timestamp=1633169000002,
            ),
        ],
        ids=["phone_number", "group_id", "multiple_selections"],
    )
    async def test_poll(self, mocker: MockerFixture, case: PollCase):
        poll_mock = mocker.AsyncMock(
            return_value=mocker.Mock(timestamp=str(case.timestamp))
        )
        mocker.patch.object(self.signal_bot._signal.polls, "create", poll_mock)

        create_poll_request = CreatePollRequest(
            recipient=case.recipient,
            question=case.question,
            answers=case.answers,
            allow_multiple_selections=case.allow_multiple,
        )
        result = await self.signal_bot.polls.create(create_poll_request)

        assert isinstance(result, CreatedPoll)
        assert result.timestamp == case.timestamp
        poll_mock.assert_called_once_with(create_poll_request)
