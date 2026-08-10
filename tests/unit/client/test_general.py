from collections.abc import Callable

import aiohttp
from pytest_mock import MockerFixture, MockType

from signalbot import ConnectionMode
from signalbot._client import SignalAPI
from signalbot._client.base import HEALTH_CHECK_GOOD_STATUS
from signalbot._client.general import HealthCheckError
from signalbot.general import About
from tests.conftest import PHONE_NUMBER, SIGNAL_SERVICE


async def test_about(
    signal_api: SignalAPI, mock_json_response: Callable[[str, dict | list], MockType]
):
    about = About(
        build=1,
        capabilities={},
        mode="json-rpc",
        version="0.97",
        versions=["v1"],
    )
    mock_json_response("get", about.model_dump(by_alias=True))

    resp = await signal_api.general.about()

    assert resp == about


async def test_health_check(signal_api: SignalAPI, mocker: MockerFixture):
    mock = mocker.patch("aiohttp.ClientSession.get", new_callable=mocker.AsyncMock)
    mock.return_value = mocker.AsyncMock(
        spec=aiohttp.ClientResponse,
        status=HEALTH_CHECK_GOOD_STATUS,
    )

    resp = await signal_api.general.health_check()

    assert mock.call_count == 1
    assert resp is mock.return_value


async def test_check_signal_service_prefers_configured_protocol(mocker: MockerFixture):
    signal_api = SignalAPI(
        SIGNAL_SERVICE,
        PHONE_NUMBER,
        connection_mode=ConnectionMode.HTTP_ONLY,
    )

    health_check_mock = mocker.patch.object(
        signal_api.general, "health_check", new_callable=mocker.AsyncMock
    )
    health_check_mock.return_value = mocker.Mock(status=HEALTH_CHECK_GOOD_STATUS)

    is_healthy = await signal_api.check_signal_service()

    assert is_healthy is True
    assert signal_api._uris.use_https is False


async def test_check_signal_service_https_only_uses_secure_protocol(
    mocker: MockerFixture,
):
    signal_api = SignalAPI(
        SIGNAL_SERVICE,
        PHONE_NUMBER,
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


async def test_check_signal_service_does_not_fallback_if_protocol_configured(
    mocker: MockerFixture,
):
    signal_api = SignalAPI(
        SIGNAL_SERVICE,
        PHONE_NUMBER,
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


async def test_check_signal_service_falls_back_to_other_protocol_in_auto_mode(
    mocker: MockerFixture,
):
    signal_api = SignalAPI(SIGNAL_SERVICE, PHONE_NUMBER)

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


async def test_check_signal_service_auto_succeeds_without_fallback(
    mocker: MockerFixture,
):
    signal_api = SignalAPI(
        SIGNAL_SERVICE,
        PHONE_NUMBER,
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
