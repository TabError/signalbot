from examples.commands.help import HasHelpMessage
from signalbot import (
    Command,
    ContextReaction,
    ReactionHandler,
    reaction_triggered,
    text_triggered,
)
from signalbot.api.requests import SendMessage
from signalbot.context.context_data_message import ContextDataMessage


class ReactCommand(HasHelpMessage, Command):
    def help_message(self) -> str:
        return "send-reaction: 🎉 Send a reaction to a message."

    @text_triggered("send-reaction")
    async def handle_data_message(self, context: ContextDataMessage) -> None:
        await context.react("🎉")


class ReactionCommand(HasHelpMessage, ReactionHandler):
    def help_message(self) -> str:
        return "react with any emoji: 👍 Reaction received decorator example."

    async def handle_reaction(self, context: ContextReaction) -> None:
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


class ThumbsUpCommand(HasHelpMessage, ReactionHandler):
    def help_message(self) -> str:
        return "react with 👍 or ❤️: 🎯 Filtered reaction received decorator example."

    @reaction_triggered("👍", "❤️")
    async def handle_reaction(self, context: ContextReaction) -> None:
        reaction = context.message
        if reaction.is_remove:
            await context.send(
                SendMessage(text=f"ThumbsUpCommand: {reaction.emoji} removed")
            )
            return

        await context.send(
            SendMessage(text=f"ThumbsUpCommand: {reaction.emoji} received")
        )
