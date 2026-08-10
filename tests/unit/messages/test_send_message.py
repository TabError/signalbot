from pathlib import Path as PathlibPath

from anyio import Path as AnyIOPath

from signalbot.messages import SendMessage, SendMessageMultiple


async def test_send_message_serializes_as_sendv2_with_single_recipient(
    tmp_path: PathlibPath,
):
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("payload")

    message = SendMessage(
        attachments=[AnyIOPath(attachment)],
    )

    result = await message.to_generated("+49123456789", "group-1")

    assert result.number == "+49123456789"
    assert result.message == ""
    assert result.recipients == ["group-1"]
    assert result.base64_attachments == ["cGF5bG9hZA=="]


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
