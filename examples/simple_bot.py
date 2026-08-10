import logging
import os

from signalbot import (
    Config,
    DataMessageContext,
    DataMessageHandler,
    SendMessage,
    SignalBot,
    text_triggered,
)


class PingCommand(DataMessageHandler):
    @text_triggered("Ping")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="Pong"))


if __name__ == "__main__":
    bot = SignalBot(
        Config(
            phone_number=os.environ["PHONE_NUMBER"],
            logging_level=logging.INFO,
        )
    )
    bot.register(PingCommand())
    bot.start()
