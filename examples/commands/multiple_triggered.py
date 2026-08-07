from signalbot import (
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    text_triggered,
)


class TriggeredCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "command-1, command-2 or command-3: 😤😤😤 Decorator example."

    # add case_sensitive=True for case sensitive triggers
    @text_triggered("command-1", "Command-2", "CoMmAnD-3")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="Multi command trigger"))
