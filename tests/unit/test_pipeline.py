from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, cast

import pytest

from signalbot import DataMessageHandler, ReadyHandler
from signalbot.errors import SignalBotError
from signalbot.test_utils import ChatTestCase, DummyHandler
from tests.conftest import GROUP_ID
from tests.unit.conftest import (
    PRIVATE_NUMBER,
    PRIVATE_UUID,
    TestCommon,
    make_data_message,
    make_group_data_message,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from signalbot.context import DataMessageContext, ReadyContext
    from signalbot.messages import DataMessage, ReceivedMessage


class TestProducer(TestCommon):
    async def test_produce(
        self,
        mock_receive: Callable[[list[str]], None],
        mock_get_all_groups: Callable[[list[dict]], None],
        fake_group: dict,
    ):
        mock_receive(
            [
                ChatTestCase.new_message("Message 1"),
                ChatTestCase.new_message("Message 2"),
            ]
        )
        mock_get_all_groups([fake_group])

        # Any two commands
        self.signal_bot.register(DummyHandler())
        self.signal_bot.register(DummyHandler())
        await self.signal_bot._pipeline.resolve_handlers()

        await self.signal_bot._pipeline._produce(1337)

        assert self.signal_bot._pipeline._q.qsize() == 4


class TestRegisterHandler(TestCommon):
    def test_register_one_handler(self):
        self.signal_bot.register(DummyHandler())
        assert len(self.signal_bot._pipeline._handlers_to_register) == 1

    def test_register_three_handlers(self):
        self.signal_bot.register(DummyHandler())
        self.signal_bot.register(DummyHandler())
        self.signal_bot.register(DummyHandler())
        assert len(self.signal_bot._pipeline._handlers_to_register) == 3

    async def test_register_single_contact(self):
        user_number = "+49987654321"
        self.signal_bot.register(DummyHandler(), contacts=[user_number])
        await self.signal_bot._pipeline.resolve_handlers()
        assert self.signal_bot.handlers[0][1] == [user_number]

    async def test_register_multiple_contacts(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.register(
            DummyHandler(),
            contacts=[user_number1, user_number2, user_number3],
        )
        await self.signal_bot._pipeline.resolve_handlers()
        expected_user_chats = [user_number1, user_number2, user_number3]
        assert self.signal_bot.handlers[0][1] == expected_user_chats

    async def test_register_multiple_contacts_multiple_handlers(self):
        user_number1 = "+49987654321"
        user_number2 = "+49987654322"
        user_number3 = "+49987654323"
        self.signal_bot.register(DummyHandler(), contacts=[user_number1, user_number2])
        self.signal_bot.register(DummyHandler(), contacts=[user_number3])
        await self.signal_bot._pipeline.resolve_handlers()
        expected_user_chats_handler0 = [user_number1, user_number2]
        expected_user_chats_handler1 = [user_number3]
        assert self.signal_bot.handlers[0][1] == expected_user_chats_handler0
        assert self.signal_bot.handlers[1][1] == expected_user_chats_handler1


class TrackingReadyHandler(ReadyHandler):
    def __init__(self):
        super().__init__()
        self.contexts: list[ReadyContext] = []

    async def handle_ready(self, context: ReadyContext) -> None:
        self.contexts.append(context)


class TestReadyHandler(TestCommon):
    async def test_run_ready_handlers_calls_handle_ready(self):
        handler = TrackingReadyHandler()
        self.signal_bot.register(handler)
        await self.signal_bot._pipeline.resolve_handlers()

        await self.signal_bot._pipeline.run_ready_handlers()

        assert len(handler.contexts) == 1
        assert handler.contexts[0].bot is self.signal_bot

    async def test_run_ready_handlers_skips_non_ready_handlers(self):
        self.signal_bot.register(DummyHandler())
        await self.signal_bot._pipeline.resolve_handlers()

        # DummyHandler is a DataMessageHandler, not a ReadyHandler, so this must
        # not raise (e.g. from trying to call a non-existent handle_ready).
        await self.signal_bot._pipeline.run_ready_handlers()

    async def test_run_ready_handlers_calls_multiple_handlers_in_registration_order(
        self,
    ):
        calls = []

        class FirstHandler(ReadyHandler):
            async def handle_ready(self, context: ReadyContext) -> None:
                calls.append("first")

        class SecondHandler(ReadyHandler):
            async def handle_ready(self, context: ReadyContext) -> None:
                calls.append("second")

        self.signal_bot.register(FirstHandler())
        self.signal_bot.register(SecondHandler())
        await self.signal_bot._pipeline.resolve_handlers()

        await self.signal_bot._pipeline.run_ready_handlers()

        assert calls == ["first", "second"]

    async def test_wait_until_ready_raises_if_bot_not_started(self):
        with pytest.raises(SignalBotError):
            await self.signal_bot.wait_until_ready()

    async def test_wait_until_ready_awaits_init_task(self):
        async def noop() -> None:
            return None

        self.signal_bot.init_task = asyncio.create_task(noop())

        await self.signal_bot.wait_until_ready()

        assert self.signal_bot.init_task.done()


class TestPipelineStop(TestCommon):
    async def test_stop_is_safe_to_call_from_a_tracked_task(self):
        """A "close" command handler runs on one of the pipeline's own
        consumer tasks. Calling `pipeline.stop()` from there means `stop()`
        would cancel-and-await its own caller unless it excludes the current
        task, which previously caused a `RecursionError` / hang.
        """
        pipeline = self.signal_bot._pipeline

        async def self_stopping_consumer() -> None:
            await pipeline.stop()

        task = asyncio.create_task(self_stopping_consumer())
        pipeline._consume_tasks.add(task)

        await asyncio.wait_for(task, timeout=1)


_private_message = make_data_message
_group_message = make_group_data_message


class TestShouldReactForContact(TestCommon):
    @pytest.mark.parametrize(
        ("message_factory", "contacts", "group_ids", "expected"),
        [
            pytest.param(
                _private_message, True, True, True, id="private-contacts-true"
            ),
            pytest.param(
                _private_message, False, True, False, id="private-contacts-false"
            ),
            pytest.param(
                _private_message,
                [PRIVATE_NUMBER],
                False,
                True,
                id="private-matches-number",
            ),
            pytest.param(
                _private_message, [PRIVATE_UUID], False, True, id="private-matches-uuid"
            ),
            pytest.param(
                _private_message,
                ["+49000000000"],
                False,
                False,
                id="private-no-match",
            ),
            pytest.param(_group_message, True, True, True, id="group-ids-true"),
            pytest.param(_group_message, True, False, False, id="group-ids-false"),
        ],
    )
    def test_should_react_for_contact(
        self,
        message_factory: Callable[[], DataMessage],
        *,
        contacts: list[str] | bool,
        group_ids: list[str] | bool,
        expected: bool,
    ):
        pipeline = self.signal_bot._pipeline
        result = pipeline._should_react_for_contact(
            message_factory(), contacts=contacts, group_ids=group_ids
        )
        assert result is expected

    async def test_group_message_matches_whitelisted_group_id(
        self,
        mock_get_all_groups: Callable[[list[dict]], None],
        fake_group: dict,
    ):
        pipeline = self.signal_bot._pipeline
        mock_get_all_groups([fake_group])
        await self.signal_bot.groups.refresh()

        result = pipeline._should_react_for_contact(
            _group_message(), contacts=False, group_ids=[GROUP_ID]
        )

        assert result is True

    def test_group_message_does_not_match_unknown_group(self):
        pipeline = self.signal_bot._pipeline
        # Registry has no entry for the message's group, so `get_id` returns None.
        result = pipeline._should_react_for_contact(
            _group_message(), contacts=False, group_ids=[GROUP_ID]
        )
        assert result is False


class TestShouldReactForLambda(TestCommon):
    def test_no_filter_always_matches(self):
        pipeline = self.signal_bot._pipeline
        assert pipeline._should_react_for_lambda(_private_message(), None) is True

    def test_filter_true_matches(self):
        pipeline = self.signal_bot._pipeline
        result = pipeline._should_react_for_lambda(_private_message(), lambda _: True)
        assert result is True

    def test_filter_false_does_not_match(self):
        pipeline = self.signal_bot._pipeline
        result = pipeline._should_react_for_lambda(_private_message(), lambda _: False)
        assert result is False


class TrackingDataMessageHandler(DataMessageHandler):
    def __init__(self) -> None:
        self.contexts: list[DataMessageContext] = []

    async def handle_data_message(self, context: DataMessageContext) -> None:
        self.contexts.append(context)


class TestInvokeHandler(TestCommon):
    async def test_dispatches_known_message_type_to_matching_handler(self):
        pipeline = self.signal_bot._pipeline
        handler = TrackingDataMessageHandler()
        message = _private_message()

        await pipeline._invoke_handler(handler, message)

        assert len(handler.contexts) == 1
        assert handler.contexts[0].message is message

    async def test_unknown_message_type_logs_warning_and_does_not_raise(
        self, caplog: pytest.LogCaptureFixture
    ):
        pipeline = self.signal_bot._pipeline
        handler = TrackingDataMessageHandler()

        with caplog.at_level(logging.WARNING):
            await pipeline._invoke_handler(handler, cast("ReceivedMessage", object()))

        assert "Unknown message type" in caplog.text
        assert handler.contexts == []


class TestConsumeResilience(TestCommon):
    async def test_consume_keeps_running_after_a_handler_raises(self):
        pipeline = self.signal_bot._pipeline

        class ExplodingHandler(DataMessageHandler):
            async def handle_data_message(self, context: DataMessageContext) -> None:
                error_msg = "boom"
                raise RuntimeError(error_msg)

        succeeded = asyncio.Event()

        class RecoveringHandler(DataMessageHandler):
            async def handle_data_message(self, context: DataMessageContext) -> None:
                succeeded.set()

        await pipeline._q.put(
            (ExplodingHandler(), _private_message(), asyncio.get_running_loop().time())
        )
        await pipeline._q.put(
            (RecoveringHandler(), _private_message(), asyncio.get_running_loop().time())
        )

        consume_task = asyncio.create_task(pipeline._consume(1))
        try:
            await asyncio.wait_for(succeeded.wait(), timeout=1)
        finally:
            consume_task.cancel()
            await asyncio.gather(consume_task, return_exceptions=True)

    async def test_consume_new_item_reraises_handler_exceptions(self):
        pipeline = self.signal_bot._pipeline

        class ExplodingHandler(DataMessageHandler):
            async def handle_data_message(self, context: DataMessageContext) -> None:
                error_msg = "boom"
                raise RuntimeError(error_msg)

        await pipeline._q.put(
            (ExplodingHandler(), _private_message(), asyncio.get_running_loop().time())
        )

        with pytest.raises(RuntimeError, match="boom"):
            await pipeline._consume_new_item(1)
