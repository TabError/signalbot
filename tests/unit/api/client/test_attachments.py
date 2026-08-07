import base64

import aiohttp
import pytest
from pytest_mock import MockerFixture

from signalbot import SignalAPI
from signalbot.api.incoming import Attachment

HTTP_OK = 200


class TestAttachments:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

    @pytest.fixture(autouse=True)
    def _use_signal_api(self, signal_api: SignalAPI) -> None:
        self.signal_api = signal_api

    def _mock_json_response(
        self, mocker: MockerFixture, verb: str, payload: dict | list
    ):
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
    async def test_download_attachment(self, mocker: MockerFixture):
        mock = mocker.patch("aiohttp.ClientSession.get", new_callable=mocker.AsyncMock)
        content_mock = mocker.AsyncMock()
        content_mock.return_value = b"file content"
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            content=mocker.Mock(read=content_mock),
        )

        attachment = Attachment(local_filename="my-file.png")
        result = await self.signal_api.attachments.download(attachment)

        assert result == base64.b64encode(b"file content").decode("utf-8")

    @pytest.mark.asyncio
    async def test_delete_attachment(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "delete", {})

        attachment = Attachment(local_filename="my-file.png")
        await self.signal_api.attachments.delete(attachment)

        assert mock.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_attachment_without_local_filename_raises(self):
        attachment = Attachment(local_filename=None)

        with pytest.raises(ValueError, match="no local filename"):
            await self.signal_api.attachments.delete(attachment)
