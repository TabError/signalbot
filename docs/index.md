# Signalbot

Python package to build your own Signal bots.

The package provides methods to easily listen for incoming messages and responding or reacting on them.
It also provides a class to develop new commands, which then can be registered within the bot.

Here is minimal example of what that looks like:
```python
--8<-- "examples/simple_bot.py"
```

To set it up follow the steps in the [getting started page](getting_started.md).

### Methods overview

The bot can do a lot more, here is a quick overview of the most common methods:

- `bot.register(command, contacts=True, groups=True)`: Register a new command, listen in all contacts and groups, same as `bot.register(command)`
- `bot.register(command, contacts=False, groups=["Hello World"])`: Only listen in the "Hello World" group
- `bot.register(command, contacts=["+49123456789"], groups=False)`: Only respond to one contact
- `bot.start()`: Start the bot
- `bot.messages.send(recipient, text)`: Send a new message
- `bot.messages.start_typing(recipient)`: Start typing
- `bot.messages.stop_typing(recipient)`: Stop typing
- `bot.messages.edit(new_message, original_message)`: Edit a previously sent message
- `bot.messages.remote_delete(sent_message)`: Delete a previously sent message
- `bot.reactions.react(message, emoji)`: React to a message
- `bot.receipts.send(message, receipt_type)`: Mark a message as read
- `bot.group_actions.update(update_group_request)`: Change group settings
- `bot.attachments.delete(attachment)`: Delete the local copy of an attachment
- `bot.scheduler`: Schedule tasks, see the [scheduler examples](examples/bot_with_scheduler.md).

Each of these is grouped under a namespace matching the underlying `signal-cli-rest-api` tag it belongs to (`messages`, `reactions`, `receipts`, `groups`, `contacts`, `attachments`, `polls`, `general`), mirroring how [`SignalAPI`](reference/bot.md) is organized. `groups` is the one exception: `bot.groups` is a read-only cache of the groups the bot is a member of, while updates go through `bot.group_actions`.

## Real world bot examples

There are many real world examples of bot implementations using this library.
Check the whole list at https://github.com/signalbot-org/signalbot/network/dependents
