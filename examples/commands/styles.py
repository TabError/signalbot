from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextDataMessage, TextMode, text_triggered
from signalbot.api.requests import SendMessage


class StylesCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "styles: 🎨 Demonstrates different text styles."

    @text_triggered("styles")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(
            SendMessage(text="**Bold style**", text_mode=TextMode.STYLED)
        )
        await context.send(
            SendMessage(text="*Italic style*", text_mode=TextMode.STYLED)
        )
        await context.send(
            SendMessage(text="~Strikethrough style~", text_mode=TextMode.STYLED)
        )
        await context.send(
            SendMessage(text="||Spoiler style||", text_mode=TextMode.STYLED)
        )
        await context.send(
            SendMessage(text="`Monospaced style`", text_mode=TextMode.STYLED)
        )
