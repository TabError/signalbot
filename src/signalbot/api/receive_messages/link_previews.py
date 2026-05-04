from __future__ import annotations

from signalbot.api.generated import Preview as BasePreview


class Preview(BasePreview):
    base64_thumbnail: str | None = None
