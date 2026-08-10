from signalbot import (
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    regex_triggered,
)


class RegexTriggeredCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "^[\\w\\.-]+@gmail\\.com$: 😤 Regular expression decorator example."

    @regex_triggered(r"^[\w\.-]+@gmail\.com$")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="Detected a Gmail address!"))
