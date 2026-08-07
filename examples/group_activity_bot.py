import os

from examples.timestamps import local_datetime_str_from_timestamp
from signalbot import (
    Config,
    DataMessageContext,
    DataMessageHandler,
    GroupUpdateContext,
    GroupUpdateHandler,
    SendMessage,
    SignalBot,
    text_triggered,
)


class GroupActivityHandler(DataMessageHandler, GroupUpdateHandler):
    """Tracks the most recent group update and answers a query about it.

    `handle_group_update` records who changed the group and when;
    `handle_data_message` answers the `last-change` command by reading that
    same cache. Combining both handlers on one instance is what lets them
    share `_last_update` directly instead of through a database or some other
    out-of-process channel.
    """

    def __init__(self) -> None:
        super().__init__()
        self._last_update: dict[str, tuple[str, str]] = {}

    async def handle_group_update(self, context: GroupUpdateContext) -> None:
        group_info = context.message.group_info
        if group_info.group_id is None:
            return

        who = context.message.source_name or context.message.source_name
        when = local_datetime_str_from_timestamp(context.message.timestamp)
        self._last_update[group_info.group_id] = (who or "someone", when)

    @text_triggered("last-change")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        group_info = context.message.group_info
        group_id = group_info.group_id if group_info is not None else None

        if group_id is None or group_id not in self._last_update:
            await context.send(SendMessage(text="No group changes seen yet."))
            return

        who, when = self._last_update[group_id]
        message = f"{who} last changed this group at {when}."
        await context.send(SendMessage(text=message))


if __name__ == "__main__":
    bot = SignalBot(Config(phone_number=os.environ["PHONE_NUMBER"]))
    bot.register(GroupActivityHandler(), contacts=False, groups=True)
    bot.start()
