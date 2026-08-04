import os

from examples.commands import (
    AttachmentCommand,
    CloseCommand,
    DeleteCommand,
    DeleteLocalAttachmentCommand,
    EditCommand,
    HelpCommand,
    LinkPreviewCommand,
    PingCommand,
    ReactCommand,
    RegexTriggeredCommand,
    ReplyCommand,
    StylesCommand,
    TriggeredCommand,
    TypingCommand,
)
from examples.handlers import (
    DeletionNotifierHandler,
    FilteredReactionHandler,
    ReactionDetailsHandler,
    WelcomeHandler,
)
from signalbot import Config, SignalBot


def main() -> None:
    phone_number = os.environ["PHONE_NUMBER"]

    bot = SignalBot(Config(phone_number=phone_number))

    # Replace the recipient with your own phone number or group ID to
    # receive the welcome message.
    bot.register(WelcomeHandler(recipient=None))

    # By default the handlers are enabled for all contacts and all groups
    bot.register(HelpCommand())
    bot.register(PingCommand())
    bot.register(ReplyCommand())
    bot.register(RegexTriggeredCommand())
    bot.register(ReactCommand())
    bot.register(EditCommand())
    bot.register(DeleteCommand())
    bot.register(DeleteLocalAttachmentCommand())
    bot.register(StylesCommand())
    bot.register(LinkPreviewCommand())
    bot.register(CloseCommand())
    bot.register(ReactionDetailsHandler())
    bot.register(FilteredReactionHandler())
    bot.register(DeletionNotifierHandler())

    # The handler will only trigger for group messages
    bot.register(AttachmentCommand(), contacts=False)

    # The handler will only trigger the group named "My Group"
    bot.register(TypingCommand(), groups=["My Group"])

    # The handler will only trigger for the contact "+490123456789"
    bot.register(TriggeredCommand(), contacts=["+490123456789"])

    bot.start()


if __name__ == "__main__":
    main()
