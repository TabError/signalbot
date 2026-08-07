import aiohttp
import pytest
from pytest_mock import MockerFixture, MockType

from signalbot import ConnectionMode, SignalAPI
from signalbot.api.client.base import HEALTH_CHECK_GOOD_STATUS
from signalbot.api.client.general import HealthCheckError
from signalbot.api.generated import About

HTTP_OK = 200


class TestGeneral:
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
    async def test_about(self, mocker: MockerFixture):
        about = About(
            build=1,
            capabilities={},
            mode="json-rpc",
            version="0.97",
            versions=["v1"],
        )
        self._mock_json_response(mocker, "get", about.model_dump(by_alias=True))

        resp = await self.signal_api.general.about()

        assert resp == about

    @pytest.mark.asyncio
    async def test_health_check(self, mocker: MockerFixture):
        mock = mocker.patch("aiohttp.ClientSession.get", new_callable=mocker.AsyncMock)
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HEALTH_CHECK_GOOD_STATUS,
        )

        resp = await self.signal_api.general.health_check()

        assert mock.call_count == 1
        assert resp is mock.return_value

    @pytest.mark.asyncio
    async def test_check_signal_service_prefers_configured_protocol(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTP_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_https_only_uses_secure_protocol(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTPS_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is True

    @pytest.mark.asyncio
    async def test_check_signal_service_does_not_fallback_if_protocol_configured(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.HTTP_ONLY,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.side_effect = HealthCheckError()

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is False
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_falls_back_to_other_protocol_in_auto_mode(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(self.signal_service, self.phone_number)

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.side_effect = [
            HealthCheckError(),
            mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS),
        ]

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert signal_api._uris.use_https is False

    @pytest.mark.asyncio
    async def test_check_signal_service_auto_succeeds_without_fallback(
        self, mocker: MockerFixture
    ):
        signal_api = SignalAPI(
            self.signal_service,
            self.phone_number,
            connection_mode=ConnectionMode.AUTO,
        )

        health_check_mock = mocker.patch.object(
            signal_api.general, "health_check", new_callable=mocker.AsyncMock
        )
        health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

        is_healthy = await signal_api.check_signal_service()

        assert is_healthy is True
        assert health_check_mock.call_count == 1
        assert signal_api._uris.use_https is True
