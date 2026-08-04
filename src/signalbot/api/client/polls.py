from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.base import BaseClient, SectionURIs
from signalbot.api.generated import CreatePollResponse

if TYPE_CHECKING:
    from signalbot.api.generated import CreatePollRequest


class PollsURIs(SectionURIs):
    def poll_uri(self) -> str:
        return self._base.http_uri(f"/v1/polls/{self._base.phone_number}")


class PollsClient(BaseClient[PollsURIs]):
    async def poll(
        self,
        create_poll_request: CreatePollRequest,
    ) -> CreatePollResponse:
        uri = self._uris.poll_uri()
        payload = create_poll_request.model_dump_json(exclude_none=True, by_alias=True)
        resp = await self._request("post", uri, error_cls=PollError, payload=payload)
        return CreatePollResponse.model_validate(await resp.json())


class PollError(Exception):
    pass
