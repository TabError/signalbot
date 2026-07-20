import base64
from pathlib import Path

from signalbot.utils.pydantic_anyio_path import PydanticPath


def attachment_to_base64(attachment: PydanticPath) -> str:
    # Add these extra metadata for better handling of the attachments.
    # This follows the RFC 2397.
    # data:<MIME-TYPE>;filename=<FILENAME>;base64,<BASE64 ENCODED DATA>
    return base64.b64encode(Path(str(attachment)).read_bytes()).decode("utf-8")
