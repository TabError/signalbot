from collections.abc import Callable

from pytest_mock import MockerFixture, MockType

from signalbot._generated import (
    CreatePollRequest,
    RemoteDeleteRequest,
    SendMessageV2,
    TypingIndicatorRequest,
)
from signalbot.client import SignalAPI
from tests.conftest import GROUP_ID, PHONE_NUMBER
from tests.unit.client.conftest import HTTP_OK


async def test_send(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    expected_timestamp = "1638715559464"
    mock_json_response("post", {"timestamp": expected_timestamp})

    data_message = SendMessageV2(
        message="Hello World!",
        number=PHONE_NUMBER,
        recipients=[GROUP_ID],
    )
    resp = await signal_api.messages.send(data_message)

    assert resp.timestamp == expected_timestamp


async def test_poll(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock_json_response("post", {"timestamp": "1774791959123"})

    create_poll_request = CreatePollRequest(
        recipient=GROUP_ID,
        question="How much is the fish?",
        answers=["hyper hyper", "3,80 DM"],
        allow_multiple_selections=False,
    )
    resp = await signal_api.polls.create(create_poll_request)

    assert resp.timestamp == "1774791959123"


async def test_receive(signal_api: SignalAPI, mocker: MockerFixture):
    messages = ['{"id": 1}', '{"id": 2}']
    mock_iterator = mocker.AsyncMock()
    mock_iterator.__aiter__.return_value = messages
    mock = mocker.patch("websockets.connect")
    mock.return_value.__aenter__.return_value = mock_iterator

    results = [raw_message async for raw_message in signal_api.messages.receive()]

    assert results == messages


async def test_remote_delete(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    expected_timestamp = "1638715559464"
    mock_json_response("delete", {"timestamp": expected_timestamp})

    remote_delete_request = RemoteDeleteRequest(
        recipient=PHONE_NUMBER, timestamp=1638715559464
    )
    resp = await signal_api.messages.remote_delete(remote_delete_request)

    assert resp.timestamp == expected_timestamp


async def test_start_typing(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock = mock_json_response("put", {})

    request = TypingIndicatorRequest(recipient=PHONE_NUMBER)
    resp = await signal_api.messages.start_typing(request)

    assert mock.call_count == 1
    assert resp.status == HTTP_OK


async def test_stop_typing(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    mock = mock_json_response("delete", {})

    request = TypingIndicatorRequest(recipient=PHONE_NUMBER)
    resp = await signal_api.messages.stop_typing(request)

    assert mock.call_count == 1
    assert resp.status == HTTP_OK
