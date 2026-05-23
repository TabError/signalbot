from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from signalbot.api.receive_messages import ReceivedMessageType
    from signalbot.api.requests import SendMessage, SentMessage
    from signalbot.bot import SignalBot


class Context:
    """
    Context is a helper class that provides methods to reply, edit, react, etc. to a
    message. This is useful to avoid having to pass the recipient and other arguments to
    the bot's methods manually.
    """

    def __init__(self, bot: SignalBot, message: ReceivedMessageType) -> None:
        self.bot = bot
        self.message = message

    async def send(
        self,
        data_message: SendMessage,
    ) -> SentMessage:
        """Same as
         [signalbot.SignalBot.send()](bot.md#signalbot.SignalBot.send)
        but with the recipient set to the message's recipient."""
        data_message.recipients = [self.message.source_or_group_uuid()]
        return await self.bot.send(data_message)

    async def receipt(self, receipt_type: Literal["read", "viewed"]) -> None:
        """Same as
         [signalbot.SignalBot.receipt()](bot.md#signalbot.SignalBot.receipt)
        but with the recipient set to the message's recipient."""
        await self.bot.receipt(self.message, receipt_type)

    async def start_typing(self) -> None:
        """Same as
        [signalbot.SignalBot.start_typing()](bot.md#signalbot.SignalBot.start_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.start_typing(self.message.source_or_group_uuid())

    async def stop_typing(self) -> None:
        """Same as
        [signalbot.SignalBot.stop_typing()](bot.md#signalbot.SignalBot.stop_typing)
         but with the recipient set to the message's recipient."""
        await self.bot.stop_typing(self.message.source_or_group_uuid())
