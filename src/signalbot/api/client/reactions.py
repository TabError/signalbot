from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.base import BaseClient, SectionURIs
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    import aiohttp

    from signalbot.api.generated.api import SendReactionRequest


class ReactionsURIs(SectionURIs):
    def react_uri(self) -> str:
        return self._base.http_uri(f"/v1/reactions/{self._base.phone_number}")


class ReactionsClient(BaseClient[ReactionsURIs]):
    async def react(
        self,
        reaction_request: SendReactionRequest,
    ) -> aiohttp.ClientResponse:
        uri = self._uris.react_uri()
        payload = reaction_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "post", uri, error_cls=SendReactionError, payload=payload
        )


class SendReactionError(SignalAPIError):
    pass
