from __future__ import annotations

from signalbot.api import generated


class LinkPreview(generated.Preview):
    base64_thumbnail: str | None = None
