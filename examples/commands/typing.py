import asyncio

from signalbot import ContextDataMessage, DataMessageHandler, text_triggered
from signalbot.api.requests import SendMessage


class TypingCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "typing: ⌨️ Demonstrates typing indicator for a few seconds."

    @text_triggered("typing")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.start_typing()
        seconds = 5
        await asyncio.sleep(seconds)
        await context.stop_typing()
        await context.send(SendMessage(text=f"Typed for {seconds}s"))
