---
title: Extending signalbot
---

Signalbot has two directions of message flow, and adding support for a new one touches a small,
predictable set of files:

- **Incoming** — signal-cli-rest-api pushes a message over the websocket, signalbot parses it into a
  typed object and dispatches it to a handler.
- **Outgoing** — a bot author calls a method that turns into an HTTP request against a
  [signal-cli-rest-api](https://bbernhard.github.io/signal-cli-rest-api/) endpoint.

Neither list below is exhaustive — some message types need extra plumbing (e.g.
[`GroupUpdate`][signalbot.groups.GroupUpdate] also touches the group registry in
[`src/signalbot/groups/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/groups)) —
so find the closest existing example and follow its shape.

## Adding a new incoming message type

1. **Get a message envelope.** Set a breakpoint in `_parse_main_messages`,
   `_parse_sync_messages`, or `_parse_data_message_variant` in
   [`src/signalbot/messages/parser.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/parser.py)
   — i.e. on the already-validated `message_envelope: MessageEnvelope` object.
   Trigger the message from another Signal client so that it is received by the bot.

2. **Identify the relevant envelope fields.** Check whether the fields exists and are already covered by the
   generated `_generated.receive` models
   ([`src/signalbot/_generated/receive/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_generated/receive)).
   Decide whether this is a genuinely new type or a variant of `data_message`/`sync_message` — compare
   with `_parse_data_message_variant` in
   [`parser.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/parser.py),
   which already branches on the `reaction`/`remote_delete`/group-update sub-fields of a data message.

   If a field is missing from the generated models, it
   is missing from upstream
   [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)'s own swagger schema — open
   an issue or a PR against that repo to add it, then pull the updated schema in and regenerate here
   with:
    ```bash
    uv run datamodel-codegen --profile signal-cli-rest-api
    ```
    Don't hand-add fields to the generated models directly.

3. **Write the parsed message class** with a `from_message_envelope(...)` classmethod, following an
   existing example —
   [`src/signalbot/messages/typing_message.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/typing_message.py)
   for a simple case, or
   [`src/signalbot/reactions/reaction.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/reactions/reaction.py)
   for one that reaches back into the envelope's nested data. Subclass
   [`BaseMessage`][signalbot.events.BaseMessage] or
   [`BaseMessageWithGroup`][signalbot.events.BaseMessageWithGroup] as appropriate.

4. **Wire it into the parser.** Add a branch in `_parse_main_messages` and/or `_parse_sync_messages` in
   [`parser.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/parser.py),
   and extend the [`ReceivedMessage`][signalbot.messages.ReceivedMessage] type
   alias.

5. **Write a [`Context`][signalbot.context.Context] class** in
   [`src/signalbot/context/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/context)
   (pattern:
   [`TypingContext`][signalbot.context.TypingContext] in
   [`typing_context.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/context/typing_context.py)),
   and a `Handler` ABC in
   [`src/signalbot/handlers.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/handlers.py)
   (pattern: [`TypingHandler`][signalbot.handlers.TypingHandler]) with one
   abstract `handle_xxx(self, context: ...)` method.

6. **Register the dispatch.** Add an entry to `_MESSAGE_DISPATCH` in
   [`src/signalbot/_pipeline.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_pipeline.py)
   mapping your new class to `(YourHandler, YourContext, "handle_xxx")`. This is the one place that
   ties parsing to dispatch — nothing reaches a handler without an entry here.

7. **(Optional) Write a trigger decorator** in
   [`handlers.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/handlers.py) if
   handlers for this type commonly filter on a field — follow
   [`reaction_triggered`][signalbot.handlers.reaction_triggered] as the smallest
   example: it checks `isinstance(context, YourContext)`, filters, and calls through.

8. **Write a test.** Follow
   [`tests/unit/messages/test_message.py`](https://github.com/signalbot-org/signalbot/blob/main/tests/unit/messages/test_message.py)'s
   pattern: build the raw envelope JSON inline (this repo doesn't use fixture files for envelopes), call
   [`parse(signal, raw_json_str)`][signalbot.messages.parse], and assert
   `isinstance(result, YourClass)` plus field values. Add dispatch coverage in
   [`tests/unit/test_pipeline.py`](https://github.com/signalbot-org/signalbot/blob/main/tests/unit/test_pipeline.py)
   if relevant.

9. **Write an example handler** under
   [`examples/handlers/`](https://github.com/signalbot-org/signalbot/tree/main/examples/handlers) or
   [`examples/commands/`](https://github.com/signalbot-org/signalbot/tree/main/examples/commands),
   following
   [`examples/commands/reaction.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/commands/reaction.py)
   (`@`[`text_triggered`][signalbot.handlers.text_triggered] +
   [`context.react(...)`][signalbot.context.DataMessageContext.react]) or
   [`examples/handlers/reaction.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/handlers/reaction.py)
   ([`ReactionHandler`][signalbot.handlers.ReactionHandler] +
   `@`[`reaction_triggered`][signalbot.handlers.reaction_triggered]) as templates,
   and register it in one of the example bots
   ([`examples/simple_bot.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/simple_bot.py) /
   [`examples/bot.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/bot.py)) with
   [`bot.register(YourHandler())`][signalbot.bot.SignalBot.register].

10. **Add a new page to the docs** under
   [`docs/examples/`](https://github.com/signalbot-org/signalbot/tree/main/docs/examples), under the
   section of the bot that you are editing.

## Adding a new outgoing action

1. **Find the endpoint** in the
   [signal-cli-rest-api Swagger docs](https://bbernhard.github.io/signal-cli-rest-api/) — note its
   HTTP verb, path, and request/response JSON shape.

2. **Find or generate the wire models** in
   [`src/signalbot/_generated/api/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_generated/api)
   (request) and
   [`src/signalbot/_generated/data/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_generated/data)
   (response). If the endpoint/shape is missing from
   [`src/signalbot/_generated/json_schema/signal-cli-rest-api.json`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_generated/json_schema/signal-cli-rest-api.json),
   it's missing from upstream
   [signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api)'s own swagger schema — open
   an issue or a PR against that repo first, then pull the updated schema in and re-run
   `uv run datamodel-codegen --profile signal-cli-rest-api` (see
   [`src/signalbot/_generated/README.md`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_generated/README.md)).
   Don't hand-add wire models.

3. **Add a client method** in the relevant
   [`src/signalbot/_client/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_client)
   file (or a new file for a new API section): add a URI method on the `*URIs` class (pattern:
   `MessagesURIs.remote_delete_uri()`) and a method on the `*Client` class that builds the payload with
   `model_dump_json(exclude_none=True, by_alias=True)`, calls
   `self._request(verb, uri, error_cls=..., payload=...)`, and parses the response (pattern:
   `MessagesClient.remote_delete` in
   [`src/signalbot/_client/messages.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_client/messages.py)).
   Define a dedicated `*Error(`[`SignalAPIError`][signalbot.SignalAPIError]`)` class alongside it.

4. **Expose it on [`SignalAPI`][signalbot.client.SignalAPI]** if it's a new
   section
   ([`src/signalbot/_client/signal_api.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_client/signal_api.py))
   — existing sections (`.messages`, `.reactions`, `.groups`, ...) already route to their client class.

5. **Add a method on the matching `*Actions` class** in
   [`src/signalbot/_actions/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_actions)
   (pattern:
   [`MessageActions.remote_delete`][signalbot._actions.MessageActions.remote_delete]
   in
   [`src/signalbot/_actions/messages.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_actions/messages.py)):
   resolve any recipient via `self._recipients.resolve(...)`, build the generated request model, call
   the client method, log via `self._logger.info(...)`, and return a friendly domain-level result if
   useful (e.g. [`SentMessage`][signalbot.messages.SentMessage]).

6. **Wire it up if it's a new Actions class** — instantiate and attach it to
   [`SignalBot`][signalbot.bot.SignalBot] in
   [`src/signalbot/_bot_init.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_bot_init.py)
   next to `self.messages`/`self.reactions`/etc.

7. **Add a [`Context`][signalbot.context.Context] convenience method** in
   [`src/signalbot/context/context.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/context/context.py)
   if handlers should be able to call it directly — follow how
   [`context.react(...)`][signalbot.context.DataMessageContext.react] /
   `context.send(...)` delegate to the Actions layer.

8. **Write a test** for the new `Actions` method (mock/stub [`SignalAPI`][signalbot.client.SignalAPI], assert the right client method
   and payload) — check
   [`tests/unit`](https://github.com/signalbot-org/signalbot/tree/main/tests/unit) for the existing
   pattern for `_actions/*` classes.

9. **Write an example** command/handler under
   [`examples/commands/`](https://github.com/signalbot-org/signalbot/tree/main/examples/commands) or
   [`examples/handlers/`](https://github.com/signalbot-org/signalbot/tree/main/examples/handlers) that
   calls the new action (pattern:
   [`examples/commands/reaction.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/commands/reaction.py)),
   registered in one of the example bots.

10. **Add a new page to the docs** under
   [`docs/examples/`](https://github.com/signalbot-org/signalbot/tree/main/docs/examples), under the
   section of the bot that you are editing.
