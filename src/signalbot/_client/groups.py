from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._client.base import BaseClient, SectionURIs
from signalbot.groups.errors import GetGroupsError, UpdateGroupError
from signalbot.groups.group_entry import GroupEntry

if TYPE_CHECKING:
    import aiohttp

    from signalbot._generated import UpdateGroupRequest


class GroupsURIs(SectionURIs):
    def groups_uri(self) -> str:
        return self._base.http_uri(f"/v1/groups/{self._base.phone_number}")

    def group_id_uri(self, group_id: str) -> str:
        return self.groups_uri() + "/" + group_id


class GroupsClient(BaseClient[GroupsURIs]):
    """Talks to the `signal-cli-rest-api` `/v1/groups` endpoints directly. Every
    call here hits the network.

    For a cached, already-parsed view of the bot's groups, use `GroupRegistry`
    (`bot.groups`) instead, which wraps this client and only refreshes on
    `refresh()`/`refresh_one()`.
    """

    async def get_all(self) -> list[GroupEntry]:
        """Fetch all groups the bot is a member of from the API."""
        uri = self._uris.groups_uri()
        resp = await self._request("get", uri, error_cls=GetGroupsError)
        return [GroupEntry.model_validate(group) for group in await resp.json()]

    async def get(self, group_id: str) -> GroupEntry:
        """Fetch a single group from the API by its public group id.

        Args:
            group_id: The group's public id (the `group.<...>=` form), not its
                internal id.
        """
        uri = self._uris.group_id_uri(group_id)
        resp = await self._request("get", uri, error_cls=GetGroupsError)
        return GroupEntry.model_validate(await resp.json())

    async def update(
        self, update_group_request: UpdateGroupRequest, group_id: str
    ) -> aiohttp.ClientResponse:
        """Update a group's metadata via the API.

        Args:
            update_group_request: The wire-format update payload.
            group_id: The group's public id (the `group.<...>=` form).
        """
        uri = self._uris.group_id_uri(group_id)
        payload = update_group_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "put", uri, error_cls=UpdateGroupError, payload=payload
        )
