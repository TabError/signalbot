import logging
import os

import typer

from signalbot import SignalBot, enable_console_logging
from signalbot.api.requests import SendMessage


async def send(bot: SignalBot, recipient: str, text: str) -> None:
    # Wait until the bot is fully initialized before sending a message
    await bot.init_task

    await bot.send(SendMessage(recipient=recipient, text=text))


def main(
    recipient: str = os.environ["PHONE_NUMBER"],
    text: str = "Hello from SignalBot!",
) -> None:
    enable_console_logging(logging.INFO)

    config = {
        "signal_service": os.environ["SIGNAL_SERVICE"],
        "phone_number": os.environ["PHONE_NUMBER"],
    }
    bot = SignalBot(config)

    bot.scheduler.add_job(send, args=[bot, recipient, text])
    bot.scheduler.add_job(
        send, args=[bot, recipient, "Ping"], trigger="interval", seconds=5
    )
    bot.start()


if __name__ == "__main__":
    typer.run(main)
