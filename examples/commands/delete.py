import asyncio
from datetime import datetime

from examples.commands.help import CommandWithHelpMessage
from signalbot import triggered
from signalbot.api.requests import SendMessage
from signalbot.context import ContextDataMessage, ContextRemoteDelete


class DeleteCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete: 🗑️ Delete a message."

    @triggered("delete")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        sent_message = await context.send(
            SendMessage(text="This message will be deleted in two seconds.")
        )
        await asyncio.sleep(2)
        await context.remote_delete(timestamp=sent_message.timestamp)

    async def handle_remote_delete(self, context: ContextRemoteDelete) -> None:
        deleted_at = datetime.fromtimestamp(  # noqa: DTZ006
            context.message.timestamp / 1000
        )
        message = f"You've deleted a message, which was sent at {deleted_at}."
        await context.send(SendMessage(text=message))


class DeleteLocalAttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete_attachment: 🗑️ Delete the local copy of an attachment."

    @triggered("delete_attachment")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        attachments = context.message.attachments
        if attachments is None or len(attachments) == 0:
            await context.send(SendMessage(text="Please send an attachment to delete."))
            return

        for attachment in attachments:
            attachment_path = await attachment.local_path()

            if attachment_path is None:
                continue

            if attachment_path.exists():
                print(f"Received file {attachment_path}")  # noqa: T201

            await context.bot.delete_attachment(attachment)

            if not attachment_path.exists():
                print(f"Deleted file {attachment_path}")  # noqa: T201
