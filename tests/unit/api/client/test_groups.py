import aiohttp
import pytest
from pytest_mock import MockerFixture, MockType

from signalbot import SignalAPI
from signalbot.api.generated import (
    AddMembers,
    EditGroup,
    GroupEntry,
    GroupPermissions,
    SendMessages,
    UpdateGroupRequest,
)

HTTP_OK = 200


class TestGroups:
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
    async def test_get_groups(self, mocker: MockerFixture):
        group_entry = GroupEntry(
            admins=[],
            blocked=False,
            description="",
            id=self.group_id,
            internal_id="internal-id",
            invite_link="",
            members=[],
            name="Test",
            pending_invites=[],
            pending_requests=[],
            permissions=GroupPermissions(
                add_members=AddMembers.EVERY_MEMBER,
                edit_group=EditGroup.EVERY_MEMBER,
                send_messages=SendMessages.EVERY_MEMBER,
            ),
        )
        self._mock_json_response(mocker, "get", [group_entry.model_dump(by_alias=True)])

        groups = await self.signal_api.groups.get_all()

        assert groups == [group_entry]

    @pytest.mark.asyncio
    async def test_get_group(self, mocker: MockerFixture):
        group_entry = GroupEntry(
            admins=[],
            blocked=False,
            description="",
            id=self.group_id,
            internal_id="internal-id",
            invite_link="",
            members=[],
            name="Test",
            pending_invites=[],
            pending_requests=[],
            permissions=GroupPermissions(
                add_members=AddMembers.EVERY_MEMBER,
                edit_group=EditGroup.EVERY_MEMBER,
                send_messages=SendMessages.EVERY_MEMBER,
            ),
        )
        self._mock_json_response(mocker, "get", group_entry.model_dump(by_alias=True))

        group = await self.signal_api.groups.get(self.group_id)

        assert group == group_entry

    @pytest.mark.asyncio
    async def test_update_group(self, mocker: MockerFixture):
        mock = self._mock_json_response(mocker, "put", {})

        update_group_request = UpdateGroupRequest(name="New Name")
        await self.signal_api.groups.update(self.group_id, update_group_request)

        assert mock.call_count == 1
