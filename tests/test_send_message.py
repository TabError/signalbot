import json
from pathlib import Path as PathlibPath

from anyio import Path as AnyIOPath

from signalbot.api.requests.send_message import SendMessage, SendMessageMultiple


def test_send_message_serializes_as_sendv2_with_single_recipient(tmp_path: PathlibPath):
    attachment = tmp_path / "attachment.txt"
    attachment.write_text("payload")

    message = SendMessage(
        attachments=[AnyIOPath(attachment)],
        number="+49123456789",
        recipient="group-1",
    )

    payload = json.loads(
        message.model_dump_json(
            exclude_none=True,
            by_alias=True,
            context={"mode": "sendv2"},
        )
    )

    assert payload["message"] == ""
    assert payload["recipients"] == ["group-1"]
    assert "recipient" not in payload
    assert payload["base64_attachments"] == ["cGF5bG9hZA=="]


def test_send_message_multiple_serializes_as_sendv2_with_attachments(
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

    payload = json.loads(
        message.model_dump_json(
            exclude_none=True,
            by_alias=True,
            context={"mode": "sendv2"},
        )
    )

    assert payload["message"] == "Hello World!"
    assert payload["recipients"] == ["group-1", "group-2"]
    assert payload["base64_attachments"] == ["cGF5bG9hZA=="]
