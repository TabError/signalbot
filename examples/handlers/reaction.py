from signalbot import ReactionContext, ReactionHandler, reaction_triggered
from signalbot.api.outgoing import SendMessage


class ReactionDetailsHandler(ReactionHandler):
    def help_message(self) -> str:
        return (
            "Reaction received or removed (any emoji except 👍/❤️): "
            "🎉 Replies with details about the reaction."
        )

    async def handle_reaction(self, context: ReactionContext) -> None:
        reaction = context.message

        if reaction.emoji in ["👍", "❤️"]:
            # ignore thumbs up/heart, handled by FilteredReactionHandler
            return

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


class FilteredReactionHandler(ReactionHandler):
    def help_message(self) -> str:
        return (
            "Reaction received or removed (👍 or ❤️): 🎯 Filtered reaction received "
            "decorator example."
        )

    @reaction_triggered("👍", "❤️")
    async def handle_reaction(self, context: ReactionContext) -> None:
        reaction = context.message
        if reaction.is_remove:
            await context.send(
                SendMessage(text=f"FilteredReactionHandler: {reaction.emoji} removed")
            )
            return

        await context.send(
            SendMessage(text=f"FilteredReactionHandler: {reaction.emoji} received")
        )
