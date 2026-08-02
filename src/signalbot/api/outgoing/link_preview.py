from __future__ import annotations

from anyio import Path
from pydantic import BaseModel

from signalbot.api.generated.data.link_preview_type import LinkPreviewType
from signalbot.utils.attachment_base64 import attachment_to_base64
from signalbot.utils.pydantic_anyio_path import PydanticPath


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
