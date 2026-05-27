from __future__ import annotations

from anyio import Path

from signalbot.api.generated import Attachment as BaseAttachment


class Attachment(BaseAttachment):
    base64_content: str | None = None

    async def local_path(self) -> Path | None:
        if self.local_filename is None:
            return None

        return (
            await Path.home()
            / ".local/share/signal-api/attachments"
            / self.local_filename
        )
