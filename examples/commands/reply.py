from examples.commands.help import CommandWithHelpMessage
from signalbot import Command, text_triggered
from signalbot.api.requests import SendMessage
from signalbot.context import ContextDataMessage


class ReplyCommand(CommandWithHelpMessage, Command):
    def help_message(self) -> str:
        return "reply: 💬 Reply to a message."

    @text_triggered("reply")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.reply(SendMessage(text="This is a reply."))
