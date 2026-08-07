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
