from signalbot import DataMessageContext, DataMessageHandler, text_triggered


class ReactCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "send-reaction: 🎉 Send a reaction to a message."

    @text_triggered("send-reaction")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.react("🎉")
