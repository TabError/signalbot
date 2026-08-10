from signalbot import CreatePoll, DataMessageContext, DataMessageHandler, text_triggered


class PollCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "poll: 🗳️ Create a poll."

    @text_triggered("poll")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.create_poll(
            CreatePoll(
                question="Cats or dogs?",
                answers=["Cats", "Dogs"],
                allow_multiple_selections=False,
            )
        )
