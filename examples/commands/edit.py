import asyncio

from signalbot import Command, text_triggered
from signalbot.api.requests import SendMessage
from signalbot.context import ContextDataMessage


class EditCommand(Command):
    def help_message(self) -> str:
        return "edit: ✏️ Edit a message."

    @text_triggered("edit")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        sent_message = await context.send(
            SendMessage(text="This message will be edited in two seconds.")
        )
        await asyncio.sleep(2)
        await context.edit(
            SendMessage(text="This message has been edited."),
            sent_message,
        )
