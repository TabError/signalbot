from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage


class CloseCommand(DataMessageHandler):
    """Demonstrates that `request_stop()` is safe to call from a handler,
    even though the handler itself runs on one of the tasks being shut down.
    """

    def help_message(self) -> str:
        return "close: 🛑 Gracefully shut the bot down."

    @text_triggered("close")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="Shutting down..."))
        context.bot.request_stop()
