from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING, Annotated, Any

from anyio import Path
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic_core import core_schema

from signalbot.api.generated import LinkPreviewType, MessageMention, SendMessageV2
from signalbot.api.generated.api import TextMode

if TYPE_CHECKING:
    from pydantic.json_schema import JsonSchemaValue


class _PathPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # noqa: ANN401
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(Path),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(Path),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        return handler(core_schema.str_schema())


PydanticPath = Annotated[Path, _PathPydanticAnnotation]


async def _attachments_to_base64(attachments: list[PydanticPath]) -> list[str]:
    base64_attachments: list[str] = []
    for attachment in attachments:
        async with await attachment.open("rb") as f:
            # data:<MIME-TYPE>;filename=<FILENAME>;base64,<BASE64 ENCODED DATA>
            base64_attachments.append(
                str(base64.b64encode(await f.read()), encoding="utf-8")
            )
    return base64_attachments


async def _model_dump_as_send_message_v2(
    data_message: SendMessage | SendMessageMultiple,
) -> dict[str, Any]:
    payload = data_message.model_dump(exclude_none=True, by_alias=True)

    if data_message.attachments is not None:
        base64_attachments: list = payload.get("base64_attachments", [])
        processed_attachments = await _attachments_to_base64(data_message.attachments)
        base64_attachments.extend(processed_attachments)
        payload["base64_attachments"] = base64_attachments
        del payload["attachments"]

    return payload


class SendMessage(BaseModel):
    base64_attachments: list[str] | None = None
    attachments: list[PydanticPath] | None = None
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
    recipient: str | None = None
    sticker: str | None = None
    text_mode: TextMode | None = None
    view_once: bool | None = None

    async def model_dump_json_as_send_message_v2(self) -> str:
        payload = await _model_dump_as_send_message_v2(self)

        payload["recipients"] = [self.recipient]
        del payload["recipient"]

        return json.dumps(payload)


class SendMessageMultiple(SendMessageV2):
    attachments: list[PydanticPath] | None = None

    async def model_dump_json_as_send_message_v2(self) -> str:
        return json.dumps(await _model_dump_as_send_message_v2(self))


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
