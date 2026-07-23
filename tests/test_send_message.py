from pathlib import Path as PathlibPath

import pytest
from anyio import Path as AnyIOPath

from signalbot.api.requests.send_message import (
    SendMessage,
    SendMessageMultiple,
    to_send_message_v2,
)


@pytest.mark.asyncio
async def test_send_message_serializes_as_sendv2_with_single_recipient(
    tmp_path: PathlibPath,
):
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("payload")

    message = SendMessage(
        attachments=[AnyIOPath(attachment)],
        number="+49123456789",
        recipient="group-1",
    )

    result = await to_send_message_v2(message)

    assert result.text == ""
    assert result.recipients == ["group-1"]
    assert result.base64_attachments == ["cGF5bG9hZA=="]


@pytest.mark.asyncio
async def test_send_message_multiple_serializes_as_sendv2_with_attachments(
    tmp_path: PathlibPath,
):
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("payload")

    message = SendMessageMultiple(
        attachments=[AnyIOPath(attachment)],
        number="+49123456789",
        recipients=["group-1", "group-2"],
        text="Hello World!",
    )

    result = await to_send_message_v2(message)

    assert result.text == "Hello World!"
    assert result.recipients == ["group-1", "group-2"]
    assert result.base64_attachments == ["cGF5bG9hZA=="]
