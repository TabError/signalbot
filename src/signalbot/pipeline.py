from __future__ import annotations

import asyncio
import itertools
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

from signalbot.api import ReceiveError
from signalbot.api.incoming import (
    DataMessage,
    GroupUpdate,
    Reaction,
    ReceivedMessage,
    RemoteDelete,
    TypingMessage,
    UnknownMessageFormatError,
    parse,
)
from signalbot.context import (
    DataMessageContext,
    GroupUpdateContext,
    ReactionContext,
    ReadyContext,
    RemoteDeleteContext,
    TypingContext,
)
from signalbot.errors import SignalBotError
from signalbot.handlers import (
    DataMessageHandler,
    GroupUpdateHandler,
    ReactionHandler,
    ReadyHandler,
    RemoteDeleteHandler,
    TypingHandler,
)
from signalbot.utils.retry import rerun_on_exception

if TYPE_CHECKING:
    import logging

    from signalbot.api import SignalAPI
    from signalbot.bot import SignalBot
    from signalbot.groups import GroupRegistry

AnyHandler: TypeAlias = (
    DataMessageHandler
    | GroupUpdateHandler
    | RemoteDeleteHandler
    | TypingHandler
    | ReactionHandler
    | ReadyHandler
)

HandlerList: TypeAlias = list[
    tuple[
        AnyHandler,
        list[str] | bool,  # contacts
        list[str] | bool | None,  # groups
        Callable[[ReceivedMessage], bool] | None,  # lambda filter
    ]
]


class MessagePipeline:
    """Owns handler registration and the produce/consume queue that dispatches
    incoming messages to registered handlers.
    """

    def __init__(
        self,
        bot: SignalBot,
        signal: SignalAPI,
        groups: GroupRegistry,
        logger: logging.Logger,
    ) -> None:
        self._bot = bot
        self._signal = signal
        self._groups = groups
        self._logger = logger

        self._handlers_to_register: HandlerList = []  # populated by .register()
        self.handlers: HandlerList = []  # populated by .resolve_handlers()

        self._q: asyncio.Queue[tuple[AnyHandler, ReceivedMessage, float]] = (
            asyncio.Queue()
        )
        self._produce_tasks: set[asyncio.Task] = set()
        self._consume_tasks: set[asyncio.Task] = set()

    def register(
        self,
        handler: AnyHandler,
        contacts: list[str] | bool = True,  # noqa: FBT001, FBT002
        groups: list[str] | bool = True,  # noqa: FBT001, FBT002
        f: Callable[[ReceivedMessage], bool] | None = None,
    ) -> None:
        self._handlers_to_register.append((handler, contacts, groups, f))

    async def resolve_handlers(self) -> None:
        self.handlers = []
        for handler, contacts, groups, f in self._handlers_to_register:
            group_ids = None

            if isinstance(groups, bool):
                group_ids = groups

            if isinstance(groups, list):
                group_ids = []
                for group in groups:
                    group_id = self._groups.resolve(group)
                    if group_id is not None:
                        group_ids.append(group_id)
                    else:
                        error_msg = f"[Bot] [{handler.__class__.__name__}] '{group}' "
                        error_msg += "is not a valid group name or id"
                        self._logger.warning(error_msg)

            self.handlers.append((handler, contacts, group_ids, f))

    async def run_ready_handlers(self) -> None:
        for handler, *_ in self.handlers:
            if isinstance(handler, ReadyHandler):
                await handler.handle_ready(ReadyContext(self._bot))

    def _store_reference_to_task(
        self,
        task: asyncio.Task,
        task_set: set[asyncio.Task],
    ) -> None:
        # Keep a hard reference to the tasks, fixes Ruff's RUF006 rule
        task_set.add(task)
        task.add_done_callback(task_set.discard)

    async def stop(self) -> None:
        """Cancel all running producer/consumer tasks and wait for them to exit."""
        # Excludes the calling task itself: `stop()` may be invoked from within
        # a handler running on one of these tasks (e.g. a "close" command), and
        # a task cannot cancel-and-await itself without deadlocking.
        current = asyncio.current_task()
        tasks = [
            task
            for task in itertools.chain(self._consume_tasks, self._produce_tasks)
            if task is not current
        ]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def start(
        self,
        producers: int = 1,
        consumers: int = 3,
    ) -> None:
        await self.stop()

        self._produce_tasks.clear()

        for n in range(1, producers + 1):
            produce_task = rerun_on_exception(self._produce, n, logger=self._logger)
            produce_task = asyncio.create_task(produce_task)
            self._store_reference_to_task(produce_task, self._produce_tasks)

        self._consume_tasks.clear()

        for n in range(1, consumers + 1):
            consume_task = rerun_on_exception(self._consume, n, logger=self._logger)
            consume_task = asyncio.create_task(consume_task)
            self._store_reference_to_task(consume_task, self._consume_tasks)

    async def _process_updates(self, message: ReceivedMessage) -> None:
        # Update groups if message is from an unknown group
        if (
            isinstance(message, GroupUpdate | DataMessage)
            and message.group_info is not None
            and message.group_info.group_id is not None
            and self._groups._get_internal(message.group_info.group_id) is None  # noqa: SLF001
        ):
            await self._groups.refresh()

        if isinstance(message, GroupUpdate):
            await self._groups.refresh_one(message.group_info.group_id)

    async def _produce(self, name: int) -> None:
        self._logger.info(f"[Bot] Producer #{name} started")  # noqa: G004
        try:
            async for raw_message in self._signal.messages.receive():
                self._logger.info(f"[Raw Message] {raw_message}")  # noqa: G004

                try:
                    message = await parse(self._signal, raw_message)
                except UnknownMessageFormatError:
                    continue

                await self._process_updates(message)

                await self._dispatch_to_handlers(message)

        except ReceiveError as e:
            # TODO: retry strategy  # noqa: TD002, TD003
            raise SignalBotError(f"Cannot receive messages: {e}")  # noqa: B904, EM102, TRY003

    def _should_react_for_contact(
        self,
        message: ReceivedMessage,
        contacts: list[str] | bool,  # noqa: FBT001
        group_ids: list[str] | bool,  # noqa: FBT001
    ) -> bool:
        """Is the handler activated for a certain chat or group?"""
        # Case 1: Private message
        if message.is_private():
            # a) registered for all numbers
            if isinstance(contacts, bool) and contacts:
                return True

            # b) whitelisted numbers
            if isinstance(contacts, list) and (
                message.source_number in contacts or message.source_uuid in contacts
            ):
                return True

        # Case 2: Group message
        if message.is_group():
            # a) registered for all groups
            if isinstance(group_ids, bool) and group_ids:
                return True

            # b) whitelisted group ids
            group = self._groups._get_internal(message.source_or_group_id())  # noqa: SLF001
            group_id = group.id if group is not None else None
            if isinstance(group_ids, list) and group_id and group_id in group_ids:
                return True

        return False

    def _should_react_for_lambda(
        self,
        message: ReceivedMessage,
        f: Callable[[ReceivedMessage], bool] | None = None,
    ) -> bool:
        if f is None:
            return True

        return f(message)

    async def _dispatch_to_handlers(self, message: ReceivedMessage) -> None:
        for handler, contacts, group_ids, f in self.handlers:
            if not self._should_react_for_contact(message, contacts, group_ids):
                continue

            if not self._should_react_for_lambda(message, f):
                continue

            await self._q.put((handler, message, time.perf_counter()))

    async def _consume(self, name: int) -> None:
        self._logger.info(f"[Bot] Consumer #{name} started")  # noqa: G004
        while True:
            try:
                await self._consume_new_item(name)
            except Exception:  # noqa: BLE001, S112
                continue

    async def _consume_new_item(self, name: int) -> None:  # noqa: C901
        handler, message, t = await self._q.get()
        now = time.perf_counter()
        self._logger.info(
            f"[Bot] Consumer #{name} got new job in {now - t:0.5f} seconds"  # noqa: G004
        )

        # dispatch to whichever handler role(s) `handler` implements
        try:
            if isinstance(message, DataMessage):
                if isinstance(handler, DataMessageHandler):
                    await handler.handle_data_message(
                        DataMessageContext(self._bot, message)
                    )
            elif isinstance(message, GroupUpdate):
                if isinstance(handler, GroupUpdateHandler):
                    await handler.handle_group_update(
                        GroupUpdateContext(self._bot, message)
                    )
            elif isinstance(message, RemoteDelete):
                if isinstance(handler, RemoteDeleteHandler):
                    await handler.handle_remote_delete(
                        RemoteDeleteContext(self._bot, message)
                    )
            elif isinstance(message, TypingMessage):
                if isinstance(handler, TypingHandler):
                    await handler.handle_typing(TypingContext(self._bot, message))
            elif isinstance(message, Reaction):
                if isinstance(handler, ReactionHandler):
                    await handler.handle_reaction(ReactionContext(self._bot, message))
            else:
                error_msg = f"[Bot] Unknown message type: {type(message)}, "
                error_msg += "skipping handler execution"
                self._logger.warning(error_msg)
        except Exception:
            self._logger.exception(f"[{handler.__class__.__name__}]")  # noqa: G004
            raise

        # done
        self._q.task_done()
