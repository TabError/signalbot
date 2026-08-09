from examples.timestamps import local_datetime_str_from_timestamp
from signalbot import RemoteDeleteContext, RemoteDeleteHandler
from signalbot.messages import SendMessage


class DeletionNotifierHandler(RemoteDeleteHandler):
    def help_message(self) -> str:
        return "Remote delete received: 🗑️ Notifies when a message was deleted."

    async def handle_remote_delete(self, context: RemoteDeleteContext) -> None:
        deleted_at = local_datetime_str_from_timestamp(context.message.timestamp)
        message = f"You've deleted a message, which was sent at {deleted_at}."
        await context.send(SendMessage(text=message))
