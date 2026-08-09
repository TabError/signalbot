from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.contacts import UpdateContact
from signalbot.messages import SendMessage

FIVE_MINUTES_IN_SECONDS = 5 * 60


class UpdateContactCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "expiration: ⏳ Toggle disappearing messages between off and 5 minutes."

    @text_triggered("expiration")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        if context.message.expires_in_seconds == FIVE_MINUTES_IN_SECONDS:
            new_expiration = 0
            status = "disabled"
        else:
            new_expiration = FIVE_MINUTES_IN_SECONDS
            status = "set to 5 minutes"

        await context.update_contact(
            UpdateContact(expiration_in_seconds=new_expiration)
        )
        await context.send(SendMessage(text=f"Disappearing messages {status}."))
