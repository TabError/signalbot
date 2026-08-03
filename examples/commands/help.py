from typing import Protocol, runtime_checkable

from signalbot import DataMessageContext, DataMessageHandler, SignalBot, text_triggered
from signalbot.api.outgoing import SendMessage


@runtime_checkable
class HasHelpMessage(Protocol):
    def help_message(self) -> str: ...


def build_help_message(bot: SignalBot) -> str:
    commands = []
    handlers = []
    for registered, _, _, _ in bot.handlers:
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

    return "\n".join(sections)


class HelpCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "help: 🆘 Shows information about available commands."

    @text_triggered("help")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text=build_help_message(context.bot)))
