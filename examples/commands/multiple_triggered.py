from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextDataMessage, text_triggered
from signalbot.api.requests import SendMessage


class TriggeredCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "command_1, command_2 or command_3: 😤😤😤 Decorator example."

    # add case_sensitive=True for case sensitive triggers
    @text_triggered("command_1", "Command_2", "CoMmAnD_3")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="Multi command trigger"))
