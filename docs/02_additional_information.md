---
title: Additional information
---

## Logging

The logger name for the library is `"signalbot"`.
It can be imported as `from signalbot import` [`LOGGER_NAME`][signalbot.LOGGER_NAME].

## Persistent storage

By default the `storage` attribute of the [signalbot.SignalBot][] class is in-memory.
Any changes are lost when the bot is stopped or reseted.
For persistent storage, see the [SQLiteStorage][signalbot.storage.SQLiteStorage] and
[RedisStorage][signalbot.storage.RedisStorage] API references and the
[storage configuration examples](./examples/02_bot_config_options.md#storage-type-options).

## Authentication

When running `signal-cli-rest-api` behind an auth-enabled proxy, specify an authentication method
using the `auth` config attribute — [`BasicAuthConfig`][signalbot.BasicAuthConfig] or
[`BearerAuthConfig`][signalbot.BearerAuthConfig].
See the [example](./examples/02_bot_config_options.md#authentication) for more details.
