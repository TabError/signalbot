from signalbot import DataMessageContext, DataMessageHandler, TextMode, text_triggered
from signalbot.api.outgoing import SendMessage


class StylesCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "styles: 🎨 Demonstrates different text styles."

    @text_triggered("styles")
    async def handle_data_message(self, context: DataMessageContext) -> None:
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
