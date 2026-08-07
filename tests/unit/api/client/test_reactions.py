from collections.abc import Callable

from pytest_mock import MockType

from signalbot import SignalAPI
from signalbot.api.generated import SendReactionRequest
from tests.conftest import GROUP_ID, PHONE_NUMBER
from tests.unit.api.client.conftest import HTTP_OK


async def test_react(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock = mock_json_response("post", {})

    request = SendReactionRequest(
        reaction="🎉",
        recipient=GROUP_ID,
        target_author=PHONE_NUMBER,
        timestamp=1638715559464,
    )
    resp = await signal_api.reactions.react(request)

    assert mock.call_count == 1
    assert resp.status == HTTP_OK
