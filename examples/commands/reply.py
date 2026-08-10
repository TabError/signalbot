from signalbot import (
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    text_triggered,
)


class ReplyCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @text_triggered("reply")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.reply(SendMessage(text="This is a reply."))
