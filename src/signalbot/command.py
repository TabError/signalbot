from __future__ import annotations

import functools
import re
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from signalbot.context import (
    ContextDataMessage,
    ContextReaction,
)

T = TypeVar("T")
P = ParamSpec("P")

if TYPE_CHECKING:
    from collections.abc import Callable

    from signalbot.bot import SignalBot
    from signalbot.context import (
        ContextGroupUpdateMessage,
        ContextRemoteDelete,
        ContextTypingMessage,
    )


def regex_triggered(
    *by: str | re.Pattern[str],
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to trigger a command if the message text matches any of the provided
    regex patterns.

    Args:
        *by: A variable number of strings or compiled regex patterns to match the
            message text against.
    """

    def decorator_regex_triggered(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper_regex_triggered(
            *args: P.args, **kwargs: P.kwargs
        ) -> T | None:
            context = args[1]
            if not isinstance(context, ContextDataMessage):
                error_msg = "regex_triggered decorator can only be used with "
                error_msg += "DataMessageHandler.handle."
                raise TypeError(error_msg)

            text = context.message.text
            if text is None:
                return None
            matches = [bool(re.search(pattern, text)) for pattern in by]
            if True not in matches:
                return None
            return await func(*args, **kwargs)

        return wrapper_regex_triggered

    return decorator_regex_triggered


def text_triggered(
    *by: str, case_sensitive: bool = False
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to trigger a command if the message text matches any of the provided
    strings.

    Args:
        *by: A variable number of strings to match the message text against.
        case_sensitive: Whether the matching should be case sensitive.
    """

    def decorator_triggered(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper_triggered(*args: P.args, **kwargs: P.kwargs) -> T | None:
            context = args[1]
            if not isinstance(context, ContextDataMessage):
                error_msg = "regex_triggered decorator can only be used with "
                error_msg += "DataMessageHandler.handle."
                raise TypeError(error_msg)

            text = context.message.text
            if text is None:
                return None

            by_words = by
            if not case_sensitive:
                text = text.lower()
                by_words = [t.lower() for t in by_words]
            if text not in by_words:
                return None

            return await func(*args, **kwargs)

        return wrapper_triggered

    return decorator_triggered


def reaction_triggered(
    *by: str,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to trigger a command when a reaction is received.

    Args:
        *by: Optional emoji strings to filter on. If empty, triggers on any reaction.
    """

    def decorator_reaction_triggered(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper_reaction_triggered(
            *args: P.args, **kwargs: P.kwargs
        ) -> T | None:
            context = args[1]
            if not isinstance(context, ContextReaction):
                error_msg = "regex_triggered decorator can only be used with "
                error_msg += "handle_reaction."
                raise TypeError(error_msg)

            if by and context.message.emoji not in by:
                return None
            return await func(*args, **kwargs)

        return wrapper_reaction_triggered

    return decorator_reaction_triggered


class Handler(ABC):  # noqa: B024 -- intentionally has no abstract methods of its own
    """Shared bot-registration plumbing.

    This class only provides bot wiring and the `setup` hook. To actually react to
    something happening on Signal, subclass one of `DataMessageHandler`,
    `GroupUpdateHandler`, `RemoteDeleteHandler`, `TypingHandler`, or
    `ReactionHandler` (or several of them at once via multiple inheritance) rather
    than this class directly.
    """

    def __init__(self) -> None:
        # The bot attribute is assigned after calling bot.register(Handler())
        self._bot: SignalBot | None = None

    @property
    def bot(self) -> SignalBot:
        if self._bot is None:
            error_msg = "Handler is not registered with a bot."
            raise CommandError(error_msg)
        return self._bot

    @bot.setter
    def bot(self, bot: SignalBot) -> None:
        if self._bot is not None:
            error_msg = "Handler is already registered with a bot."
            raise CommandError(error_msg)
        self._bot = bot

    def setup(self) -> None:
        """Optional setup method that can be overridden by subclasses.
        This method is called after the handler is registered with the bot but
        before any data is retrieved, so it cannot access the group ids.
        """
        return


class DataMessageHandler(Handler):
    """Abstract base class for text, attachments and stickers messages.
    It handles both original messages and edited messages.

    To create a command, subclass this class and implement `handle`.
    Then, register the command with the bot using `bot.register(CommandSubclass)`.
    """

    @abstractmethod
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        """Method to handle a data or edit message.
        This method must be implemented by subclasses to define the behavior of the
            command.
        Args:
            context: Chat context containing the received message and other information.
                `context.message` is an `EditMessage` (a `ReceiveDataMessage` subclass)
                when the message is an edit of a previously sent message.
        """


class GroupUpdateHandler(Handler):
    """Abstract base class for reacting to group update events.

    Subclass this and implement `handle_group_update_message`, then register the
    instance with the bot using `bot.register(...)`. Combine with
    `DataMessageHandler` or the other handler classes via multiple inheritance if a
    single object should react to more than one kind of event.
    """

    @abstractmethod
    async def handle_group_update_message(
        self, context: ContextGroupUpdateMessage
    ) -> None:
        """Method to handle a group update message.
        This method must be implemented by subclasses to define the behavior of the
            handler.
        Args:
            context: Chat context containing the received message and other information.
        """


class RemoteDeleteHandler(Handler):
    """Abstract base class for reacting to remote delete events.

    Subclass this and implement `handle_remote_delete`, then register the instance
    with the bot using `bot.register(...)`. Combine with `DataMessageHandler` or
    the other handler classes via multiple inheritance if a single object should
    react to more than one kind of event.
    """

    @abstractmethod
    async def handle_remote_delete(self, context: ContextRemoteDelete) -> None:
        """Method to handle a remote delete message.
        This method must be implemented by subclasses to define the behavior of the
            handler.
        Args:
            context: Chat context containing the received message and other information.
        """


class TypingHandler(Handler):
    """Abstract base class for reacting to typing indicator events.

    Subclass this and implement `handle_typing_message`, then register the instance
    with the bot using `bot.register(...)`. Combine with `DataMessageHandler` or
    the other handler classes via multiple inheritance if a single object should
    react to more than one kind of event.
    """

    @abstractmethod
    async def handle_typing_message(self, context: ContextTypingMessage) -> None:
        """Method to handle a typing message.
        This method must be implemented by subclasses to define the behavior of the
            handler.
        Args:
            context: Chat context containing the received message and other information.
        """


class ReactionHandler(Handler):
    """Abstract base class for reacting to reaction events.

    Subclass this and implement `handle_reaction`, then register the instance with
    the bot using `bot.register(...)`. Combine with `DataMessageHandler` or the
    other handler classes via multiple inheritance if a single object should react
    to more than one kind of event.
    """

    @abstractmethod
    async def handle_reaction(self, context: ContextReaction) -> None:
        """Method to handle a reaction.
        This method must be implemented by subclasses to define the behavior of the
            handler.
        Args:
            context: Chat context containing the received message and other information.
        """


class CommandError(Exception):
    pass
