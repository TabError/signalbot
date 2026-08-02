from signalbot.api.receive_messages.attachments import Attachment
from signalbot.api.receive_messages.base_message import (
    BaseMessage,
    BaseMessageWithGroup,
)
from signalbot.api.receive_messages.data_message import DataMessage
from signalbot.api.receive_messages.edit_message import EditMessage
from signalbot.api.receive_messages.group_update_message import GroupUpdateMessage
from signalbot.api.receive_messages.link_previews import Preview
from signalbot.api.receive_messages.reaction import Reaction
from signalbot.api.receive_messages.received_message import ReceivedMessage
from signalbot.api.receive_messages.remote_delete import RemoteDelete
from signalbot.api.receive_messages.typing_message import TypingMessage

ReceivedMessageType = (
    DataMessage
    | GroupUpdateMessage
    | RemoteDelete
    | TypingMessage
    | EditMessage
    | Reaction
)

__all__ = [
    "Attachment",
    "BaseMessage",
    "BaseMessageWithGroup",
    "DataMessage",
    "EditMessage",
    "GroupUpdateMessage",
    "Preview",
    "Reaction",
    "ReceivedMessage",
    "ReceivedMessageType",
    "RemoteDelete",
    "TypingMessage",
]
