import importlib.metadata

from signalbot.api import (
    ConnectionMode,
    ReceiveError,
    SendError,
    SignalAPI,
    SignalAPIError,
)
from signalbot.api.generated import TextMode
from signalbot.api.incoming import (
    Attachment,
    DataMessage,
    EditMessage,
    GroupInfo,
    GroupUpdate,
    Reaction,
    ReceivedMessage,
    RemoteDelete,
    TypingMessage,
)
from signalbot.api.incoming import LinkPreview as ReceivedLinkPreview
from signalbot.api.outgoing import (
    CreatedPoll,
    LinkPreview,
    SendMessage,
    SendMessageMultiple,
    SentMessage,
    UpdateContact,
    UpdateGroup,
)
from signalbot.bot import (
    MIN_SIGNAL_CLI_REST_API_VERSION,
    SignalBot,
)
from signalbot.bot_config import (
    BasicAuthConfig,
    BearerAuthConfig,
    Config,
    InMemoryConfig,
    RedisConfig,
    SQLiteConfig,
)
from signalbot.context import (
    DataMessageContext,
    GroupUpdateContext,
    ReactionContext,
    ReadyContext,
    RemoteDeleteContext,
    TypingContext,
)
from signalbot.handlers import (
    DataMessageHandler,
    GroupUpdateHandler,
    ReactionHandler,
    ReadyHandler,
    RemoteDeleteHandler,
    TypingHandler,
    reaction_triggered,
    regex_triggered,
    text_triggered,
)
from signalbot.logger import LOGGER_NAME

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "Attachment",
    "BasicAuthConfig",
    "BearerAuthConfig",
    "Config",
    "ConnectionMode",
    "CreatedPoll",
    "DataMessage",
    "DataMessageContext",
    "DataMessageHandler",
    "EditMessage",
    "GroupInfo",
    "GroupUpdate",
    "GroupUpdateContext",
    "GroupUpdateHandler",
    "InMemoryConfig",
    "LinkPreview",
    "Reaction",
    "ReactionContext",
    "ReactionHandler",
    "ReadyContext",
    "ReadyHandler",
    "ReceiveError",
    "ReceivedLinkPreview",
    "ReceivedMessage",
    "RedisConfig",
    "RemoteDelete",
    "RemoteDeleteContext",
    "RemoteDeleteHandler",
    "SQLiteConfig",
    "SendError",
    "SendMessage",
    "SendMessageMultiple",
    "SentMessage",
    "SignalAPI",
    "SignalAPIError",
    "SignalBot",
    "TextMode",
    "TypingContext",
    "TypingHandler",
    "TypingMessage",
    "UpdateContact",
    "UpdateGroup",
    "reaction_triggered",
    "regex_triggered",
    "text_triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
