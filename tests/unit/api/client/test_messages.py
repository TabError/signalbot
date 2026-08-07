import aiohttp
import pytest
from pytest_mock import MockerFixture, MockType

from signalbot import SignalAPI
from signalbot.api.generated import (
    CreatePollRequest,
    RemoteDeleteRequest,
    SendMessageV2,
    TypingIndicatorRequest,
)

HTTP_OK = 200


class TestMessages:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"
    group_id = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="

    @pytest.fixture(autouse=True)
    def _use_signal_api(self, signal_api: SignalAPI) -> None:
        self.signal_api = signal_api

    def _mock_json_response(
        self, mocker: MockerFixture, verb: str, payload: dict | list
    ) -> MockType:
        mock2 = mocker.AsyncMock()
        mock2.return_value = payload
        mock = mocker.patch(
            f"aiohttp.ClientSession.{verb}", new_callable=mocker.AsyncMock
        )
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            json=mock2,
        )
        return mock

    @pytest.mark.asyncio
    async def test_send(self, mocker: MockerFixture):
        expected_timestamp = "1638715559464"
        self._mock_json_response(mocker, "post", {"timestamp": expected_timestamp})

        data_message = SendMessageV2(
            message="Hello World!",
            number=self.phone_number,
            recipients=[self.group_id],
        )
        resp = await self.signal_api.messages.send(data_message)

        assert resp.timestamp == expected_timestamp

    @pytest.mark.asyncio
    async def test_poll(self, mocker: MockerFixture):
        self._mock_json_response(mocker, "post", {"timestamp": "1774791959123"})

        recipient = self.group_id
        question = "How much is the fish?"
        answers = ["hyper hyper", "3,80 DM"]
        create_poll_request = CreatePollRequest(
            recipient=recipient,
            question=question,
            answers=answers,
            allow_multiple_selections=False,
        )
        resp = await self.signal_api.polls.create(create_poll_request)

        assert resp.timestamp == "1774791959123"

    @pytest.mark.asyncio
    async def test_receive(self, mocker: MockerFixture):
        message1 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 1","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'
        message2 = '{"envelope":{"source":"+4901234567890","sourceNumber":"+4901234567890","sourceUuid":"asdf","sourceName":"name","sourceDevice":1,"timestamp":1633169000000,"syncMessage":{"sentMessage":{"timestamp":1633169000000,"message":"Message 2","expiresInSeconds":0,"viewOnce":false,"mentions":[],"attachments":[],"contacts":[],"groupInfo":{"groupId":"group1","type":"DELIVER"},"destination":null,"destinationNumber":null,"destinationUuid":null}}}}'
        messages = [message1, message2]
        mock_iterator = mocker.AsyncMock()
        mock_iterator.__aiter__.return_value = messages
        mock = mocker.patch("websockets.connect")
        mock.return_value.__aenter__.return_value = mock_iterator

        results = [
            raw_message async for raw_message in self.signal_api.messages.receive()
        ]

        assert len(results) == len(messages)
        for i, _ in enumerate(results):
            assert messages[i] == results[i]

    @pytest.mark.asyncio
    async def test_remote_delete(self, mocker: MockerFixture):
        expected_timestamp = "1638715559464"
        self._mock_json_response(mocker, "delete", {"timestamp": expected_timestamp})

        remote_delete_request = RemoteDeleteRequest(
            recipient=self.phone_number, timestamp=1638715559464
        )
        resp = await self.signal_api.messages.remote_delete(remote_delete_request)

        assert resp.timestamp == expected_timestamp

    @pytest.mark.asyncio
    async def test_start_typing(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "put", {})

        request = TypingIndicatorRequest(recipient=self.phone_number)
        resp = await self.signal_api.messages.start_typing(request)

        assert mock.call_count == 1
        assert resp.status == HTTP_OK

    @pytest.mark.asyncio
    async def test_stop_typing(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "delete", {})

        request = TypingIndicatorRequest(recipient=self.phone_number)
        resp = await self.signal_api.messages.stop_typing(request)

        assert mock.call_count == 1
        assert resp.status == HTTP_OK
