from signalbot import Command, text_triggered
from signalbot.api.requests import SendMessage
from signalbot.context import ContextDataMessage


class ReplyCommand(Command):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @text_triggered("reply")
    async def handle(self, context: ContextDataMessage) -> None:
        await context.reply(SendMessage(text="This is a reply."))
