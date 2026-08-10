from signalbot import SendMessage, TypingAction, TypingContext, TypingHandler


class TypingIndicatorHandler(TypingHandler):
    """Notifies when someone starts typing. Starts disabled; toggle it with the
    `enable_typing_indicator` / `disable_typing_indicator` commands in
    `examples/commands/typing.py`.
    """

    def __init__(self) -> None:
        self.enabled = False

    def help_message(self) -> str:
        return "Typing indicator received: ⌨️ Notifies when someone starts typing."

    async def handle_typing(self, context: TypingContext) -> None:
        if not self.enabled:
            return

        if context.message.action != TypingAction.STARTED:
            return

        await context.send(
            SendMessage(text=f"{context.message.source_name} is typing…")
        )
