from anyio import Path

from signalbot import ContextDataMessage, DataMessageHandler, text_triggered
from signalbot.api.requests import LinkPreview, SendMessage


class LinkPreviewCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "link-preview: 🧽 Send a link preview."

    @text_triggered("link-preview")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.send(
            SendMessage(
                text="This is the link preview for https://www.youtube.com/watch?v=pU2SdH1HBuk",
                link_preview=LinkPreview(
                    description="A link preview description",
                    title="A link preview title",
                    url="https://www.youtube.com/watch?v=pU2SdH1HBuk",
                    thumbnail=Path(__file__).parent / "image.jpeg",
                ),
            )
        )
