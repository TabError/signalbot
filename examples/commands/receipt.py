from signalbot import DataMessageContext, DataMessageHandler, text_triggered
from signalbot.receipts import ReceiptType


class ReceiptCommand(DataMessageHandler):
    def help_message(self) -> str:
        return "receipt: 👀 Send a read receipt back for this message."

    @text_triggered("receipt")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send_receipt(ReceiptType.READ)
