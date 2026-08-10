from examples.commands.help import build_help_messages
from signalbot import ReadyContext, ReadyHandler, SendMessage


class WelcomeHandler(ReadyHandler):
    def __init__(self, recipient: str | None) -> None:
        self.recipient = recipient

    async def handle_ready(self, context: ReadyContext) -> None:
        welcome_message = (
            "👋 Welcome! The bot is now connected and ready to receive messages.\n"
        )
        welcome_message += (
            "Send a text message with one of the commands or perform "
            "an action that a handler is listening to."
        )
        commands_msg, handlers_msg = build_help_messages(context.bot)

        if self.recipient is not None:
            await context.bot.messages.send(
                SendMessage(text=welcome_message), self.recipient
            )
            await context.bot.messages.send(
                SendMessage(text=commands_msg), self.recipient
            )
            await context.bot.messages.send(
                SendMessage(text=handlers_msg), self.recipient
            )
        else:
            print(welcome_message)
            print(commands_msg)
            print(handlers_msg)
