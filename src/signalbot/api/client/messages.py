from __future__ import annotations

from typing import TYPE_CHECKING

import websockets

from signalbot.api.client.base import BaseClient, SectionURIs
from signalbot.api.generated import RemoteDeleteResponse, SendMessageResponse
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import aiohttp

    from signalbot.api.generated import (
        RemoteDeleteRequest,
        SendMessageV2,
        TypingIndicatorRequest,
    )


class MessagesURIs(SectionURIs):
    def receive_ws_uri(self) -> str:
        return self._base.ws_uri(f"/v1/receive/{self._base.phone_number}")

    def send_uri(self) -> str:
        return self._base.http_uri("/v2/send")

    def typing_indicator_uri(self) -> str:
        return self._base.http_uri(f"/v1/typing-indicator/{self._base.phone_number}")

    def remote_delete_uri(self) -> str:
        return self._base.http_uri(f"/v1/remote-delete/{self._base.phone_number}")


class MessagesClient(BaseClient[MessagesURIs]):
    async def receive(self) -> AsyncIterator[str]:
        headers = self._add_auth()

        try:
            uri = self._uris.receive_ws_uri()
            self.connection = websockets.connect(uri, additional_headers=headers)
            async with self.connection as websocket:
                async for raw_message in websocket:
                    yield str(raw_message)

        except Exception as e:
            raise ReceiveError from e

    async def send(
        self,
        data_message: SendMessageV2,
    ) -> SendMessageResponse:
        uri = self._uris.send_uri()
        payload = data_message.model_dump_json(exclude_none=True, by_alias=True)
        resp = await self._request("post", uri, error_cls=SendError, payload=payload)
        return SendMessageResponse.model_validate(await resp.json())

    async def start_typing(
        self, typing_request: TypingIndicatorRequest
    ) -> aiohttp.ClientResponse:
        uri = self._uris.typing_indicator_uri()
        payload = typing_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "put", uri, error_cls=StartTypingError, payload=payload
        )

    async def stop_typing(
        self, typing_request: TypingIndicatorRequest
    ) -> aiohttp.ClientResponse:
        uri = self._uris.typing_indicator_uri()
        payload = typing_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "delete", uri, error_cls=StopTypingError, payload=payload
        )

    async def remote_delete(
        self, remote_delete_request: RemoteDeleteRequest
    ) -> RemoteDeleteResponse:
        uri = self._uris.remote_delete_uri()
        payload = remote_delete_request.model_dump_json(
            exclude_none=True, by_alias=True
        )
        resp = await self._request(
            "delete", uri, error_cls=RemoteDeleteError, payload=payload
        )
        return RemoteDeleteResponse.model_validate(await resp.json())


class ReceiveError(SignalAPIError):
    pass


class SendError(SignalAPIError):
    pass


class TypingError(SignalAPIError):
    pass


class StartTypingError(TypingError):
    pass


class StopTypingError(TypingError):
    pass


class RemoteDeleteError(SignalAPIError):
    pass
