from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot.api.incoming.base_message import BaseMessageWithGroup

if TYPE_CHECKING:
    from signalbot.api import generated
    from signalbot.api.generated import (
        DataMessage,
        MessageEnvelope,
        SyncDataMessage,
    )


class Reaction(BaseMessageWithGroup):
    emoji: str | None = None
    is_remove: bool
    target_author: str | None = None
    target_author_number: str | None = None
    target_author_uuid: str | None = None

    @classmethod
    async def _internal_parse(
        cls,
        message_envelope: MessageEnvelope,
        data_message: DataMessage | SyncDataMessage,
        reaction_message: generated.Reaction,
    ) -> Reaction:
        return cls(
            server_delivered_timestamp=message_envelope.server_delivered_timestamp,
            server_received_timestamp=message_envelope.server_received_timestamp,
            source=message_envelope.source,
            source_device=message_envelope.source_device,
            source_name=message_envelope.source_name,
            source_number=message_envelope.source_number,
            source_uuid=message_envelope.source_uuid,
            timestamp=reaction_message.target_sent_timestamp,
            group_info=data_message.group_info,
            emoji=reaction_message.emoji,
            is_remove=reaction_message.is_remove,
            target_author=reaction_message.target_author,
            target_author_number=reaction_message.target_author_number,
            target_author_uuid=reaction_message.target_author_uuid,
        )

    @classmethod
    async def from_message_envelope(cls, message_envelope: MessageEnvelope) -> Reaction:
        if (
            message_envelope.data_message is not None
            and message_envelope.data_message.reaction is not None
        ):
            return await cls._internal_parse(
                message_envelope,
                message_envelope.data_message,
                message_envelope.data_message.reaction,
            )

        if (
            message_envelope.sync_message is not None
            and message_envelope.sync_message.sent_message is not None
            and message_envelope.sync_message.sent_message.reaction is not None
        ):
            return await cls._internal_parse(
                message_envelope,
                message_envelope.sync_message.sent_message,
                message_envelope.sync_message.sent_message.reaction,
            )

        error_msg = "MessageEnvelope does not contain a Reaction"
        raise ValueError(error_msg)
