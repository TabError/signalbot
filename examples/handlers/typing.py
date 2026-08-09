from signalbot import TypingContext, TypingHandler
from signalbot.messages import SendMessage, TypingAction


class TypingIndicatorHandler(TypingHandler):
    def help_message(self) -> str:
        return "Typing indicator received: ⌨️ Notifies when someone starts typing."

    async def handle_typing(self, context: TypingContext) -> None:
        if context.message.action != TypingAction.STARTED:
            return

        await context.send(
            SendMessage(text=f"{context.message.source_name} is typing…")
        )
