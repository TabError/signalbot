from __future__ import annotations

import asyncio
import copy
import itertools
import re
import time
import traceback
import uuid
from collections import defaultdict
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, TypeAlias

import phonenumbers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from packaging.version import Version

from signalbot.api import ReceiveError, SignalAPI
from signalbot.api.generated.api.receipt import Receipt
from signalbot.api.generated.api.send_reaction_request import SendReactionRequest
from signalbot.api.generated.api.typing_indicator_request import TypingIndicatorRequest
from signalbot.api.incoming import (
    DataMessage,
    EditMessage,
    GroupUpdate,
    Reaction,
    ReceivedMessage,
    RemoteDelete,
    TypingMessage,
)
from signalbot.api.outgoing import CreatedPoll, SentMessage
from signalbot.auth import BasicAuthentication, BearerAuthentication
from signalbot.bot_config import (
    BasicAuthConfig,
    BearerAuthConfig,
    Config,
    InMemoryConfig,
    RedisConfig,
    SQLiteConfig,
    load_config,
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
)
from signalbot.logger import initialize_logger
from signalbot.message import UnknownMessageFormatError, parse
from signalbot.storage import RedisStorage, SQLiteStorage

if TYPE_CHECKING:
    from pathlib import Path

    from signalbot.api.generated import (
        About,
        CreatePollRequest,
        GroupEntry,
        RemoteDeleteRequest,
    )
    from signalbot.api.generated.api.receipt_type import ReceiptType
    from signalbot.api.incoming import Attachment
    from signalbot.api.outgoing import (
        SendMessage,
        SendMessageMultiple,
        UpdateContact,
        UpdateGroup,
    )

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


MIN_SIGNAL_CLI_REST_API_VERSION = Version("0.95.0")
"""
The minimum required version of `signal-cli-rest-api` for this version of `signalbot`.
"""


class SignalBot:
    """
    SignalBot is the main class for the bot. It provides methods to register handlers,
    start the bot, and interact with messages.

    Attributes:
        config (Config): The configuration for the bot.
        handlers: A list of registered handlers with their filters.
            Only available after `.start()` is called and `init_task` is done.
        groups (list): A list of groups the bot is a member of.
            Only available after `.start()` is called and `init_task` is done.
        storage (SQLiteStorage | RedisStorage): The storage backend used by the bot.
        scheduler (AsyncIOScheduler): The scheduler for running scheduled tasks.
        init_task: The initialization async task for the bot.
            Only available after `.start()` is called.
    """

    def __init__(self, config: Config | Mapping | Path | str) -> None:
        """Initilization for the SignalBot.

        Args:
            config: the configuration for the bot.

        Example config:
        ```python
        {
            phone_number: "+49123456789"
        }
        ```
        """
        self.config = load_config(config)

        self._logger = initialize_logger(self.config.logging_level)

        if isinstance(self.config.auth, BasicAuthConfig):
            auth = BasicAuthentication(
                self.config.auth.username, self.config.auth.password
            )
        elif isinstance(self.config.auth, BearerAuthConfig):
            auth = BearerAuthentication(self.config.auth.token)
        else:
            if self.config.auth is not None:
                error_msg = f"Unsupported auth type '{self.config.auth}', "
                error_msg += "no authentication will be used."
                self._logger.warning(error_msg)
            auth = None

        self._handlers_to_register: HandlerList = []  # populated by .register()
        self.handlers: HandlerList = []  # populated by .start()

        self.groups: list[GroupEntry] = []  # populated by .start()
        self._groups_by_id = {}
        self._groups_by_internal_id = {}
        self._groups_by_name = defaultdict(list)

        self.init_task: None | asyncio.Task = None

        try:
            self._signal = SignalAPI(
                self.config.signal_service,
                self.config.phone_number,
                auth,
                self.config.download_attachments,
                self.config.connection_mode,
            )
        except KeyError:
            raise SignalBotError("Could not initialize SignalAPI with given config")  # noqa: B904, EM101, TRY003

        try:
            self._event_loop = asyncio.get_event_loop()
        except RuntimeError:
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)

        self._q: asyncio.Queue[tuple[AnyHandler, ReceivedMessage, float]] = (
            asyncio.Queue()
        )

        self._produce_tasks: set[asyncio.Task] = set()
        self._consume_tasks: set[asyncio.Task] = set()

        try:
            self.scheduler = AsyncIOScheduler(event_loop=self._event_loop)
        except Exception as e:  # noqa: BLE001
            raise SignalBotError(f"Could not initialize scheduler: {e}")  # noqa: B904, EM102, TRY003

        if isinstance(self.config.storage, SQLiteConfig):
            self.storage = SQLiteStorage(
                self.config.storage.db,
                check_same_thread=self.config.storage.check_same_thread,
            )
            self._logger.info("sqlite storage initilized")
        elif isinstance(self.config.storage, RedisConfig):
            self.storage = RedisStorage(
                self.config.storage.host,
                self.config.storage.port,
                self.config.storage.password,
            )
            self._logger.info("redis storage initilized")
        elif isinstance(self.config.storage, InMemoryConfig):
            self.storage = SQLiteStorage()
            self._logger.info("in-memory storage initilized")
        else:
            self.storage = SQLiteStorage()
            self._logger.warning(
                " Using in-memory storage."
                " Restarting will delete the storage!"
                " Add storage: {'type': 'in-memory'}"
                " to the config to silence this error.",
            )

    def get_group(self, internal_id: str) -> GroupEntry | None:
        if internal_id in self._groups_by_internal_id:
            return copy.deepcopy(self._groups_by_internal_id[internal_id])
        return None

    def register(
        self,
        handler: AnyHandler,
        contacts: list[str] | bool = True,  # noqa: FBT001, FBT002
        groups: list[str] | bool = True,  # noqa: FBT001, FBT002
        f: Callable[[ReceivedMessage], bool] | None = None,
    ) -> None:
        """Register a handler with optional contact/group filters.

        Args:
            handler: Handler instance to register. This is typically a
                `DataMessageHandler`, but can be any combination of
                `DataMessageHandler`, `GroupUpdateHandler`,
                `RemoteDeleteHandler`, `TypingHandler`, and `ReactionHandler`.
            contacts: Allowed contacts or True for all.
            groups: Allowed groups or True for all.
            f: Optional function to further filter messages.
        """
        self._handlers_to_register.append((handler, contacts, groups, f))

    async def _resolve_handlers(self) -> None:
        self.handlers = []
        for handler, contacts, groups, f in self._handlers_to_register:
            group_ids = None

            if isinstance(groups, bool):
                group_ids = groups

            if isinstance(groups, list):
                group_ids = []
                for group in groups:
                    group_id = self._resolve_group_recipient(group)
                    if group_id is not None:
                        group_ids.append(group_id)
                    else:
                        error_msg = f"[Bot] [{handler.__class__.__name__}] '{group}' "
                        error_msg += "is not a valid group name or id"
                        self._logger.warning(error_msg)

            self.handlers.append((handler, contacts, group_ids, f))

    async def _async_post_init(self) -> None:
        await self._check_signal_service()
        await self._check_signal_cli_rest_api_version()
        await self._check_signal_cli_rest_api_mode()
        await self._refresh_groups()
        await self._resolve_handlers()
        await self._run_ready_handlers()
        await self._create_produce_consume_messages_tasks()

    async def _run_ready_handlers(self) -> None:
        for handler, *_ in self.handlers:
            if isinstance(handler, ReadyHandler):
                await handler.handle_ready(ReadyContext(self))

    async def _check_signal_service(self) -> None:
        while (await self._signal.check_signal_service()) is False:
            self._logger.error(
                "Cannot connect to the signal-cli-rest-api service, retrying"
            )
            await asyncio.sleep(self.config.retry_interval)

    async def _check_signal_cli_rest_api_version(self) -> None:
        version = (await self.about()).version

        # `unset` version is for preview versions of signal-cli-rest-api
        if version == "unset":
            self._logger.warning(
                "signal-cli-rest-api version is unset; skipping compatibility check",
            )
            return

        if Version(version) < MIN_SIGNAL_CLI_REST_API_VERSION:
            error_msg = f"Incompatible signal-cli-rest-api version, found {version}"
            error_msg += f", minimum required is {MIN_SIGNAL_CLI_REST_API_VERSION}"
            raise RuntimeError(error_msg)

    async def _check_signal_cli_rest_api_mode(self) -> None:
        mode = (await self.about()).mode
        if mode != "json-rpc":
            error_msg = (
                f"Wrong signal-cli-rest-api mode, found '{mode}', expected 'json-rpc'"
            )
            raise RuntimeError(error_msg)

    def _store_reference_to_task(
        self,
        task: asyncio.Task,
        task_set: set[asyncio.Task],
    ) -> None:
        # Keep a hard reference to the tasks, fixes Ruff's RUF006 rule
        task_set.add(task)
        task.add_done_callback(task_set.discard)

    def start(self, run_forever: bool = True) -> None:  # noqa: FBT001, FBT002
        """Start the bot event loop and scheduler.

        Args:
            run_forever: Whether to start the event loop or only add the task to it.
        """
        self.init_task = self._event_loop.create_task(
            self._rerun_on_exception(self._async_post_init),
        )

        if run_forever:
            self.scheduler.start()

            self._event_loop.run_forever()

    async def wait_until_ready(self) -> None:
        """Wait until the bot has finished connecting and is ready to send messages.

        Useful for code that runs outside of a `ReadyHandler`, e.g. a scheduled job
        that may execute before `start()` has finished initializing the bot.
        """
        if self.init_task is None:
            error_msg = "Bot is not initialized yet, call .start() first"
            raise SignalBotError(error_msg)

        await self.init_task

    async def about(self) -> About:
        """Return the signal-cli-rest-api about information."""
        return await self._signal.about()

    async def send(
        self,
        message: SendMessage,
    ) -> SentMessage:
        """Send or edit a message.

        Args:
            message: The message to send.

        Returns:
            A SentMessage instance.
        """
        if message.recipient is None:
            error_msg = "Recipient must be set in SendMessage"
            raise ValueError(error_msg)
        message.recipient = self._resolve_recipient(message.recipient)

        send_message_v2 = await message.to_generated(self.config.phone_number)
        send_message_response = await self._signal.send(send_message_v2)
        timestamp = int(send_message_response.timestamp)
        self._logger.info(
            f"[Bot] New message {timestamp} sent:\n{message.text}"  # noqa: G004
        )

        return SentMessage.from_send_message(message, timestamp)

    async def send_multiple(
        self,
        message: SendMessageMultiple,
    ) -> list[SentMessage]:
        """Send one message to multiple recipients.

        Args:
            message: The message payload with multiple recipients.

        Returns:
            A list of SentMessage instances, one per recipient.
        """
        message.recipients = [
            self._resolve_recipient(recipient) for recipient in message.recipients
        ]

        send_message_v2 = await message.to_generated(self.config.phone_number)
        send_message_response = await self._signal.send(send_message_v2)
        timestamp = int(send_message_response.timestamp)

        self._logger.info(
            f"[Bot] New message {timestamp} sent:\n{message.text}"  # noqa: G004
        )

        return SentMessage.from_send_message_multiple(message, timestamp)

    async def edit(
        self, new_message: SendMessage, original_message: SentMessage
    ) -> SentMessage:
        """Edit a message.

        Args:
            new_message: The message to send.
            original_message: The original message to edit.

        Returns:
            A SentMessage instance.
        """
        new_message.edit_timestamp = original_message.timestamp
        return await self.send(new_message)

    async def create_poll(
        self,
        create_poll_request: CreatePollRequest,
    ) -> CreatedPoll:
        """Create a poll.

        Args:
            create_poll_request: Request payload for poll creation.

        Returns:
            A CreatedPoll instance.
        """
        create_poll_request.recipient = self._resolve_recipient(
            create_poll_request.recipient
        )

        created_poll = await self._signal.poll(create_poll_request)
        timestamp = int(created_poll.timestamp)
        self._logger.info("[Bot] New poll created:\n%s", create_poll_request.question)

        return CreatedPoll.from_create_poll_request(create_poll_request, timestamp)

    async def react(self, message: SentMessage | DataMessage, emoji: str) -> None:
        """React to a message with an emoji.

        Args:
            message: The message to react to.
            emoji: Emoji reaction value.
        """
        if isinstance(message, SentMessage):
            if message.recipient is None:
                error_msg = "Recipient must be set in SendMessage"
                raise ValueError(error_msg)
            recipient = message.recipient
            target_author = self.config.phone_number
        else:
            recipient = message.source_or_group_uuid()
            if message.is_group():
                recipient = self._resolve_group_recipient(recipient)
                if recipient is None:
                    error_msg = "Cannot react to group message without group id"
                    raise ValueError(error_msg)

                target_author = message.source_uuid or message.source_number
                if target_author is None:
                    error_msg = "Cannot react to group message without source uuid"
                    raise ValueError(error_msg)
            else:
                target_author = message.source_uuid or message.source_number
                if target_author is None:
                    error_msg = "Message does not contain a source"
                    raise ValueError(error_msg)

        reaction_request = SendReactionRequest(
            recipient=recipient,
            reaction=emoji,
            target_author=target_author,
            timestamp=message.timestamp,
        )
        await self._signal.react(reaction_request)
        self._logger.info(f"[Bot] New reaction: {emoji}")  # noqa: G004

    async def receipt(
        self,
        message: DataMessage | EditMessage,
        receipt_type: ReceiptType,
    ) -> None:
        """Send a read or viewed receipt for a message if supported.

        Args:
            message: The message to acknowledge.
            receipt_type: The receipt type to send.
        """
        if message.is_group():
            self._logger.warning("[Bot] Receipts are not supported for groups")
            return

        recipient = self._resolve_recipient(message.source_or_group_uuid())
        receipt_request = Receipt(
            recipient=recipient, receipt_type=receipt_type, timestamp=message.timestamp
        )
        await self._signal.receipt(receipt_request)
        self._logger.info(f"[Bot] Receipt: {receipt_type}")  # noqa: G004

    async def start_typing(self, recipient: str) -> None:
        """Send a typing indicator to a recipient.

        Args:
            recipient: Message recipient.
        """
        recipient = self._resolve_recipient(recipient)
        await self._signal.start_typing(TypingIndicatorRequest(recipient=recipient))

    async def stop_typing(self, recipient: str) -> None:
        """Stop a typing indicator for a recipient.

        Args:
            recipient: Message recipient.
        """
        recipient = self._resolve_recipient(recipient)
        await self._signal.stop_typing(TypingIndicatorRequest(recipient=recipient))

    async def update_contact(
        self,
        update_contact: UpdateContact,
    ) -> None:
        """Update a contact's metadata.

        Args:
            update_contact: Contact update payload.
        """
        update_contact.recipient = self._resolve_recipient(update_contact.recipient)
        await self._signal.update_contact(update_contact)

    async def update_group(
        self,
        update_group: UpdateGroup,
    ) -> None:
        """Update a group's metadata.

        Args:
            update_group: Group update payload.
        """
        group_id_or_name = self._resolve_recipient(update_group.group_id_or_name)
        wire_request = await update_group.to_generated()
        await self._signal.update_group(group_id_or_name, wire_request)

    async def remote_delete(
        self,
        remote_delete_request: RemoteDeleteRequest,
    ) -> int:
        """Delete a previously sent message.

        Args:
            remote_delete_request: Request payload for remote delete.

        Returns:
            The timestamp of the delete action.
        """
        remote_delete_request.recipient = self._resolve_recipient(
            remote_delete_request.recipient
        )

        remote_delete_response = await self._signal.remote_delete(remote_delete_request)
        ret_timestamp = int(remote_delete_response.timestamp)
        self._logger.info(
            f"[Bot] Deleted message with timestamp {remote_delete_request.timestamp}"  # noqa: G004
        )

        return ret_timestamp

    async def delete_attachment(self, attachment: Attachment) -> None:
        """Delete an attachment from local storage.

        Args:
            attachment: Attachment to delete.
        """
        await self._signal.delete_attachment(attachment)

    async def _refresh_groups(self) -> None:
        # reset group lookups to avoid stale data
        self.groups = await self._signal.get_groups()

        self._groups_by_id: dict[str, GroupEntry] = {}
        self._groups_by_internal_id: dict[str, GroupEntry] = {}
        self._groups_by_name: defaultdict[str, list[GroupEntry]] = defaultdict(list)
        for group in self.groups:
            self._groups_by_id[group.id] = group
            self._groups_by_internal_id[group.internal_id] = group
            self._groups_by_name[group.name].append(group)

        self._logger.info(f"[Bot] {len(self.groups)} groups detected")  # noqa: G004

    async def _refresh_group_cache(self, group_internal_id: str) -> None:
        # look up group that requires update
        group = await self._signal.get_group(
            self._groups_by_internal_id[group_internal_id].id
        )

        current_group_name = self._groups_by_internal_id[group_internal_id].name
        # group name may have been updated
        self._groups_by_name[current_group_name] = [
            g for g in self._groups_by_name[current_group_name] if g.id != group.id
        ]
        self.groups = [
            group if g.internal_id == group_internal_id else g for g in self.groups
        ]
        self._groups_by_id[group.id] = group
        self._groups_by_internal_id[group.internal_id] = group
        self._groups_by_name[group.name].append(group)

        self._logger.info("[Bot] Group updated")

    async def _process_updates(self, message: ReceivedMessage) -> None:
        # Update groups if message is from an unknown group
        if (
            isinstance(message, GroupUpdate | DataMessage)
            and message.group_info is not None
            and message.group_info.group_id is not None
            and self._groups_by_internal_id.get(message.group_info.group_id) is None
        ):
            await self._refresh_groups()

        if isinstance(message, GroupUpdate):
            await self._refresh_group_cache(message.group_info.group_id)

    def _resolve_recipient(self, recipient: str) -> str:
        if self._is_phone_number(recipient):
            return recipient

        if self._is_valid_uuid(recipient):
            return recipient

        if self._is_username(recipient):
            return recipient

        group_id = self._resolve_group_recipient(recipient)
        if group_id is not None:
            return group_id

        raise SignalBotError("Cannot resolve recipient.")  # noqa: EM101, TRY003

    def _resolve_group_recipient(self, group_id_or_name: str) -> str | None:
        group = self._groups_by_id.get(group_id_or_name)
        if group is not None:
            return group.id

        if self._is_group_id(group_id_or_name):
            error_msg = f"[Bot] Group with id '{group_id_or_name}' not found. There "
            error_msg += "is a typo in id or the bot is not a member of the group."
            self._logger.warning(error_msg)
            return group_id_or_name

        group = self._groups_by_internal_id.get(group_id_or_name)
        if group is not None:
            return group.id

        group = self._get_group_by_name(group_id_or_name)
        if group is not None:
            return group.id

        return None

    def _is_phone_number(self, phone_number: str) -> bool:
        try:
            parsed_number = phonenumbers.parse(phone_number, region=None)
            return phonenumbers.is_valid_number(parsed_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

    def _is_valid_uuid(self, recipient_uuid: str) -> bool:
        try:
            uuid.UUID(str(recipient_uuid))
            return True  # noqa: TRY300
        except ValueError:
            return False

    def _is_username(self, recipient_username: str) -> bool:  # noqa: PLR0911
        """
        Check if username has correct format, as described in
        https://support.signal.org/hc/en-us/articles/6712070553754-Phone-Number-Privacy-and-Usernames#username_req
        Additionally, cannot have more than 9 digits and the digits cannot be 00.
        """
        split_username = recipient_username.split(".")
        if len(split_username) == 2:  # noqa: PLR2004
            characters = split_username[0]
            digits = split_username[1]
            if len(characters) < 3 or len(characters) > 32:  # noqa: PLR2004
                return False
            if not re.match(r"^[A-Za-z\d_]+$", characters):
                return False
            if len(digits) < 2 or len(digits) > 9:  # noqa: PLR2004
                return False
            try:
                digits = int(digits)
                if digits == 0:  # noqa: SIM103
                    return False
                return True  # noqa: TRY300
            except ValueError:
                return False
        else:
            return False

    def _is_group_id(self, group_id: str) -> bool:
        """Check if group_id has the right format, e.g.

              random string                                              length 66
              ↓                                                          ↓
        group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm=
        ↑                                                                ↑
        prefix                                                           suffix
        """
        if group_id is None:
            return False

        return re.match(r"^group\.[a-zA-Z0-9]{59}=$", group_id)

    def _is_internal_id(self, internal_id: str) -> bool:
        if internal_id is None:
            return False
        return internal_id[-1] == "="

    def _get_group_by_name(self, group_name: str) -> GroupEntry | None:
        groups = self._groups_by_name.get(group_name)
        if groups is not None:
            if len(groups) > 1:
                error_msg = f"[Bot] There is more than one group named '{group_name}',"
                error_msg += " using the first one."
                self._logger.warning(error_msg)
            return groups[0]
        return None

    # see https://stackoverflow.com/questions/55184226/catching-exceptions-in-individual-tasks-and-restarting-them
    async def _rerun_on_exception(self, coro, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        """Restart coroutine by waiting an exponential time deplay"""
        max_sleep = 5 * 60  # sleep for at most 5 mins until rerun
        reset = 3 * 60  # reset after 3 minutes running successfully
        init_sleep = 1  # always start with sleeping for 1 second

        next_sleep = init_sleep
        while True:
            start_t = int(time.monotonic())  # seconds

            try:
                return await coro(*args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001
                traceback.print_exc()

            end_t = int(time.monotonic())  # seconds

            if end_t - start_t < reset:
                sleep_t = next_sleep
                next_sleep = min(max_sleep, next_sleep * 2)  # double sleep time
            else:
                next_sleep = init_sleep  # reset sleep time
                sleep_t = next_sleep

            self._logger.warning(f"Restarting coroutine in {sleep_t} seconds")  # noqa: G004
            await asyncio.sleep(sleep_t)

    async def _create_produce_consume_messages_tasks(
        self,
        producers: int = 1,
        consumers: int = 3,
    ) -> None:
        for task in itertools.chain(self._consume_tasks, self._produce_tasks):
            task.cancel()

        self._produce_tasks.clear()

        for n in range(1, producers + 1):
            produce_task = self._rerun_on_exception(self._produce, n)
            produce_task = asyncio.create_task(produce_task)
            self._store_reference_to_task(produce_task, self._produce_tasks)

        self._consume_tasks.clear()

        for n in range(1, consumers + 1):
            consume_task = self._rerun_on_exception(self._consume, n)
            consume_task = asyncio.create_task(consume_task)
            self._store_reference_to_task(consume_task, self._consume_tasks)

    async def _produce(self, name: int) -> None:
        self._logger.info(f"[Bot] Producer #{name} started")  # noqa: G004
        try:
            async for raw_message in self._signal.receive():
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
            group_id = self._groups_by_internal_id.get(message.source_or_group_uuid())
            if group_id is not None:
                group_id = group_id.id
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
                    await handler.handle_data_message(DataMessageContext(self, message))
            elif isinstance(message, GroupUpdate):
                if isinstance(handler, GroupUpdateHandler):
                    await handler.handle_group_update(GroupUpdateContext(self, message))
            elif isinstance(message, RemoteDelete):
                if isinstance(handler, RemoteDeleteHandler):
                    await handler.handle_remote_delete(
                        RemoteDeleteContext(self, message)
                    )
            elif isinstance(message, TypingMessage):
                if isinstance(handler, TypingHandler):
                    await handler.handle_typing(TypingContext(self, message))
            elif isinstance(message, Reaction):
                if isinstance(handler, ReactionHandler):
                    await handler.handle_reaction(ReactionContext(self, message))
            else:
                error_msg = f"[Bot] Unknown message type: {type(message)}, "
                error_msg += "skipping handler execution"
                self._logger.warning(error_msg)
        except Exception:
            self._logger.exception(f"[{handler.__class__.__name__}]")  # noqa: G004
            raise

        # done
        self._q.task_done()


class SignalBotError(Exception):
    pass
