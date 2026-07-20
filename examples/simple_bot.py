import logging
import os

from signalbot import (
    Command,
    Config,
    ContextDataMessage,
    SignalBot,
    text_triggered,
)
from signalbot.api.requests import SendMessage


class PingCommand(Command):
    @text_triggered("Ping")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(SendMessage(text="Pong"))


if __name__ == "__main__":
    bot = SignalBot(
        Config(
            phone_number=os.environ["PHONE_NUMBER"],
            logging_level=logging.INFO,
        )
    )
    bot.register(PingCommand())  # Run the command for all contacts and groups
    bot.start()
