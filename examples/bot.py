import os

from examples.commands import (
    AttachmentCommand,
    DeleteCommand,
    DeleteLocalAttachmentCommand,
    EditCommand,
    HelpCommand,
    LinkPreviewCommand,
    PingCommand,
    ReactCommand,
    ReactionCommand,
    ReceiveDeleteCommand,
    RegexTriggeredCommand,
    ReplyCommand,
    StylesCommand,
    ThumbsUpCommand,
    TriggeredCommand,
    TypingCommand,
)
from signalbot import Config, SignalBot


def main() -> None:
    phone_number = os.environ["PHONE_NUMBER"]

    bot = SignalBot(Config(phone_number=phone_number))

    bot.register(HelpCommand())

    # enable a chat command for all contacts and all groups
    bot.register(PingCommand())
    bot.register(ReplyCommand())

    # enable a chat command only for groups
    bot.register(AttachmentCommand(), contacts=False, groups=True)

    # enable a chat command for one specific group with the name "My Group"
    bot.register(TypingCommand(), groups=["My Group"])

    # chat command is enabled for all groups and one specific contact
    bot.register(TriggeredCommand(), contacts=["+490123456789"], groups=True)

    bot.register(RegexTriggeredCommand())

    bot.register(ReactionCommand())
    bot.register(ThumbsUpCommand())
    bot.register(ReactCommand())

    bot.register(EditCommand())
    bot.register(DeleteCommand())
    bot.register(ReceiveDeleteCommand())
    bot.register(DeleteLocalAttachmentCommand())
    bot.register(StylesCommand())
    bot.register(LinkPreviewCommand())
    bot.start()


if __name__ == "__main__":
    main()
