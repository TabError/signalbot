from signalbot import (
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    text_triggered,
)


class AboutCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "about: 📋 Show signal-cli-rest-api version information."

    @text_triggered("about")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        about = await context.bot.general.about()
        await context.send(
            SendMessage(text=f"signal-cli-rest-api version: {about.version}")
        )
