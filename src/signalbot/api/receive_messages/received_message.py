from __future__ import annotations

from pydantic import BaseModel

from signalbot.api.generated import MessageEnvelope


class ReceivedMessage(BaseModel):
    envelope: MessageEnvelope
    account: str
