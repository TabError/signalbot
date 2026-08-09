from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.contacts import UpdateContact
from signalbot.messages import SendMessage


class UpdateContactCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "nickname: 📇 Set the bot's local nickname for you as a contact."

    @text_triggered("nickname")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.update_contact(UpdateContact(name="Signalbot friend"))
        await context.send(SendMessage(text="Updated your contact nickname."))
