from signalbot.api.incoming.attachment import Attachment
from signalbot.api.incoming.base_message import (
    BaseMessage,
    BaseMessageWithGroup,
)
from signalbot.api.incoming.data_message import DataMessage
from signalbot.api.incoming.edit_message import EditMessage
from signalbot.api.incoming.envelope import ReceivedEnvelope
from signalbot.api.incoming.group_update_message import GroupInfo, GroupUpdateMessage
from signalbot.api.incoming.link_preview import LinkPreview
from signalbot.api.incoming.reaction import Reaction
from signalbot.api.incoming.remote_delete import RemoteDelete
from signalbot.api.incoming.typing_message import TypingMessage

ReceivedMessage = (
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
    "GroupInfo",
    "GroupUpdateMessage",
    "LinkPreview",
    "Reaction",
    "ReceivedEnvelope",
    "ReceivedMessage",
    "RemoteDelete",
    "TypingMessage",
]
