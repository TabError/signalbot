from examples.timestamps import local_datetime_str_from_timestamp
from signalbot import ReactionContext, ReactionHandler, SendMessage, reaction_triggered


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

        message_sent_at = local_datetime_str_from_timestamp(reaction.timestamp)
        await context.send(
            SendMessage(
                text=(
                    f"{context.message.source_name} reacted with {reaction.emoji} "
                    f"on a message that was sent by {reaction.target_author} at "
                    f"{message_sent_at}"
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
