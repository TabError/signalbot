from signalbot import ContextDataMessage, DataMessageHandler, text_triggered
from signalbot.api.requests import SendMessage


class PingCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "ping: 🏓 Listen for a ping and send a pong reply."

    @text_triggered("ping")
    async def handle(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="pong"))
