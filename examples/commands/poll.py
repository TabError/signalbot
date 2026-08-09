from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.polls import CreatePoll


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
