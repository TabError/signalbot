from anyio import Path

from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.api.outgoing import SendMessage


class AttachmentCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "friday: 🦀 Send an image."

    @text_triggered("friday")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(
            SendMessage(
                text="https://www.youtube.com/watch?v=pU2SdH1HBuk",
                attachments=[Path(__file__).parent / "image.jpeg"],
            )
        )
