from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.messages import SendMessageMultiple


class BroadcastCommand(DataMessageHandler):
    def __init__(self, recipients: list[str]) -> None:
        self.recipients = recipients

    def help_message(self) -> str:
        return "broadcast: 📢 Send the same message to multiple recipients at once."

    @text_triggered("broadcast")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.bot.messages.send_multiple(
            SendMessageMultiple(
                recipients=self.recipients, text="📢 Broadcast message!"
            )
        )
