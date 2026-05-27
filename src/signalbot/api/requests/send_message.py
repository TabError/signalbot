from __future__ import annotations

from signalbot.api.generated import SendMessageV2


class SendMessage(SendMessageV2):
    pass


class SentMessage(SendMessage):
    timestamp: int

    @classmethod
    def from_send_message(
        cls, send_message: SendMessage, timestamp: int
    ) -> SentMessage:
        return cls.model_construct(**send_message.model_dump(), timestamp=timestamp)
