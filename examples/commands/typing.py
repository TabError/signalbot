import asyncio

from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextDataMessage, triggered
from signalbot.api.requests import SendMessage


class TypingCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "typing: ⌨️ Demonstrates typing indicator for a few seconds."

    @triggered("typing")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.start_typing()
        seconds = 5
        await asyncio.sleep(seconds)
        await context.stop_typing()
        await context.send(SendMessage(text=f"Typed for {seconds}s"))
