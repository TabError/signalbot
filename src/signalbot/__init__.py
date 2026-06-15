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
    Command,
    CommandError,
    reaction_triggered,
    regex_triggered,
    triggered,
)
from signalbot.context import (
    ContextDataMessage,
    ContextEditMessage,
    ContextGroupUpdateMessage,
    ContextReaction,
    ContextRemoteDelete,
    ContextTypingMessage,
)
from signalbot.logger import (
    LOGGER_NAME,
    enable_console_logging,
)
from signalbot.message import UnknownMessageFormatError

__all__ = [
    "LOGGER_NAME",
    "MIN_SIGNAL_CLI_REST_API_VERSION",
    "BasicAuth",
    "BearerAuth",
    "Command",
    "CommandError",
    "Config",
    "ConnectionMode",
    "ContextDataMessage",
    "ContextEditMessage",
    "ContextGroupUpdateMessage",
    "ContextReaction",
    "ContextRemoteDelete",
    "ContextTypingMessage",
    "InMemoryConfig",
    "Preview",
    "ReceiveMessagesError",
    "RedisConfig",
    "SQLiteConfig",
    "SendMessageError",
    "SignalAPI",
    "SignalBot",
    "TextMode",
    "UnknownMessageFormatError",
    "enable_console_logging",
    "reaction_triggered",
    "regex_triggered",
    "triggered",
]

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"
