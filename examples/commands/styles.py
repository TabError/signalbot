from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, triggered
from signalbot.api.requests import SendMessage


class StylesCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "styles: 🎨 Demonstrates different text styles."

    @triggered("styles")
    async def handle_data_message(self, context: Context) -> None:
        await context.send(SendMessage(text="**Bold style**", text_mode="styled"))
        await context.send(SendMessage(text="*Italic style*", text_mode="styled"))
        await context.send(
            SendMessage(text="~Strikethrough style~", text_mode="styled")
        )
        await context.send(SendMessage(text="||Spoiler style||", text_mode="styled"))
        await context.send(SendMessage(text="`Monospaced style`", text_mode="styled"))
