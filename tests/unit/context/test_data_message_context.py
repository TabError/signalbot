from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from signalbot.context.data_message_context import DataMessageContext
from signalbot.messages import Mention, MessageMention, SendMessage
from signalbot.receipts import ReceiptType
from tests.unit.conftest import (
    PRIVATE_NUMBER,
    PRIVATE_UUID,
    TestCommon,
    make_data_message,
)

if TYPE_CHECKING:
    import pytest
    from pytest_mock import MockerFixture

    from signalbot.messages import DataMessage

SOURCE_UUID = PRIVATE_UUID
SOURCE_NUMBER = PRIVATE_NUMBER


def _message(**overrides: object) -> DataMessage:
    fields = {"timestamp": 1700000000000, "text": "original text", **overrides}
    return make_data_message(**fields)


class TestReply(TestCommon):
    async def test_reply_sets_quote_from_message(self, mocker: MockerFixture):
        message = _message()
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        result = await context.reply(SendMessage(text="my reply"))

        send_mock.assert_awaited_once()
        (sent_arg, recipient), _ = send_mock.call_args
        assert recipient == SOURCE_UUID
        assert sent_arg.text == "my reply"
        assert sent_arg.quote_author == SOURCE_UUID
        assert sent_arg.quote_text == "original text"
        assert sent_arg.quote_timestamp == 1700000000000
        assert result == "sent"

    async def test_reply_falls_back_to_source_number_for_quote_author(
        self, mocker: MockerFixture
    ):
        message = _message(source_uuid=None)
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.reply(SendMessage(text="my reply"))

        (sent_arg, _recipient), _ = send_mock.call_args
        assert sent_arg.quote_author == SOURCE_NUMBER

    async def test_reply_does_not_mutate_caller_message(self, mocker: MockerFixture):
        message = _message()
        mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)
        outgoing = SendMessage(text="my reply")

        await context.reply(outgoing)

        assert outgoing.quote_text is None

    async def test_reply_converts_mentions_dropping_ones_without_uuid(
        self, mocker: MockerFixture
    ):
        message = _message(
            mentions=[
                Mention(uuid="mentioned-uuid", start=0, length=3),
                Mention(uuid=None, number="+491111", start=5, length=2),
            ]
        )
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.reply(SendMessage(text="hi"))

        (sent_arg, _recipient), _ = send_mock.call_args
        assert sent_arg.quote_mentions == [
            MessageMention(author="mentioned-uuid", start=0, length=3)
        ]

    async def test_reply_with_no_mentions_leaves_quote_mentions_none(
        self, mocker: MockerFixture
    ):
        message = _message(mentions=None)
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.reply(SendMessage(text="hi"))

        (sent_arg, _recipient), _ = send_mock.call_args
        assert sent_arg.quote_mentions is None

    async def test_reply_with_only_uuidless_mentions_yields_none(
        self, mocker: MockerFixture
    ):
        message = _message(
            mentions=[Mention(uuid=None, number="+491111", start=0, length=2)]
        )
        send_mock = mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.reply(SendMessage(text="hi"))

        (sent_arg, _recipient), _ = send_mock.call_args
        assert sent_arg.quote_mentions is None

    async def test_reply_logs_warning_for_mention_without_uuid(
        self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
    ):
        message = _message(
            mentions=[Mention(uuid=None, number="+491111", start=0, length=2)]
        )
        mocker.patch.object(
            self.signal_bot.messages, "send", mocker.AsyncMock(return_value="sent")
        )
        context = DataMessageContext(self.signal_bot, message)

        with caplog.at_level(logging.WARNING):
            await context.reply(SendMessage(text="hi"))

        assert "no uuid" in caplog.text


class TestEdit(TestCommon):
    async def test_edit_delegates_to_message_actions(self, mocker: MockerFixture):
        message = _message()
        edit_mock = mocker.patch.object(
            self.signal_bot.messages, "edit", mocker.AsyncMock(return_value="edited")
        )
        context = DataMessageContext(self.signal_bot, message)
        outgoing = SendMessage(text="updated text")
        original = mocker.Mock()

        result = await context.edit(outgoing, original_message=original)

        edit_mock.assert_awaited_once_with(outgoing, original)
        assert result == "edited"


class TestReact(TestCommon):
    async def test_react_delegates_to_reactions(self, mocker: MockerFixture):
        message = _message()
        react_mock = mocker.patch.object(
            self.signal_bot.reactions, "react", mocker.AsyncMock()
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.react("👍")

        react_mock.assert_awaited_once_with(message, "👍")


class TestSendReceipt(TestCommon):
    async def test_send_receipt_delegates_to_receipts(self, mocker: MockerFixture):
        message = _message()
        receipt_mock = mocker.patch.object(
            self.signal_bot.receipts, "send", mocker.AsyncMock()
        )
        context = DataMessageContext(self.signal_bot, message)

        await context.send_receipt(ReceiptType.READ)

        receipt_mock.assert_awaited_once_with(message, ReceiptType.READ)


class TestRemoteDelete(TestCommon):
    async def test_remote_delete_delegates_to_messages(self, mocker: MockerFixture):
        message = _message()
        remote_delete_mock = mocker.patch.object(
            self.signal_bot.messages, "remote_delete", mocker.AsyncMock(return_value=42)
        )
        context = DataMessageContext(self.signal_bot, message)
        sent_message = mocker.Mock()

        result = await context.remote_delete(sent_message)

        remote_delete_mock.assert_awaited_once_with(sent_message)
        assert result == 42


class TestDeleteAttachment(TestCommon):
    async def test_delete_attachment_delegates_to_attachments(
        self, mocker: MockerFixture
    ):
        message = _message()
        delete_mock = mocker.patch.object(
            self.signal_bot.attachments, "delete", mocker.AsyncMock()
        )
        context = DataMessageContext(self.signal_bot, message)
        attachment = mocker.Mock()

        await context.delete_attachment(attachment)

        delete_mock.assert_awaited_once_with(attachment)
