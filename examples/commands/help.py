from typing import Protocol, runtime_checkable

from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage


@runtime_checkable
class HasHelpMessage(Protocol):
    def help_message(self) -> str: ...


class HelpCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "help: 🆘 Shows information about available commands."

    @text_triggered("help")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        commands = []
        handlers = []
        for registered, _, _, _ in context.bot.handlers:
            if not isinstance(registered, HasHelpMessage):
                continue
            if isinstance(registered, DataMessageHandler):
                commands.append(registered.help_message())
            else:
                handlers.append(registered.help_message())

        sections = []
        if commands:
            entries = "\n".join(f"  {entry}" for entry in commands)
            sections.append(f"Commands:\n{entries}")
        if handlers:
            entries = "\n".join(f"  {entry}" for entry in handlers)
            sections.append(f"Handlers:\n{entries}")

        await context.send(SendMessage(text="\n".join(sections)))
