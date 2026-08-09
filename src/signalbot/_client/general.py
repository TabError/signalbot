from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot._client.base import BaseClient, SectionURIs
from signalbot._generated import About
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    import aiohttp


class GeneralURIs(SectionURIs):
    def health_check_uri(self) -> str:
        return self._base.http_uri("/v1/health")

    def about_uri(self) -> str:
        return self._base.http_uri("/v1/about")


class GeneralClient(BaseClient[GeneralURIs]):
    async def health_check(self) -> aiohttp.ClientResponse:
        uri = self._uris.health_check_uri()
        return await self._request("get", uri, error_cls=HealthCheckError)

    async def about(self) -> About:
        uri = self._uris.about_uri()
        resp = await self._request("get", uri, error_cls=AboutError)
        return About.model_validate(await resp.json())


class HealthCheckError(SignalAPIError):
    pass


class AboutError(SignalAPIError):
    pass
