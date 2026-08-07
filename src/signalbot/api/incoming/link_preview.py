from __future__ import annotations

from signalbot.api.generated import Preview


class LinkPreview(Preview):
    base64_thumbnail: str | None = None
