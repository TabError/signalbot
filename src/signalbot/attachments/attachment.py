from __future__ import annotations

from anyio import Path

from signalbot import _generated as generated


class Attachment(generated.Attachment):
    base64_content: str | None = None

    async def local_path(self) -> Path | None:
        if self.local_filename is None:
            return None

        return (
            await Path.home()
            / ".local/share/signal-api/attachments"
            / self.local_filename
        )
