from abc import abstractmethod

from signalbot import Command, ContextDataMessage, Handler, text_triggered
from signalbot.api.requests import SendMessage


class CommandWithHelpMessage(Handler):
    @abstractmethod
    def help_message(self) -> str:
        pass


class HelpCommand(CommandWithHelpMessage, Command):
    def help_message(self) -> str:
        return "help: 🆘 Shows information about available commands."

    @text_triggered("help")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        help_message = "Available commands:\n"
        for command, _, _, _ in self.bot.commands:
            if isinstance(command, CommandWithHelpMessage):
                help_message += f"\t - {command.help_message()}\n"
        await context.send(SendMessage(text=help_message))
