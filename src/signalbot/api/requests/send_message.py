from __future__ import annotations

from pydantic import AliasChoices, BaseModel, Field

from signalbot.api.generated import LinkPreviewType, MessageMention, SendMessageV2
from signalbot.api.generated.api import TextMode


class SendMessage(BaseModel):
    base64_attachments: list[str] | None = None
    edit_timestamp: int | None = None
    link_preview: LinkPreviewType | None = None
    mentions: list[MessageMention] | None = None
    text: str = Field(
        ...,
        serialization_alias="message",
        validation_alias=AliasChoices("message", "text"),
    )
    notify_self: bool | None = None
    number: str | None = None
    quote_author: str | None = None
    quote_mentions: list[MessageMention] | None = None
    quote_message: str | None = None
    quote_timestamp: int | None = None
    recipient: str
    sticker: str | None = None
    text_mode: TextMode | None = None
    view_once: bool | None = None

    def to_send_message_v2(self) -> SendMessageV2:
        payload = self.model_dump(exclude_none=True, by_alias=True)
        return SendMessageV2.model_construct(**payload, recipients=[self.recipient])


class SendMessageMultiple(SendMessageV2): ...


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
