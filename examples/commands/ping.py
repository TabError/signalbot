from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextDataMessage, triggered
from signalbot.api.requests import SendMessage


class PingCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "ping: 🏓 Listen for a ping and send a pong reply."

    @triggered("ping")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="pong"))
