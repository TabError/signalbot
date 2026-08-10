from __future__ import annotations

import json
from typing import TYPE_CHECKING, TypeAlias

from signalbot._generated import Message
from signalbot.errors import SignalAPIError
from signalbot.groups import GroupUpdate
from signalbot.messages.data_message import DataMessage
from signalbot.messages.edit_message import EditMessage
from signalbot.messages.remote_delete import RemoteDelete
from signalbot.messages.typing_message import TypingMessage
from signalbot.reactions import Reaction

if TYPE_CHECKING:
    from signalbot import _generated as generated
    from signalbot._client import SignalAPI
    from signalbot._generated import MessageEnvelope, SyncDataMessage

ReceivedMessage: TypeAlias = (
    "DataMessage | GroupUpdate | RemoteDelete | TypingMessage | EditMessage | Reaction"
)
"""Union of all message types `parse` can return."""


async def _parse_data_message_variant(
    signal: SignalAPI,
    message_envelope: MessageEnvelope,
    data_message: generated.DataMessage | SyncDataMessage,
) -> ReceivedMessage:
    if GroupUpdate.message_envelope_is_group_update(message_envelope):
        return GroupUpdate.from_message_envelope(message_envelope)
    if data_message.reaction is not None:
        return await Reaction.from_message_envelope(message_envelope)
    if data_message.remote_delete is not None:
        return await RemoteDelete.from_message_envelope(message_envelope)
    return await DataMessage.from_message_envelope(message_envelope, signal)


async def _parse_sync_messages(
    signal: SignalAPI, message_envelope: MessageEnvelope
) -> ReceivedMessage | None:
    if message_envelope.sync_message is not None:
        sync_message = message_envelope.sync_message
        if sync_message.sent_message is not None:
            if sync_message.sent_message.edit_message is not None:
                return await EditMessage.from_message_envelope(message_envelope, signal)

            return await _parse_data_message_variant(
                signal, message_envelope, sync_message.sent_message
            )

    return None


async def _parse_main_messages(
    signal: SignalAPI, message_envelope: MessageEnvelope
) -> ReceivedMessage | None:
    if message_envelope.data_message is not None:
        return await _parse_data_message_variant(
            signal, message_envelope, message_envelope.data_message
        )

    if message_envelope.edit_message is not None:
        return await EditMessage.from_message_envelope(message_envelope, signal)

    if message_envelope.typing_message is not None:
        return await TypingMessage.from_message_envelope(message_envelope)

    return None


async def parse(signal: SignalAPI, raw_message_str: str) -> ReceivedMessage:
    """Parse a raw JSON message string from the Signal API into a Message object.

    Args:
        signal: An instance of the `SignalAPI` class, used to fetch attachments and
            link previews if necessary.
        raw_message_str: The raw JSON string of the message as received from the
            Signal API.

    Returns:
        A `Message` object representing the parsed message.

    Raises:
        UnknownMessageFormatError: If the message format is unrecognized or if
            required fields are missing.
    """
    try:
        raw_message = json.loads(raw_message_str)
    except Exception as exc:
        raise UnknownMessageFormatError from exc

    envelope = Message.model_validate(raw_message)

    parsed_message = await _parse_main_messages(signal, envelope.envelope)
    if parsed_message is not None:
        return parsed_message

    parsed_message = await _parse_sync_messages(signal, envelope.envelope)
    if parsed_message is not None:
        return parsed_message

    error_msg = "MessageEnvelope does not contain a recognizable message type"
    raise UnknownMessageFormatError(error_msg)


class UnknownMessageFormatError(SignalAPIError):
    """Exception raised when a message with an unknown format is encountered."""
