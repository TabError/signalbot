from signalbot.api.receive_messages.attachments import Attachment
from signalbot.api.receive_messages.base_message import (
    BaseMessage,
    BaseMessageWithGroup,
)
from signalbot.api.receive_messages.data_message import ReceiveDataMessage
from signalbot.api.receive_messages.edit_message import EditMessage
from signalbot.api.receive_messages.group_update_message import GroupUpdateMessage
from signalbot.api.receive_messages.link_previews import Preview
from signalbot.api.receive_messages.received_message import ReceivedMessage
from signalbot.api.receive_messages.remote_delete import RemoteDelete
from signalbot.api.receive_messages.typing_message import TypingMessage

ReceivedMessageType = (
    ReceiveDataMessage | GroupUpdateMessage | RemoteDelete | TypingMessage | EditMessage
)

__all__ = [
    "Attachment",
    "BaseMessage",
    "BaseMessageWithGroup",
    "EditMessage",
    "GroupUpdateMessage",
    "Preview",
    "ReceiveDataMessage",
    "ReceivedMessage",
    "ReceivedMessageType",
    "RemoteDelete",
    "TypingMessage",
]
