import importlib.metadata

from signalbot.api import (
    ConnectionMode,
    ReceiveError,
    SendError,
    SignalAPI,
)
from signalbot.api.generated.api import TextMode
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
from signalbot.message import UnknownMessageFormatError

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "BasicAuthConfig",
    "BearerAuthConfig",
    "Config",
    "ConnectionMode",
    "DataMessageContext",
    "DataMessageHandler",
    "GroupUpdateContext",
    "GroupUpdateHandler",
    "InMemoryConfig",
    "ReactionContext",
    "ReactionHandler",
    "ReadyContext",
    "ReadyHandler",
    "ReceiveError",
    "RedisConfig",
    "RemoteDeleteContext",
    "RemoteDeleteHandler",
    "SQLiteConfig",
    "SendError",
    "SignalAPI",
    "SignalBot",
    "TextMode",
    "TypingContext",
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
