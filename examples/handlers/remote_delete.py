from datetime import UTC, datetime

from signalbot import RemoteDeleteHandler
from signalbot.api.outgoing import SendMessage
from signalbot.context import RemoteDeleteContext


class DeletionNotifierHandler(RemoteDeleteHandler):
    def help_message(self) -> str:
        return "Remote delete received: 🗑️ Notifies when a message was deleted."

    async def handle_remote_delete(self, context: RemoteDeleteContext) -> None:
        deleted_at = datetime.fromtimestamp(context.message.timestamp / 1000, tz=UTC)
        message = f"You've deleted a message, which was sent at {deleted_at}."
        await context.send(SendMessage(text=message))
