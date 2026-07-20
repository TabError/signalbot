from __future__ import annotations

from typing import Any

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    model_serializer,
)

from signalbot.api.generated import MessageMention, SendMessageV2
from signalbot.api.generated.api import TextMode
from signalbot.api.requests import LinkPreview
from signalbot.utils.attachment_base64 import attachment_to_base64
from signalbot.utils.pydantic_anyio_path import PydanticPath


def _serialize_send_message_v2_payload(
    payload: dict[str, Any],
    *,
    attachments: list[PydanticPath] | None,
    recipient: str | None = None,
) -> dict[str, Any]:
    if payload.get("message") is None:
        payload["message"] = ""

    if attachments is not None:
        base64_attachments = list(payload.get("base64_attachments", []) or [])
        base64_attachments.extend(
            attachment_to_base64(attachment) for attachment in attachments
        )
        payload["base64_attachments"] = base64_attachments
        payload.pop("attachments", None)

    if recipient is not None:
        payload["recipients"] = [recipient]
        payload.pop("recipient", None)

    return payload


class SendMessage(BaseModel):
    base64_attachments: list[str] | None = None
    attachments: list[PydanticPath] | None = None
    edit_timestamp: int | None = None
    link_preview: LinkPreview | None = None
    mentions: list[MessageMention] | None = None
    text: str | None = Field(
        default=None,
        serialization_alias="message",
        validation_alias=AliasChoices("message", "text"),
    )
    notify_self: bool | None = None
    number: str | None = None
    quote_author: str | None = None
    quote_mentions: list[MessageMention] | None = None
    quote_message: str | None = None
    quote_timestamp: int | None = None
    recipient: str | None = None
    sticker: str | None = None
    text_mode: TextMode | None = None
    view_once: bool | None = None

    @model_serializer(mode="wrap")
    def serialize_model(
        self,
        handler: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = handler(self)
        if info.context and info.context.get("mode") == "sendv2":
            payload = _serialize_send_message_v2_payload(
                payload,
                attachments=self.attachments,
                recipient=self.recipient,
            )

            # Validate the payload using the original request type
            SendMessageV2.model_validate(payload)

        return payload


class SendMessageMultiple(SendMessageV2):
    attachments: list[PydanticPath] | None = None

    @model_serializer(mode="wrap")
    def serialize_model(
        self,
        handler: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = handler(self)
        if info.context and info.context.get("mode") == "sendv2":
            payload = _serialize_send_message_v2_payload(
                payload,
                attachments=self.attachments,
            )

            # Validate the payload using the original request type
            SendMessageV2.model_validate(payload)

        return payload


class SentMessage(SendMessage):
    timestamp: int

    @classmethod
    def from_send_message(
        cls, send_message: SendMessage, timestamp: int
    ) -> SentMessage:
        return cls.model_construct(**send_message.model_dump(), timestamp=timestamp)

    @classmethod
    def from_send_message_multiple(
        cls, send_message: SendMessageMultiple, timestamp: int
    ) -> list[SentMessage]:
        return [
            cls.model_construct(
                **send_message.model_dump(), recipient=recipient, timestamp=timestamp
            )
            for recipient in send_message.recipients
        ]
