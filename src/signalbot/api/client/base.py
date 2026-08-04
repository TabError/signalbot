from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Generic, Literal, TypeVar

import aiohttp
import aiohttp.http_exceptions

if TYPE_CHECKING:
    from signalbot.auth import Authentication


class ConnectionMode(StrEnum):
    """Protocol strategy for connecting to `signal-cli-rest-api`.

    Attributes:
        HTTPS_ONLY: Always use HTTPS/WSS.
        HTTP_ONLY: Always use HTTP/WS.
        AUTO: Start with HTTPS/WSS and fallback to HTTP/WS if unavailable.
    """

    HTTPS_ONLY = "https_only"
    HTTP_ONLY = "http_only"
    AUTO = "auto"


HEALTH_CHECK_GOOD_STATUS = 204


class BaseURIs:
    def __init__(
        self, signal_service: str, phone_number: str, *, use_https: bool = True
    ) -> None:
        self.signal_service = signal_service
        self.phone_number = phone_number
        self.use_https = use_https

    @property
    def https_or_http(self) -> str:
        return "https" if self.use_https else "http"

    @property
    def wss_or_ws(self) -> str:
        return "wss" if self.use_https else "ws"

    def set_https(self, use_https: bool) -> None:  # noqa: FBT001
        self.use_https = use_https

    def http_uri(self, path: str) -> str:
        return f"{self.https_or_http}://{self.signal_service}{path}"

    def ws_uri(self, path: str) -> str:
        return f"{self.wss_or_ws}://{self.signal_service}{path}"


class SectionURIs:
    """Base for a section's `*URIs` class: holds the shared `BaseURIs`."""

    def __init__(self, base: BaseURIs) -> None:
        self._base = base


UrisT = TypeVar("UrisT", bound=SectionURIs)

_TRANSPORT_ERRORS: tuple[type[Exception], ...] = (
    aiohttp.ClientError,
    aiohttp.http_exceptions.HttpProcessingError,
)

HttpVerb = Literal["get", "post", "put", "delete"]


class BaseClient(Generic[UrisT]):
    """Shared HTTP helpers for a `signal-cli-rest-api` section client.

    Generic over its section's `*URIs` type (e.g. `ContactsClient` holds a
    `ContactsURIs`).
    """

    def __init__(self, uris: UrisT, auth: Authentication | None) -> None:
        self._uris = uris
        self._auth = auth

    def _add_auth(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        if headers is None:
            headers = {}
        if self._auth is not None:
            self._auth.write_header(headers)
        return headers

    async def _request(
        self,
        verb: HttpVerb,
        uri: str,
        *,
        error_cls: type[Exception],
        payload: str | None = None,
    ) -> aiohttp.ClientResponse:
        """Issue a request and raise `error_cls` on any transport failure."""
        headers = self._add_auth()
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                method = getattr(session, verb)
                resp = await (method(uri, data=payload) if payload else method(uri))
                resp.raise_for_status()
        except _TRANSPORT_ERRORS as exc:
            raise error_cls from exc
        else:
            return resp
