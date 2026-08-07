from collections.abc import AsyncIterator

import pytest_asyncio

from signalbot import SignalAPI, SignalBot

SIGNAL_SERVICE = "127.0.0.1:8080"
PHONE_NUMBER = "+49123456789"
GROUP_ID = "group.OyZzqio1xDmYiLsQ1VsqRcUFOU4tK2TcECmYt2KeozHJwglMBHAPS7jlkrm="
GROUP_INTERNAL_ID = "Mg8LQTdaZJs8+LJCrtQgblqHx+xI2dX9JJ8hVA2kqt8="


@pytest_asyncio.fixture
async def signal_api() -> AsyncIterator[SignalAPI]:
    api = SignalAPI(SIGNAL_SERVICE, PHONE_NUMBER)
    yield api
    await api.close()


@pytest_asyncio.fixture
async def signal_bot() -> AsyncIterator[SignalBot]:
    config = {
        "signal_service": SIGNAL_SERVICE,
        "phone_number": PHONE_NUMBER,
        "storage": {"type": "in-memory"},
    }
    bot = SignalBot(config)
    yield bot
    await bot.close()
