from examples.commands.help import build_help_message
from signalbot import ReadyContext, ReadyHandler
from signalbot.api.outgoing import SendMessage


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
        help_message = build_help_message(context.bot)

        if self.recipient is not None:
            await context.bot.send(
                SendMessage(recipient=self.recipient, text=welcome_message)
            )
            await context.bot.send(
                SendMessage(recipient=self.recipient, text=help_message)
            )
        else:
            print(welcome_message)  # noqa: T201
            print(help_message)  # noqa: T201
