import base64

import aiohttp
import pytest
from pytest_mock import MockerFixture

from signalbot import SignalAPI
from signalbot.api.generated import SendMessageV2
from signalbot.auth import Authentication, BasicAuthentication, BearerAuthentication


class TestAuth:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"
    group_id = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="

    async def _send_with_auth_helper(
        self, mocker: MockerFixture, auth: Authentication | None
    ) -> None:
        signal_api = SignalAPI(self.signal_service, self.phone_number, auth=auth)

        status_code = 201
        mock2 = mocker.AsyncMock()
        mock2.return_value = {"timestamp": "1638715559464"}

        mock_session = mocker.AsyncMock()
        mock_session.post.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status_code=status_code,
            json=mock2,
        )

        mocker.patch("aiohttp.ClientSession", return_value=mock_session)

        data_message = SendMessageV2(
            message="Hello World!",
            number=self.phone_number,
            recipients=[self.group_id],
        )

        resp = await signal_api.messages.send(data_message)

        _, kwargs = mock_session.post.call_args

        assert resp.timestamp == "1638715559464"
        return kwargs["headers"].get("Authorization")

    @pytest.mark.asyncio
    async def test_send_with_basic_auth(self, mocker: MockerFixture):
        username = "user"
        password = "pw"

        credentials = f"{username}:{password}".encode()
        credential_string = base64.b64encode(credentials).decode("utf-8")

        auth = BasicAuthentication(username=username, password=password)

        auth_header = await self._send_with_auth_helper(mocker, auth)

        assert auth_header == f"Basic {credential_string}"

    @pytest.mark.asyncio
    async def test_send_with_bearer_auth(self, mocker: MockerFixture):
        token = "token"

        auth = BearerAuthentication(token=token)

        auth_header = await self._send_with_auth_helper(mocker, auth)

        assert auth_header == f"Bearer {token}"

    @pytest.mark.asyncio
    async def test_send_without_auth(self, mocker: MockerFixture):
        auth_header = await self._send_with_auth_helper(mocker, None)

        assert auth_header is None
