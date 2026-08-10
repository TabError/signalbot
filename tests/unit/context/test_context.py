from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from signalbot.contacts import UpdateContact
from signalbot.context.context import Context
from signalbot.groups import UpdateGroup
from signalbot.messages import SendMessage
from signalbot.polls import CreatePoll
from tests.conftest import GROUP_INTERNAL_ID
from tests.unit.conftest import (
    PRIVATE_UUID,
    TestCommon,
    make_data_message,
    make_group_data_message,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

_private_message = make_data_message
_group_message = make_group_data_message


class TestContext(TestCommon):
    async def test_send_sets_recipient_from_message_source(self, mocker: MockerFixture):
        message = _private_message()
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = Context(self.signal_bot, message)
        outgoing = SendMessage(text="hi")

        result = await context.send(outgoing)

        send_mock.assert_awaited_once_with(outgoing, PRIVATE_UUID)
        assert result == "sent"

    async def test_send_sets_recipient_from_group_message(self, mocker: MockerFixture):
        message = _group_message()
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = Context(self.signal_bot, message)
        outgoing = SendMessage(text="hi")

        await context.send(outgoing)

        send_mock.assert_awaited_once_with(outgoing, GROUP_INTERNAL_ID)

    async def test_start_typing_uses_message_source(self, mocker: MockerFixture):
        message = _private_message()
        typing_mock = mocker.patch.object(
            self.signal_bot.messages, "start_typing", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        await context.start_typing()

        typing_mock.assert_awaited_once_with(PRIVATE_UUID)

    async def test_stop_typing_uses_message_source(self, mocker: MockerFixture):
        message = _private_message()
        typing_mock = mocker.patch.object(
            self.signal_bot.messages, "stop_typing", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        await context.stop_typing()

        typing_mock.assert_awaited_once_with(PRIVATE_UUID)

    async def test_update_contact_sets_recipient_for_private_message(
        self, mocker: MockerFixture
    ):
        message = _private_message()
        update_mock = mocker.patch.object(
            self.signal_bot.contacts, "update", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        update_contact = UpdateContact(name="Bob")
        await context.update_contact(update_contact)

        update_mock.assert_awaited_once_with(update_contact, PRIVATE_UUID)

    async def test_update_contact_raises_for_group_message(self, mocker: MockerFixture):
        message = _group_message()
        update_mock = mocker.patch.object(
            self.signal_bot.contacts, "update", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        with pytest.raises(ValueError, match="Cannot update contact for a group"):
            await context.update_contact(UpdateContact(name="Bob"))

        update_mock.assert_not_awaited()

    async def test_update_group_sets_group_id_for_group_message(
        self, mocker: MockerFixture
    ):
        message = _group_message()
        update_mock = mocker.patch.object(
            self.signal_bot.groups.actions, "update", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        update_group = UpdateGroup(name="New name")
        await context.update_group(update_group)

        update_mock.assert_awaited_once_with(update_group, GROUP_INTERNAL_ID)

    async def test_update_group_raises_for_private_message(self, mocker: MockerFixture):
        message = _private_message()
        update_mock = mocker.patch.object(
            self.signal_bot.groups.actions, "update", mocker.AsyncMock()
        )
        context = Context(self.signal_bot, message)

        with pytest.raises(ValueError, match="Cannot update group for a private"):
            await context.update_group(UpdateGroup(name="New name"))

        update_mock.assert_not_awaited()

    async def test_create_poll_sets_recipient_from_message_source(
        self, mocker: MockerFixture
    ):
        message = _private_message()
        create_mock = mocker.patch.object(
            self.signal_bot.polls, "create", mocker.AsyncMock(return_value="poll")
        )
        context = Context(self.signal_bot, message)

        poll = CreatePoll(question="Cats or dogs?", answers=["Cats", "Dogs"])
        result = await context.create_poll(poll)

        create_mock.assert_awaited_once_with(poll, PRIVATE_UUID)
        assert result == "poll"

    async def test_create_poll_sets_recipient_from_group_message(
        self, mocker: MockerFixture
    ):
        message = _group_message()
        create_mock = mocker.patch.object(
            self.signal_bot.polls, "create", mocker.AsyncMock(return_value="poll")
        )
        context = Context(self.signal_bot, message)

        poll = CreatePoll(question="Cats or dogs?", answers=["Cats", "Dogs"])
        await context.create_poll(poll)

        create_mock.assert_awaited_once_with(poll, GROUP_INTERNAL_ID)
