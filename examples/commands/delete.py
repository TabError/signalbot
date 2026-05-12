import asyncio
from datetime import datetime

from anyio import Path

from examples.commands.help import CommandWithHelpMessage
from signalbot import triggered
from signalbot.context import ContextDataMessage, ContextRemoteDelete


class DeleteCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete: 🗑️ Delete a message."

    @triggered("delete")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        timestamp = await context.send("This message will be deleted in two seconds.")
        await asyncio.sleep(2)
        await context.remote_delete(timestamp=timestamp)


class DeleteLocalAttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "delete_attachment: 🗑️ Delete the local copy of an attachment."

    @triggered("delete_attachment")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        local_filenames = [attachment.id for attachment in context.message.attachments]
        if local_filenames is None or len(local_filenames) == 0:
            await context.send("Please send an attachment to delete.")

        for attachment_filename in local_filenames:
            attachment_path: Path = (
                await Path.home()
                / ".local/share/signal-api/attachments"
                / attachment_filename
            )

            if await attachment_path.exists():
                print(f"Received file {attachment_path}")  # noqa: T201

            await context.bot.delete_attachment(attachment_filename)

            if not await attachment_path.exists():
                print(f"Deleted file {attachment_path}")  # noqa: T201


class ReceiveDeleteCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "N/A: 🗑️ Receive a message has been deleted notification."

    async def handle_remote_delete(self, context: ContextRemoteDelete) -> None:
        deleted_at = datetime.fromtimestamp(  # noqa: DTZ006
            context.message.timestamp / 1000
        )
        message = f"You've deleted a message, which was sent at {deleted_at}."
        await context.send(message)
