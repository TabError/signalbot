import importlib.metadata

from signalbot.api import (
    ConnectionMode,
    ReceiveMessagesError,
    SendMessageError,
    SignalAPI,
)
from signalbot.api.generated.api import TextMode
from signalbot.api.receive_messages.link_previews import Preview
from signalbot.bot import (
    MIN_SIGNAL_CLI_REST_API_VERSION,
    SignalBot,
)
from signalbot.bot_config import (
    BasicAuth,
    BearerAuth,
    Config,
    InMemoryConfig,
    RedisConfig,
    SQLiteConfig,
)
from signalbot.command import (
    CommandError,
    DataMessageHandler,
    GroupUpdateHandler,
    Handler,
    ReactionHandler,
    ReadyHandler,
    RemoteDeleteHandler,
    TypingHandler,
    reaction_triggered,
    regex_triggered,
    text_triggered,
)
from signalbot.context import (
    ContextDataMessage,
    ContextGroupUpdateMessage,
    ContextReaction,
    ContextReady,
    ContextRemoteDelete,
    ContextTypingMessage,
)
from signalbot.logger import LOGGER_NAME
from signalbot.message import UnknownMessageFormatError

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "BasicAuth",
    "BearerAuth",
    "CommandError",
    "Config",
    "ConnectionMode",
    "ContextDataMessage",
    "ContextGroupUpdateMessage",
    "ContextReaction",
    "ContextReady",
    "ContextRemoteDelete",
    "ContextTypingMessage",
    "DataMessageHandler",
    "GroupUpdateHandler",
    "Handler",
    "InMemoryConfig",
    "Preview",
    "ReactionHandler",
    "ReadyHandler",
    "ReceiveMessagesError",
    "RedisConfig",
    "RemoteDeleteHandler",
    "SQLiteConfig",
    "SendMessageError",
    "SignalAPI",
    "SignalBot",
    "TextMode",
    "TypingHandler",
    "UnknownMessageFormatError",
    "reaction_triggered",
    "regex_triggered",
    "text_triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
