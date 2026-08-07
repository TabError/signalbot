from __future__ import annotations

from typing import TYPE_CHECKING

from signalbot import DataMessageHandler
from signalbot.api.generated import GroupEntry
from signalbot.test_utils import ChatTestCase
from tests.unit.conftest import TestCommon

if TYPE_CHECKING:
    from collections.abc import Callable

    from signalbot.context import DataMessageContext


class TestGetter(TestCommon):
    def test_null_group(self):
        assert not self.signal_bot.groups.get("none")

    async def test_get_group(
        self,
        mock_receive: Callable[[list[str]], None],
        mock_get_all_groups: Callable[[list[dict]], None],
        fake_group: dict,
    ):
        class GroupInspector(DataMessageHandler):
            def __init__(self):
                super().__init__()
                self.found_group = None

            async def handle_data_message(self, context: DataMessageContext) -> None:
                assert context.message.group_info is not None
                assert context.message.group_info.group_id is not None
                self.found_group = context.bot.groups.get(
                    context.message.group_info.group_id
                )

        mock_receive([ChatTestCase.new_message("Message 1")])
        mock_get_all_groups([fake_group])

        inspector = GroupInspector()
        self.signal_bot.register(inspector)

        await self.signal_bot._pipeline.resolve_handlers()

        await self.signal_bot._pipeline._produce(1337)

        await self.signal_bot._pipeline._consume_new_item(1337)

        expected_group = GroupEntry.model_validate(fake_group)
        assert inspector.found_group == expected_group
        assert inspector.found_group is not expected_group
