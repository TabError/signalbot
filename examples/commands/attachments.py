import base64

from anyio import Path

from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextDataMessage, text_triggered
from signalbot.api.requests import SendMessage


class AttachmentCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "friday: 🦀 Send an image."

    @text_triggered("friday")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        image_path = Path(__file__).parent / "image.jpeg"
        async with await image_path.open(mode="rb") as f:
            image = str(base64.b64encode(await f.read()), encoding="utf-8")

        await context.send(
            SendMessage(
                text="https://www.youtube.com/watch?v=pU2SdH1HBuk",
                base64_attachments=[image],
            )
        )
