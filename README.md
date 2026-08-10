# Signal Bot Framework

[![PyPI Downloads](https://img.shields.io/pypi/dm/signalbot?label=Downloads
)](https://pypistats.org/packages/signalbot)
[![Version](https://img.shields.io/pypi/v/signalbot?logo=python&logoColor=white&label=PyPI)](https://pypi.python.org/pypi/signalbot)
[![License](https://img.shields.io/pypi/l/signalbot.svg?label=License)](https://pypi.python.org/pypi/signalbot)
[![CI](https://github.com/signalbot-org/signalbot/actions/workflows/ci.yaml/badge.svg)](https://github.com/signalbot-org/signalbot/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/signalbot-org/signalbot/graph/badge.svg?token=N3ZA5MTU2P)](https://codecov.io/gh/signalbot-org/signalbot)

Python package to build your own Signal bots.

## Installation

See the [getting started](https://signalbot-org.github.io/signalbot/latest/01_getting_started) section in the documentation.

## Minimal bot

This is what a minimal bot using signalbot looks like:

```python
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
```

## Help

See the [documentation](https://signalbot-org.github.io/signalbot/) for more details.
