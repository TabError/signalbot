from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered


class ReplyCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @triggered("reply")
    async def handle_data_message(self, context: Context) -> None:
        await context.reply("This is a reply.")
