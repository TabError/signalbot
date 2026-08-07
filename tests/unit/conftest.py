from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
import pytest

from signalbot.api.generated import (
    AddMembers,
    EditGroup,
    GroupPermissions,
    SendMessages,
)
from tests.conftest import GROUP_ID, GROUP_INTERNAL_ID

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_mock import MockerFixture

    from signalbot import SignalBot

HTTP_OK = 200

FULL_GROUP_PERMISSIONS = GroupPermissions(
    add_members=AddMembers.EVERY_MEMBER,
    edit_group=EditGroup.EVERY_MEMBER,
    send_messages=SendMessages.EVERY_MEMBER,
)


class TestCommon:
    @pytest.fixture(autouse=True)
    def _use_signal_bot(self, signal_bot: SignalBot) -> None:
        self.signal_bot = signal_bot


@pytest.fixture
def fake_group() -> dict:
    return {
        "admins": [],
        "blocked": False,
        "description": "",
        "name": "mocked group",
        "id": GROUP_ID,
        "internal_id": GROUP_INTERNAL_ID,
        "invite_link": "",
        "members": [],
        "pending_invites": [],
        "pending_requests": [],
        "permissions": FULL_GROUP_PERMISSIONS.model_dump(),
    }


@pytest.fixture
def mock_receive(mocker: MockerFixture) -> Callable[[list[str]], None]:
    def _mock(raw_messages: list[str]) -> None:
        mock_iterator = mocker.AsyncMock()
        mock_iterator.__aiter__.return_value = raw_messages
        mock = mocker.patch("websockets.connect")
        mock.return_value.__aenter__.return_value = mock_iterator

    return _mock


@pytest.fixture
def mock_get_all_groups(mocker: MockerFixture) -> Callable[[list[dict]], None]:
    def _mock(groups: list[dict]) -> None:
        json_mock = mocker.AsyncMock(return_value=groups)
        get_groups_mock = mocker.patch(
            "aiohttp.ClientSession.get", new_callable=mocker.AsyncMock
        )
        get_groups_mock.return_value = mocker.AsyncMock(
            spec=aiohttp.ClientResponse,
            status=HTTP_OK,
            json=json_mock,
        )

    return _mock
