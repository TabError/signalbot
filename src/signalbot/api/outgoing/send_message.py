from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Self

from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    model_validator,
)

from signalbot.api.generated import MessageMention, SendMessageV2
from signalbot.api.generated.api import TextMode
from signalbot.api.outgoing.link_preview import LinkPreview
from signalbot.utils.attachment_base64 import attachment_to_base64
from signalbot.utils.pydantic_anyio_path import PydanticPath

if TYPE_CHECKING:
    from signalbot.api.generated.data.link_preview_type import LinkPreviewType


async def _resolve_base64_attachments(
    send_message: BaseSendMessage,
) -> list[str] | None:
    base64_attachments = list(send_message.base64_attachments or [])
    if send_message.attachments:
        base64_attachments += await asyncio.gather(
            *(attachment_to_base64(path) for path in send_message.attachments)
        )
    return base64_attachments or None


async def _resolve_link_preview(
    link_preview: LinkPreview | None,
) -> LinkPreviewType | None:
    if link_preview is None:
        return None
    return await link_preview.to_generated()


def _check_link_preview_url_in_text(send_message: BaseSendMessage) -> None:
    if send_message.link_preview is not None and (
        send_message.text is None
        or send_message.link_preview.url not in send_message.text
    ):
        error_msg = (
            "If the link_preview is included, the URL must be present in the text."
        )
        raise ValueError(error_msg)


class BaseSendMessage(BaseModel):
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
    quote_author: str | None = None
    quote_mentions: list[MessageMention] | None = None
    quote_message: str | None = None
    quote_timestamp: int | None = None
    sticker: str | None = None
    text_mode: TextMode | None = None
    view_once: bool | None = None

    @model_validator(mode="after")
    def check_link_preview_url_in_text(self) -> Self:
        _check_link_preview_url_in_text(self)
        return self


class SendMessage(BaseSendMessage):
    recipient: str | None = None

    async def to_generated(self, number: str) -> SendMessageV2:
        base64_attachments = await _resolve_base64_attachments(self)
        link_preview = await _resolve_link_preview(self.link_preview)

        if self.recipient is None:
            error_msg = "Recipient must be set in SendMessage"
            raise ValueError(error_msg)

        return SendMessageV2(
            base64_attachments=base64_attachments,
            edit_timestamp=self.edit_timestamp,
            link_preview=link_preview,
            mentions=self.mentions,
            message=self.text or "",
            notify_self=self.notify_self,
            number=number,
            quote_author=self.quote_author,
            quote_mentions=self.quote_mentions,
            quote_message=self.quote_message,
            quote_timestamp=self.quote_timestamp,
            recipients=[self.recipient],
            sticker=self.sticker,
            text_mode=self.text_mode,
            view_once=self.view_once,
        )


class SendMessageMultiple(BaseSendMessage):
    recipients: list[str]

    async def to_generated(self, number: str) -> SendMessageV2:
        base64_attachments = await _resolve_base64_attachments(self)
        link_preview = await _resolve_link_preview(self.link_preview)

        return SendMessageV2(
            base64_attachments=base64_attachments,
            edit_timestamp=self.edit_timestamp,
            link_preview=link_preview,
            mentions=self.mentions,
            message=self.text or "",
            notify_self=self.notify_self,
            number=number,
            quote_author=self.quote_author,
            quote_mentions=self.quote_mentions,
            quote_message=self.quote_message,
            quote_timestamp=self.quote_timestamp,
            recipients=self.recipients,
            sticker=self.sticker,
            text_mode=self.text_mode,
            view_once=self.view_once,
        )


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
