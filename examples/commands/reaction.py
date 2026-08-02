from signalbot import (
    DataMessageHandler,
    ReactionContext,
    ReactionHandler,
    reaction_triggered,
    text_triggered,
)
from signalbot.api.outgoing import SendMessage
from signalbot.context.data_message_context import DataMessageContext


class ReactCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "send-reaction: 🎉 Send a reaction to a message."

    @text_triggered("send-reaction")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.react("🎉")


class ReactionCommand(ReactionHandler):
    def help_message(self) -> str:
        return (
            "Reaction received (any emoji except 👍/❤️): 🎉 Replies with details "
            "about the reaction."
        )

    async def handle_reaction(self, context: ReactionContext) -> None:
        reaction = context.message

        if reaction.emoji in ["👍", "❤️"]:
            return  # ignore thumbs up and heart reactions, handled by ThumbsUpCommand

        if reaction.is_remove:
            await context.send(
                SendMessage(text=f"You removed your {reaction.emoji} reaction")
            )
            return

        await context.send(
            SendMessage(
                text=(
                    f"{reaction.emoji} from {context.message.source} "
                    f"on message at {reaction.timestamp}"
                )
            )
        )


class ThumbsUpCommand(ReactionHandler):
    def help_message(self) -> str:
        return (
            "Reaction received (👍 or ❤️): 🎯 Filtered reaction received "
            "decorator example."
        )

    @reaction_triggered("👍", "❤️")
    async def handle_reaction(self, context: ReactionContext) -> None:
        reaction = context.message
        if reaction.is_remove:
            await context.send(
                SendMessage(text=f"ThumbsUpCommand: {reaction.emoji} removed")
            )
            return

        await context.send(
            SendMessage(text=f"ThumbsUpCommand: {reaction.emoji} received")
        )
