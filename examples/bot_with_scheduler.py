import os

import typer

from signalbot import ContextReady, ReadyHandler, SignalBot
from signalbot.api.requests import SendMessage


class Welcome(ReadyHandler):
    def __init__(self, recipient: str, text: str) -> None:
        super().__init__()
        self.recipient = recipient
        self.text = text

    async def handle_ready(self, context: ContextReady) -> None:
        await context.bot.send(SendMessage(recipient=self.recipient, text=self.text))


async def ping(bot: SignalBot, recipient: str) -> None:
    # Scheduled jobs can run before the bot has finished connecting, so wait for it.
    await bot.wait_until_ready()

    await bot.send(SendMessage(recipient=recipient, text="Ping"))


def main(
    recipient: str = os.environ["PHONE_NUMBER"],
    text: str = "Hello from SignalBot!",
) -> None:
    config = {"phone_number": os.environ["PHONE_NUMBER"]}
    bot = SignalBot(config)

    bot.register(Welcome(recipient, text))
    bot.scheduler.add_job(ping, args=[bot, recipient], trigger="interval", seconds=5)
    bot.start()


if __name__ == "__main__":
    typer.run(main)
