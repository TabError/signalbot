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

## New incoming message

Every incoming type follows the same name chain from the wire to the handler. Match it when
adding a new one — `Xxx` (wrapped class) → `XxxHandler` → `XxxContext` → `handle_xxx`
(snake_case of `Xxx`):

| Generated class                             | Wrapped class                                                  | Handler ABC                                                          | Context class                                                      | Handler method        |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------------------------------- | ---------------------- |
| `DataMessage`                                        | [`DataMessage`][signalbot.messages.DataMessage]                  | [`DataMessageHandler`][signalbot.handlers.DataMessageHandler]           | [`DataMessageContext`][signalbot.context.DataMessageContext]           | `handle_data_message`  |
| `Reaction`                                                                | [`Reaction`][signalbot.reactions.Reaction]                       | [`ReactionHandler`][signalbot.handlers.ReactionHandler]                 | [`ReactionContext`][signalbot.context.ReactionContext]                 | `handle_reaction`      |
| `RemoteDelete`                                                            | [`RemoteDelete`][signalbot.messages.RemoteDelete]                | [`RemoteDeleteHandler`][signalbot.handlers.RemoteDeleteHandler]         | [`RemoteDeleteContext`][signalbot.context.RemoteDeleteContext]         | `handle_remote_delete` |
| `TypingMessage`                                                           | [`TypingMessage`][signalbot.messages.TypingMessage]              | [`TypingHandler`][signalbot.handlers.TypingHandler]                     | [`TypingContext`][signalbot.context.TypingContext]                     | `handle_typing`        |
| `GroupInfo`               | [`GroupUpdate`][signalbot.groups.GroupUpdate] | [`GroupUpdateHandler`][signalbot.handlers.GroupUpdateHandler] | [`GroupUpdateContext`][signalbot.context.GroupUpdateContext]           | `handle_group_update`  |

Steps:

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

4. **Wrap any nested `_generated` types your class exposes.** No `signalbot._generated` type may appear
   on the public API, directly or nested inside a field —
   [`tests/unit/test_public_api_surface.py`](https://github.com/signalbot-org/signalbot/blob/main/tests/unit/test_public_api_surface.py)
   enforces this and will fail your PR if you skip it. For each generated type your class reaches:

   - If nothing about it needs to change, still give it a thin domain subclass with a docstring —
     `class GroupInfo(GeneratedGroupInfo): """..."""` — even with zero added fields. The generated tree
     is produced from a bare JSON schema and carries no docstrings of its own, so this subclass is the
     only place that documentation exists, and it's what actually gets rendered under `docs/reference/`.
   - Add real fields or methods only when the domain type needs state or behavior the wire format
     doesn't have — pattern:
     [`Attachment.base64_content`][signalbot.attachments.Attachment] in
     [`src/signalbot/attachments/attachment.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/attachments/attachment.py).
   - If a container field then needs to point at one of these wrapped types instead of the generated
     type it replaces, that's a genuine override of the generated base class. pyright flags this as
     `reportIncompatibleVariableOverride` because narrowing a mutable attribute's type in a subclass is
     unsound in general — but it's sound here: every wrapped type is a strict superset of the generated
     type it replaces (same fields, same validation, plus extra), and pydantic validates the value
     against the narrower type on construction, so nothing bypasses it. Annotate the field with a bare
     `# pyright: ignore[reportIncompatibleVariableOverride]` — the rationale above is why.
     See `GroupEntry.permissions` in
     [`src/signalbot/groups/group_entry.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/groups/group_entry.py)
     or `Quote.attachments` in
     [`src/signalbot/messages/data_message_content.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/data_message_content.py)
     for the pattern.

5. **Wire it into the parser.** Add a branch in `_parse_main_messages` and/or `_parse_sync_messages` in
   [`parser.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/parser.py),
   and extend the [`ReceivedMessage`][signalbot.messages.ReceivedMessage] type
   alias.

6. **Write a [`Context`][signalbot.context.Context] class** in
   [`src/signalbot/context/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/context)
   (pattern:
   [`TypingContext`][signalbot.context.TypingContext] in
   [`typing_context.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/context/typing_context.py)),
   and a `Handler` ABC in
   [`src/signalbot/handlers.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/handlers.py)
   (pattern: [`TypingHandler`][signalbot.handlers.TypingHandler]) with one
   abstract `handle_xxx(self, context: ...)` method.

7. **Register the dispatch.** Add an entry to `_MESSAGE_DISPATCH` in
   [`src/signalbot/_pipeline.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_pipeline.py)
   mapping your new class to `(YourHandler, YourContext, "handle_xxx")`. This is the one place that
   ties parsing to dispatch — nothing reaches a handler without an entry here.

8. **(Optional) Write a trigger decorator** in
   [`handlers.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/handlers.py) if
   handlers for this type commonly filter on a field — follow
   [`reaction_triggered`][signalbot.handlers.reaction_triggered] as the smallest
   example: it checks `isinstance(context, YourContext)`, filters, and calls through.

9. **Write a test.** Follow
   [`tests/unit/messages/test_message.py`](https://github.com/signalbot-org/signalbot/blob/main/tests/unit/messages/test_message.py)'s
   pattern: build the raw envelope JSON inline (this repo doesn't use fixture files for envelopes), call
   [`parse(signal, raw_json_str)`][signalbot.messages.parse], and assert
   `isinstance(result, YourClass)` plus field values. Add dispatch coverage in
   [`tests/unit/test_pipeline.py`](https://github.com/signalbot-org/signalbot/blob/main/tests/unit/test_pipeline.py)
   if relevant.

10. **Write an example handler** under
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

11. **Add a new page to the docs** under
   [`docs/examples/`](https://github.com/signalbot-org/signalbot/tree/main/docs/examples), under the
   section of the bot that you are editing.

## New outgoing action

Every outgoing action follows the same name chain from the wire request to the bot author's
call site. Match it when adding a new one:

| Generated request              | Request class                                                                                  | Actions method                                | Context shortcut                                                                                                      |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `SendMessageV2`                                       | [`SendMessage`][signalbot.messages.SendMessage]                                                             | `bot.messages.send`                                | [`Context.send`][signalbot.context.Context.send]  |
| `RemoteDeleteRequest`                                 | built inline                                                     | `bot.messages.remote_delete`                       | [`DataMessageContext.remote_delete`][signalbot.context.DataMessageContext.remote_delete]                                   |
| `TypingIndicatorRequest`                              | built inline                                                                                             | `bot.messages.start_typing` / `.stop_typing`       | [`Context.start_typing`][signalbot.context.Context.start_typing] / [`Context.stop_typing`][signalbot.context.Context.stop_typing] |
| `SendReactionRequest`                                 | built inline                                                              | `bot.reactions.react`                              | [`DataMessageContext.react`][signalbot.context.DataMessageContext.react]                                                   |
| `Receipt`                                              | built inline                                                                  | `bot.receipts.send`                                | [`DataMessageContext.send_receipt`][signalbot.context.DataMessageContext.send_receipt]                                     |
| `UpdateGroupRequest`                                  | [`UpdateGroup`][signalbot.groups.UpdateGroup]                                                                | `bot.groups.actions.update`                        | [`Context.update_group`][signalbot.context.Context.update_group]                                                           |
| `CreatePollRequest`                                   | [`CreatePoll`][signalbot.polls.CreatePoll]  | `bot.polls.create`                                 | [`Context.create_poll`][signalbot.context.Context.create_poll]                                                             |
| `UpdateContactRequest`                                | [`UpdateContact`][signalbot.contacts.UpdateContact]                                                          | `bot.contacts.update`                              | [`Context.update_contact`][signalbot.context.Context.update_contact]                                                       |

Naming patterns to follow:

- **Generated request → request class drops the `Request` suffix.** `UpdateGroupRequest` →
  `UpdateGroup`, `CreatePollRequest` → `CreatePoll`, `UpdateContactRequest` → `UpdateContact`.
  `SendMessageV2`.
- **Context shortcut = the Actions method's bare verb, unless that verb is already taken.**
  [`Context`][signalbot.context.Context] flattens every domain's actions into one namespace, so
  a verb already used by another action gets qualified with its noun to disambiguate; otherwise
  it stays bare. `remote_delete`, `react`, `start_typing`/`stop_typing` all carry over unchanged
  from their `bot.<noun>.<verb>` call. `send` is already claimed by
  [`Context.send`][signalbot.context.Context.send] (messages), so receipts' `send` becomes
  [`send_receipt`][signalbot.context.DataMessageContext.send_receipt] instead. `update` is used
  by both groups and contacts, so neither gets the bare name — both keep the noun
  (`update_group`, `update_contact`).
- `GroupActions` attaches at `bot.groups.actions`, not directly on the bot — `bot.groups` is
  already the [`GroupRegistry`][signalbot.groups.GroupRegistry] cache, so `GroupActions` nests
  underneath it instead of taking a top-level `bot.<noun>` name of its own.

Steps:

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

3. **Write the domain-facing request model** that a bot author actually constructs, in the relevant
   top-level package (e.g. `src/signalbot/polls/`). Pick the shape based on whether every field is
   knowable at construction time:

   - **Straight subclass of the generated request** — `class X(GeneratedXRequest): """..."""` — when
     nothing needs to be filled in later. Narrowing a field to a wrapped type (as in the incoming-flow
     guidance above) is fine here too, same rule: additive narrowing is sound, mark it with
     `# pyright: ignore[reportIncompatibleVariableOverride]` and a reason.
   - **Standalone `BaseModel` with a `to_generated()` method** when a field the wire format requires
     won't be known until later — most commonly `recipient`/`group_id_or_name`, which a
     [`Context`][signalbot.context.Context] convenience method fills in from the received message.
     Follow [`SendMessage`][signalbot.messages.SendMessage] in
     [`send_message.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/messages/send_message.py),
     [`UpdateGroup`][signalbot.groups.UpdateGroup], or
     [`CreatePoll`][signalbot.polls.CreatePoll]: `to_generated()` raises a `ValueError` if the deferred
     field is still `None` when called.

4. **Add a client method** in the relevant
   [`src/signalbot/_client/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_client)
   file (or a new file for a new API section): add a URI method on the `*URIs` class (pattern:
   `MessagesURIs.remote_delete_uri()`) and a method on the `*Client` class, **typed to accept the
   generated request model**, that builds the
   payload with `model_dump_json(exclude_none=True, by_alias=True)`, calls
   `self._request(verb, uri, error_cls=..., payload=...)`, and parses the response (pattern:
   `MessagesClient.remote_delete` in
   [`src/signalbot/_client/messages.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_client/messages.py)).
   Define a dedicated `*Error(`[`SignalAPIError`][signalbot.SignalAPIError]`)` class alongside it.

5. **Expose it on [`SignalAPI`][signalbot.client.SignalAPI]** if it's a new
   section
   ([`src/signalbot/_client/signal_api.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_client/signal_api.py))
   — existing sections (`.messages`, `.reactions`, `.groups`, ...) already route to their client class.

6. **Add a method on the matching `*Actions` class** in
   [`src/signalbot/_actions/`](https://github.com/signalbot-org/signalbot/tree/main/src/signalbot/_actions)
   (pattern:
   [`MessageActions.remote_delete`][signalbot._actions.MessageActions.remote_delete]
   in
   [`src/signalbot/_actions/messages.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_actions/messages.py)):
   resolve any recipient via `self._recipients.resolve(...)`, convert to the wire request — call
   `.to_generated()` on the domain model if it has one (pattern:
   [`PollActions.create`][signalbot._actions.PollActions.create]), or construct the generated model
   directly for simple cases that never needed a domain wrapper (pattern:
   `MessageActions.remote_delete` building a `RemoteDeleteRequest` inline) — call the client method, log
   via `self._logger.info(...)`, and return a friendly domain-level result if useful (e.g.
   [`SentMessage`][signalbot.messages.SentMessage]).

7. **Wire it up if it's a new Actions class** — instantiate and attach it to
   [`SignalBot`][signalbot.bot.SignalBot] in
   [`src/signalbot/_bot_init.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/_bot_init.py)
   next to `self.messages`/`self.reactions`/etc.

8. **Add a [`Context`][signalbot.context.Context] convenience method** in
   [`src/signalbot/context/context.py`](https://github.com/signalbot-org/signalbot/blob/main/src/signalbot/context/context.py)
   if handlers should be able to call it directly — follow how
   [`context.react(...)`][signalbot.context.DataMessageContext.react] /
   `context.send(...)` delegate to the Actions layer. This is usually exactly where the deferred field
   from step 3 gets filled in — e.g. `create_poll_request.recipient = received_message.source_or_group_id()`.

9. **Write a test** for the new `Actions` method (mock/stub [`SignalAPI`][signalbot.client.SignalAPI], assert the right client method
   and payload) — check
   [`tests/unit`](https://github.com/signalbot-org/signalbot/tree/main/tests/unit) for the existing
   pattern for `_actions/*` classes.

10. **Write an example** command/handler under
   [`examples/commands/`](https://github.com/signalbot-org/signalbot/tree/main/examples/commands) or
   [`examples/handlers/`](https://github.com/signalbot-org/signalbot/tree/main/examples/handlers) that
   calls the new action (pattern:
   [`examples/commands/reaction.py`](https://github.com/signalbot-org/signalbot/blob/main/examples/commands/reaction.py)),
   registered in one of the example bots.

11. **Add a new page to the docs** under
   [`docs/examples/`](https://github.com/signalbot-org/signalbot/tree/main/docs/examples), under the
   section of the bot that you are editing.
