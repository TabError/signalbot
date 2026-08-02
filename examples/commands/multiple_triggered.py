from signalbot import Command, ContextDataMessage, text_triggered
from signalbot.api.requests import SendMessage


class TriggeredCommand(Command):
    def help_message(self) -> str:
        return "command-1, command-2 or command-3: 😤😤😤 Decorator example."

    # add case_sensitive=True for case sensitive triggers
    @text_triggered("command-1", "Command-2", "CoMmAnD-3")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="Multi command trigger"))
