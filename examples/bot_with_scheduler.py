import os

import typer

from signalbot import SendMessage, SignalBot


async def ping(bot: SignalBot, recipient: str) -> None:
    # Scheduled jobs can run before the bot has finished connecting, so wait for it.
    await bot.wait_until_ready()

    await bot.messages.send(SendMessage(text="Ping"), recipient)


def main(recipient: str = os.environ["PHONE_NUMBER"]) -> None:
    config = {"phone_number": os.environ["PHONE_NUMBER"]}
    bot = SignalBot(config)

    bot.scheduler.add_job(ping, args=[bot, recipient], trigger="interval", seconds=5)
    bot.start()


if __name__ == "__main__":
    typer.run(main)
