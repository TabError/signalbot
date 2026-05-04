from __future__ import annotations

from signalbot.api.generated import Attachment as BaseAttachment


class Attachment(BaseAttachment):
    base64_content: str | None = None
