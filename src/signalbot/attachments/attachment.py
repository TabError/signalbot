from __future__ import annotations

from anyio import Path

from signalbot import _generated as generated


class Attachment(generated.Attachment):
    """A file attached to a received or sent message."""

    base64_content: str | None = None

    async def local_path(self) -> Path | None:
        """Resolve where this attachment is cached on disk, if it was downloaded.

        Returns:
            The local path, or `None` if the attachment has no local filename.
        """
        if self.local_filename is None:
            return None

        return (
            await Path.home()
            / ".local/share/signal-api/attachments"
            / self.local_filename
        )
