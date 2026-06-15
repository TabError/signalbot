from examples.commands.help import CommandWithHelpMessage
from signalbot import ContextReaction, reaction_triggered
from signalbot.api.requests import SendMessage


class ReactionCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "react with any emoji: 👍 Reaction decorator example."

    @reaction_triggered()
    async def handle_reaction(self, context: ContextReaction) -> None:
        reaction = context.message
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


class ThumbsUpCommand(CommandWithHelpMessage):
    def help_message(self) -> str:
        return "react with 👍 or ❤️: 🎯 Filtered reaction decorator example."

    @reaction_triggered("👍", "❤️")
    async def handle_reaction(self, context: ContextReaction) -> None:
        await context.send(SendMessage(text="Thanks for the love!"))
