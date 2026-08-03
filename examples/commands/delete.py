import asyncio

from signalbot import DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage
from signalbot.context import DataMessageContext


class DeleteCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "delete: 🗑️ Delete a message."

    @text_triggered("delete")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        sent_message = await context.send(
            SendMessage(text="This message will be deleted in two seconds.")
        )
        await asyncio.sleep(2)
        await context.remote_delete(timestamp=sent_message.timestamp)


class DeleteLocalAttachmentCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "delete-attachment: 🗑️ Delete the local copy of an attachment."

    @text_triggered("delete-attachment")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        attachments = context.message.attachments
        if attachments is None or len(attachments) == 0:
            await context.send(SendMessage(text="Please send an attachment to delete."))
            return

        for attachment in attachments:
            attachment_path = await attachment.local_path()

            if attachment_path is None:
                continue

            if await attachment_path.exists():
                await context.send(SendMessage(text=f"Received file {attachment_path}"))

            await context.bot.delete_attachment(attachment)

            if not await attachment_path.exists():
                await context.send(SendMessage(text=f"Deleted file {attachment_path}"))
