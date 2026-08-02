from signalbot import DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage
from signalbot.context import DataMessageContext


class ReplyCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @text_triggered("reply")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.reply(SendMessage(text="This is a reply."))
