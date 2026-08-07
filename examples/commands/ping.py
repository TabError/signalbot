from signalbot import (
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    text_triggered,
)


class PingCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "ping: 🏓 Listen for a ping and send a pong reply."

    @text_triggered("ping")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="pong"))
