---
title: Overview
---

# Signalbot

Python package to build your own Signal bots.

The package provides methods to easily listen for incoming messages and responding or reacting on them.
It also provides a class to develop new handlers, which then can be registered within the bot.

Here is minimal example of what that looks like:
```python
--8<-- "examples/simple_bot.py"
```

To set it up follow the steps in the [getting started page](01_getting_started.md).

### Methods overview

The bot can do a lot more, here is a quick overview of the most common methods:

- [bot.register(handler)][signalbot.bot.SignalBot.register]: Register a new handler
- `bot.start()`: Start the bot
- `bot.messages.send(SendMessage(recipient=..., text=...))`: Send a new message
- `bot.messages.start_typing(recipient)`: Start typing
- `bot.messages.stop_typing(recipient)`: Stop typing
- `bot.messages.edit(new_message, original_message)`: Edit a previously sent message
- `bot.messages.remote_delete(sent_message)`: Delete a previously sent message
- `bot.reactions.react(message, emoji)`: React to a message
- `bot.receipts.send(message, receipt_type)`: Mark a message as read
- `bot.group_actions.update(update_group_request)`: Change group settings
- `bot.attachments.delete(attachment)`: Delete the local copy of an attachment
- `bot.scheduler`: Schedule tasks, see the [scheduler examples](examples/03_bot_with_scheduler.md).

## Real world bot examples

There are many real world examples of bot implementations using this library.
Check the whole list at https://github.com/signalbot-org/signalbot/network/dependents
