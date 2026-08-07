from pathlib import Path as PathlibPath

import pytest
from anyio import Path as AnyIOPath

from signalbot.api.outgoing import SendMessage, SendMessageMultiple


@pytest.mark.asyncio
async def test_send_message_serializes_as_sendv2_with_single_recipient(
    tmp_path: PathlibPath,
):
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("payload")

    message = SendMessage(
        attachments=[AnyIOPath(attachment)],
        recipient="group-1",
    )

    result = await message.to_generated("+49123456789")

    assert result.number == "+49123456789"
    assert result.message == ""
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
        recipients=["group-1", "group-2"],
        text="Hello World!",
    )

    result = await message.to_generated("+49123456789")

    assert result.number == "+49123456789"
    assert result.message == "Hello World!"
    assert result.recipients == ["group-1", "group-2"]
    assert result.base64_attachments == ["cGF5bG9hZA=="]
