from examples.commands.help import CommandWithHelpMessage
from signalbot import Context, regex_triggered
from signalbot.api.requests import SendMessage


class RegexTriggeredCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "^[\\w\\.-]+@gmail\\.com$: 😤 Regular expression decorator example."

    @regex_triggered(r"^[\w\.-]+@gmail\.com$")
    async def handle_data_message(self, context: Context) -> None:
        await context.send(SendMessage(text="Detected a Gmail address!"))
