import aiohttp
import pytest
from pytest_mock import MockerFixture, MockType

from signalbot import SignalAPI
from signalbot.api.outgoing import UpdateContact

HTTP_OK = 200


class TestContacts:
    signal_service = "127.0.0.1:8080"
    phone_number = "+49123456789"

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
    async def test_update_contact(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "put", {})

        update_contact = UpdateContact(recipient=self.phone_number, name="Bob")
        await self.signal_api.contacts.update(update_contact)

        assert mock.call_count == 1
