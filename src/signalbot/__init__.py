import importlib.metadata

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
from signalbot.client import ConnectionMode
from signalbot.context import (
    DataMessageContext,
    GroupUpdateContext,
    ReactionContext,
    ReadyContext,
    RemoteDeleteContext,
    TypingContext,
)
from signalbot.errors import SignalAPIError, SignalBotError
from signalbot.handlers import (
    AnyHandler,
    DataMessageHandler,
    GroupUpdateHandler,
    HandlerList,
    ReactionHandler,
    ReadyHandler,
    RemoteDeleteHandler,
    TypingHandler,
    reaction_triggered,
    regex_triggered,
    text_triggered,
)
from signalbot.logger import LOGGER_NAME
from signalbot.storage import StorageError

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "AnyHandler",
    "BasicAuthConfig",
    "BearerAuthConfig",
    "Config",
    "ConnectionMode",
    "DataMessageContext",
    "DataMessageHandler",
    "GroupUpdateContext",
    "GroupUpdateHandler",
    "HandlerList",
    "InMemoryConfig",
    "ReactionContext",
    "ReactionHandler",
    "ReadyContext",
    "ReadyHandler",
    "RedisConfig",
    "RemoteDeleteContext",
    "RemoteDeleteHandler",
    "SQLiteConfig",
    "SignalAPIError",
    "SignalBot",
    "SignalBotError",
    "StorageError",
    "TypingContext",
    "TypingHandler",
    "reaction_triggered",
    "regex_triggered",
    "text_triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
