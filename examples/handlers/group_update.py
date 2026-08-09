from signalbot import GroupUpdateContext, GroupUpdateHandler
from signalbot.messages import SendMessage


class GroupUpdateNotifierHandler(GroupUpdateHandler):
    def help_message(self) -> str:
        return "Group update received: 👥 Notifies when a group's metadata changes."

    async def handle_group_update(self, context: GroupUpdateContext) -> None:
        group_info = context.message.group_info
        await context.send(
            SendMessage(
                text=(
                    f"Group '{group_info.group_name}' was updated "
                    f"(now at revision {group_info.revision})."
                )
            )
        )
