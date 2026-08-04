from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.base import BaseClient, SectionURIs
from signalbot.api.generated import GroupEntry
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    import aiohttp

    from signalbot.api import generated


class GroupsURIs(SectionURIs):
    def groups_uri(self) -> str:
        return self._base.http_uri(f"/v1/groups/{self._base.phone_number}")

    def group_id_uri(self, group_id: str) -> str:
        return self.groups_uri() + "/" + group_id


class GroupsClient(BaseClient[GroupsURIs]):
    async def get_groups(self) -> list[GroupEntry]:
        uri = self._uris.groups_uri()
        resp = await self._request("get", uri, error_cls=GetGroupsError)
        return [GroupEntry.model_validate(group) for group in await resp.json()]

    async def get_group(self, group_id: str) -> GroupEntry:
        uri = self._uris.group_id_uri(group_id)
        resp = await self._request("get", uri, error_cls=GetGroupsError)
        return GroupEntry.model_validate(await resp.json())

    async def update_group(
        self, group_id: str, update_group_request: generated.UpdateGroupRequest
    ) -> aiohttp.ClientResponse:
        uri = self._uris.group_id_uri(group_id)
        payload = update_group_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "put", uri, error_cls=UpdateGroupError, payload=payload
        )


class GetGroupsError(SignalAPIError):
    pass


class UpdateGroupError(SignalAPIError):
    pass
