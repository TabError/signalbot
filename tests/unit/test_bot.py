import pytest
from packaging.version import InvalidVersion
from pytest_mock import MockerFixture

from signalbot import MIN_SIGNAL_CLI_REST_API_VERSION, ConnectionMode, SignalBot
from tests.conftest import PHONE_NUMBER, SIGNAL_SERVICE
from tests.unit.conftest import TestCommon


class TestSignalApiProtocolConfig:
    def test_connection_mode_defaults_to_auto(self):
        signal_bot = SignalBot(
            {
                "signal_service": SIGNAL_SERVICE,
                "phone_number": PHONE_NUMBER,
                "storage": {"type": "in-memory"},
            }
        )

        assert signal_bot._signal.connection_mode == ConnectionMode.AUTO
        assert signal_bot._signal._uris.use_https is True

    def test_connection_mode_can_be_set_to_http_only(self):
        signal_bot = SignalBot(
            {
                "signal_service": SIGNAL_SERVICE,
                "phone_number": PHONE_NUMBER,
                "storage": {"type": "in-memory"},
                "connection_mode": ConnectionMode.HTTP_ONLY,
            }
        )

        assert signal_bot._signal.connection_mode == ConnectionMode.HTTP_ONLY
        assert signal_bot._signal._uris.use_https is False

    def test_connection_mode_can_be_set_to_https_only(self):
        signal_bot = SignalBot(
            {
                "signal_service": SIGNAL_SERVICE,
                "phone_number": PHONE_NUMBER,
                "storage": {"type": "in-memory"},
                "connection_mode": ConnectionMode.HTTPS_ONLY,
            }
        )

        assert signal_bot._signal.connection_mode == ConnectionMode.HTTPS_ONLY
        assert signal_bot._signal._uris.use_https is True


class TestSignalApiVersionCheck(TestCommon):
    async def test_new_version_is_okay(self, mocker: MockerFixture):
        about_mock = mocker.patch.object(
            self.signal_bot.general,
            "about",
            new_callable=mocker.AsyncMock,
        )
        about_mock.return_value = mocker.Mock(
            version=str(MIN_SIGNAL_CLI_REST_API_VERSION)
        )

        await self.signal_bot._check_signal_cli_rest_api_version()

        about_mock.return_value = mocker.Mock(
            version=f"{MIN_SIGNAL_CLI_REST_API_VERSION.major + 1}.0.0"
        )
        await self.signal_bot._check_signal_cli_rest_api_version()

    async def test_unset_version(self, mocker: MockerFixture):
        about_mock = mocker.patch.object(
            self.signal_bot.general,
            "about",
            new_callable=mocker.AsyncMock,
        )
        about_mock.return_value = mocker.Mock(version="unset")

        await self.signal_bot._check_signal_cli_rest_api_version()

    async def test_old_version_raises_runtime_error(self, mocker: MockerFixture):
        about_mock = mocker.patch.object(
            self.signal_bot.general,
            "about",
            new_callable=mocker.AsyncMock,
        )
        prev_version = f"{MIN_SIGNAL_CLI_REST_API_VERSION.major}."
        prev_version += f"{MIN_SIGNAL_CLI_REST_API_VERSION.minor - 1}.0"
        about_mock.return_value = mocker.Mock(version=prev_version)

        with pytest.raises(
            RuntimeError, match="Incompatible signal-cli-rest-api version"
        ):
            await self.signal_bot._check_signal_cli_rest_api_version()

    async def test_invalid_version(self, mocker: MockerFixture):
        about_mock = mocker.patch.object(
            self.signal_bot.general,
            "about",
            new_callable=mocker.AsyncMock,
        )
        about_mock.return_value = mocker.Mock(version="abc")

        with pytest.raises(InvalidVersion, match="Invalid version: 'abc'"):
            await self.signal_bot._check_signal_cli_rest_api_version()
