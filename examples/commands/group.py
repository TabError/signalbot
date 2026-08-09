from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.groups import UpdateGroup
from signalbot.messages import SendMessage


class UpdateGroupCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "set-group-description: 📝 Update this group's description."

    @text_triggered("set-group-description")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        # group_id_or_name is filled in by context.update_group() with the
        # group this message came from.
        await context.update_group(UpdateGroup(description="Managed by signalbot 🤖"))
        await context.send(SendMessage(text="Updated the group description."))
