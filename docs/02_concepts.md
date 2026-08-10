---
title: How it works
---

Signalbot moves messages in two directions: **incoming** messages arrive over a websocket and are
routed to your code, **outgoing** messages are sent by your code through an HTTP API. This page
shows how the pieces fit together — read [Extending signalbot](06_extending.md) once you're ready
to add a new message type or action yourself.

## Architecture

### Incoming

```mermaid
%%{init: {"flowchart": {"useMaxWidth": false}}}%%
flowchart LR
    WS(["signal-cli-rest-api<br/>websocket"]) --> Parse["parser.parse()"]
    Parse --> Queue[["dispatch queue"]]
    Queue --> Dispatch["_MESSAGE_DISPATCH"]
    Dispatch --> Handler["Handler.handle_xxx()"]
    Handler --> Context(["Context"])
```

### Outgoing

```mermaid
%%{init: {"flowchart": {"useMaxWidth": false}}}%%
flowchart LR
    Call(["context.send(), .react(), ..."]) --> Actions["*Actions"]
    Actions --> Client["SignalAPI client"]
    Client --> HTTP(["signal-cli-rest-api<br/>HTTP endpoint"])
```

- **Incoming**: `MessagePipeline._produce` reads the websocket, `parse()` turns the raw JSON into a
  typed [`ReceivedMessage`][signalbot.messages.ReceivedMessage], and `_MESSAGE_DISPATCH` decides
  which [`Handler`][signalbot.handlers] ABC and [`Context`][signalbot.context.Context] subclass
  apply before your `handle_xxx` method runs.
- **Outgoing**: calling a method on `context` (or directly on `bot.messages` / `bot.reactions` /
  ...) resolves the recipient, builds a wire request, and sends it through
  [`SignalAPI`][signalbot.client.SignalAPI] to `signal-cli-rest-api`.

## Registration

Before any of this runs, handlers need to be registered with the bot — typically once at startup,
e.g. `bot.register(PingHandler())`. There are two ways to look at what that does; see which one
clicks and drop the other.

### Option A — registration as its own diagram

```mermaid
%%{init: {"flowchart": {"useMaxWidth": false}}}%%
flowchart TD
    Register["bot.register(handler, contacts=..., groups=..., f=...)"] --> Pending[["_handlers_to_register"]]
    Start(["bot.start()"]) --> Resolve["resolve_handlers()<br/>(resolves group names → ids)"]
    Pending --> Resolve
    Resolve --> Handlers[["pipeline.handlers"]]

    Handlers -. "on every incoming message" .-> Filter{"contact / group / f(message)<br/>filters match?"}
    Filter -- yes --> Lookup["_MESSAGE_DISPATCH[type(message)]<br/>→ (HandlerABC, ContextClass, method name)"]
    Lookup --> IsInstance{"isinstance(handler, HandlerABC)?"}
    IsInstance -- yes --> Invoke["await handler.handle_xxx(ContextClass(bot, message))"]
```

`bot.register()` just stores the handler and its filters; nothing is invoked yet. At startup,
`resolve_handlers()` turns group names into group ids. From then on, every incoming message is
checked against each registered handler's filters, matched against `_MESSAGE_DISPATCH` by message
type, and — only if the handler is actually an instance of the expected `Handler` ABC (e.g. a
`ReactionHandler` is skipped for a `DataMessage`) — invoked with a fresh `Context`.

### Option B — registration folded into the message lifecycle

Instead of a separate diagram, registration can be shown as the opening step of one concrete
message's journey — see steps 1-2 below.

## Following one message end to end

Take a bot with a single handler:

```python
class PingHandler(DataMessageHandler):
    @text_triggered("!ping")
    async def handle_data_message(self, context: DataMessageContext) -> None:
        await context.send(SendMessage(text="pong"))
```

```mermaid
%%{init: {"sequence": {"useMaxWidth": false}}}%%
sequenceDiagram
    participant Author as Bot author code
    participant Bot as SignalBot
    participant API as signal-cli-rest-api
    participant Pipeline as MessagePipeline
    participant Handler as PingHandler
    participant Context as DataMessageContext

    Author->>Bot: bot.register(PingHandler())
    Bot->>Pipeline: store handler + filters
    Note over Pipeline: bot.start() → resolve_handlers()

    API-->>Pipeline: websocket push: raw "!ping" envelope
    Pipeline->>Pipeline: parse() → DataMessage
    Pipeline->>Pipeline: filters match? _MESSAGE_DISPATCH lookup
    Pipeline->>Handler: handle_data_message(DataMessageContext(bot, message))
    Note over Handler: @text_triggered("!ping") matches
    Handler->>Context: context.send(SendMessage(text="pong"))
    Context->>Bot: bot.messages.send(message, recipient)
    Bot-->>API: HTTP POST /v2/send
    API-->>Author: "pong" delivered to the chat
```

Every incoming message type has its own `Handler`/`Context` pair and dispatch entry (see the table
in [Extending signalbot](06_extending.md#new-incoming-message)) — this walk-through uses
`DataMessage` because it's the most common case, but reactions, typing indicators, remote deletes,
and group updates all follow the same shape.
