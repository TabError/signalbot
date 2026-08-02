from signalbot import Command, ContextDataMessage, regex_triggered
from signalbot.api.requests import SendMessage


class RegexTriggeredCommand(Command):
    def help_message(self) -> str:
        return "^[\\w\\.-]+@gmail\\.com$: 😤 Regular expression decorator example."

    @regex_triggered(r"^[\w\.-]+@gmail\.com$")
    async def handle(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="Detected a Gmail address!"))
