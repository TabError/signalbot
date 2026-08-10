from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture, MockType

HTTP_OK = 200


@pytest.fixture
def mock_json_response(mocker: MockerFixture) -> Callable[[str, dict | list], MockType]:
    """Patch `aiohttp.ClientSession.<verb>` to return an OK response with `payload` as JSON."""

    def _mock(verb: str, payload: dict | list) -> MockType:
        json_mock = mocker.AsyncMock(return_value=payload)
        mock = mocker.patch(
            f"aiohttp.ClientSession.{verb}", new_callable=mocker.AsyncMock
        )
        mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            json=json_mock,
        )
        return mock

    return _mock


@pytest.fixture
def mock_error_response(mocker: MockerFixture) -> Callable[[str, int, str], MockType]:
    """Patch `aiohttp.ClientSession.<verb>` so `raise_for_status()` raises,
    simulating `signal-cli-rest-api` rejecting the request."""

    def _mock(verb: str, status: int, message: str) -> MockType:
        response = mocker.AsyncMock(spec=aiohttp.ClientResponse)
        response.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=mocker.Mock(),
            history=(),
            status=status,
            message=message,
        )
        mock = mocker.patch(
            f"aiohttp.ClientSession.{verb}", new_callable=mocker.AsyncMock
        )
        mock.return_value = response
        return mock

    return _mock
