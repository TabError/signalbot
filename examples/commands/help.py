from typing import Protocol, runtime_checkable

from signalbot import ContextDataMessage, DataMessageHandler, text_triggered
from signalbot.api.requests import SendMessage


@runtime_checkable
class HasHelpMessage(Protocol):
    def help_message(self) -> str: ...


class HelpCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "help: 🆘 Shows information about available commands."

    @text_triggered("help")
    async def handle(self, context: ContextDataMessage) -> None:
        commands = []
        handlers = []
        for registered, _, _, _ in self.bot.commands:
            if not isinstance(registered, HasHelpMessage):
                continue
            if isinstance(registered, DataMessageHandler):
                commands.append(registered.help_message())
            else:
                handlers.append(registered.help_message())

        sections = []
        if commands:
            entries = "\n".join(f"  {entry}" for entry in commands)
            sections.append(f"commands:\n{entries}")
        if handlers:
            entries = "\n".join(f"  {entry}" for entry in handlers)
            sections.append(f"handlers:\n{entries}")

        await context.send(SendMessage(text="\n".join(sections)))
