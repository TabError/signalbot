import pytest
from pytest_mock import MockerFixture

from signalbot import Command, text_triggered
from signalbot.api.requests import SendMessage
from signalbot.context import ContextDataMessage
from signalbot.test_utils import ChatTestCase, mock_chat


class SchnickSchnackSchnuckCommand(Command):
    @text_triggered("schnick", "schnack")
    async def handle(self, context: ContextDataMessage) -> None:
        text = context.message.text
        if text == "schnick":
            await context.send(SendMessage(text="schnack"))

        if text == "schnack":
            await context.send(SendMessage(text="schnuck"))


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore:There is no current event loop:DeprecationWarning")
class TestSchnickSchnackSchnuckCommand(ChatTestCase):
    @pytest.fixture(autouse=True)
    def setup(self):
        super().setup()
        self.signal_bot.register(SchnickSchnackSchnuckCommand())

    @mock_chat("schnick")
    async def test_schnick(
        self,
        mocker: MockerFixture,  # noqa: ARG002
        *args: object,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ):
        replies = self.signal_bot._signal.send
        assert replies.call_count == 1
        assert len(replies.results()) == 1
        for sent in replies.results():
            assert sent.recipients == [ChatTestCase.group_id]
            assert sent.message == "schnack"

    @mock_chat("schnack")
    async def test_schnack(
        self,
        mocker: MockerFixture,  # noqa: ARG002
        *args: object,  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ):
        replies = self.signal_bot._signal.send
        assert replies.call_count == 1
        assert len(replies.results()) == 1
        for sent in replies.results():
            assert sent.recipients == [ChatTestCase.group_id]
            assert sent.message == "schnuck"
