from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage


class PingCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "ping: 🏓 Listen for a ping and send a pong reply."

    @text_triggered("ping")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="pong"))
