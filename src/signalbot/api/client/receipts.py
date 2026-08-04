from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.client.base import BaseClient, SectionURIs
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    import aiohttp

    from signalbot.api.generated.api import Receipt


class ReceiptsURIs(SectionURIs):
    def receipts_uri(self) -> str:
        return self._base.http_uri(f"/v1/receipts/{self._base.phone_number}")


class ReceiptsClient(BaseClient[ReceiptsURIs]):
    async def send_receipt(self, receipt_request: Receipt) -> aiohttp.ClientResponse:
        uri = self._uris.receipts_uri()
        payload = receipt_request.model_dump_json(exclude_none=True, by_alias=True)
        return await self._request(
            "post", uri, error_cls=SendReceiptError, payload=payload
        )


class SendReceiptError(SignalAPIError):
    pass
