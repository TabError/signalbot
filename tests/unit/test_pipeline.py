from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from signalbot import ReadyHandler
from signalbot.errors import SignalBotError
from signalbot.test_utils import ChatTestCase, DummyHandler
from tests.unit.conftest import TestCommon

if TYPE_CHECKING:
    from collections.abc import Callable

    from signalbot.context import ReadyContext


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
