from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from signalbot._client.base import BaseClient, SectionURIs
from signalbot.errors import SignalAPIError

if TYPE_CHECKING:
    import aiohttp

    from signalbot._generated import Attachment


class AttachmentsURIs(SectionURIs):
    def attachment_uri(self) -> str:
        return self._base.http_uri("/v1/attachments")


class AttachmentsClient(BaseClient[AttachmentsURIs]):
    async def download(self, attachment: Attachment) -> str:
        uri = f"{self._uris.attachment_uri()}/{attachment.local_filename}"
        resp = await self._request("get", uri, error_cls=DownloadAttachmentError)
        content = await resp.content.read()
        return str(base64.b64encode(content), encoding="utf-8")

    async def delete(self, attachment: Attachment) -> aiohttp.ClientResponse:
        attachment_id = attachment.local_filename
        if attachment_id is None:
            error_msg = "Attachment has no local filename"
            raise ValueError(error_msg)

        uri = f"{self._uris.attachment_uri()}/{attachment_id}"
        return await self._request("delete", uri, error_cls=DeleteAttachmentError)


class DownloadAttachmentError(SignalAPIError):
    pass


class DeleteAttachmentError(SignalAPIError):
    pass
