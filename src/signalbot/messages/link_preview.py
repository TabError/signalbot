from __future__ import annotations

from anyio import Path
from pydantic import BaseModel

from signalbot._generated import LinkPreviewType
from signalbot._generated import Preview as GeneratedPreview
from signalbot._utils.attachment_base64 import attachment_to_base64
from signalbot._utils.pydantic_anyio_path import PydanticPath


class Preview(GeneratedPreview):
    """The preview metadata Signal already generated for a link in a received
    message.
    """

    base64_thumbnail: str | None = None


class LinkPreview(BaseModel):
    """
    LinkPreview

    Attributes:
        description: The description of the link preview.
        title: The title of the link preview.
        url: The URL of the link preview.
        thumbnail : The thumbnail of the link preview. This can be a Path or a base64
            encoded string of the image content.
    """

    description: str
    title: str
    url: str
    thumbnail: PydanticPath | str

    async def to_generated(self) -> LinkPreviewType:
        base64_thumbnail = (
            await attachment_to_base64(self.thumbnail)
            if isinstance(self.thumbnail, Path)
            else self.thumbnail
        )
        return LinkPreviewType(
            base64_thumbnail=base64_thumbnail,
            description=self.description,
            title=self.title,
            url=self.url,
        )
