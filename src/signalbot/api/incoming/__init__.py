from signalbot.api.incoming.attachment import Attachment
from signalbot.api.incoming.base_message import (
    BaseMessage,
    BaseMessageWithGroup,
)
from signalbot.api.incoming.data_message import DataMessage
from signalbot.api.incoming.edit_message import EditMessage
from signalbot.api.incoming.group_update import GroupInfo, GroupUpdate
from signalbot.api.incoming.link_preview import LinkPreview
from signalbot.api.incoming.reaction import Reaction
from signalbot.api.incoming.remote_delete import RemoteDelete
from signalbot.api.incoming.typing_message import TypingMessage

ReceivedMessage = (
    DataMessage | GroupUpdate | RemoteDelete | TypingMessage | EditMessage | Reaction
)

__all__ = [
    "Attachment",
    "BaseMessage",
    "BaseMessageWithGroup",
    "DataMessage",
    "EditMessage",
    "GroupInfo",
    "GroupUpdate",
    "LinkPreview",
    "Reaction",
    "ReceivedMessage",
    "RemoteDelete",
    "TypingMessage",
]
