This bot showcases how to use most of the features in the library.
Check the [commands section](#commands) and [handlers section](#handlers) to see the implementation of each command and handler.
The code shown here can be found the [examples folder](https://github.com/signalbot-org/signalbot/tree/main/examples).

This bot uses additional libraries. If you cloned the [repository](https://github.com/signalbot-org/signalbot), install them with:
```bash
uv sync --group examples
```

<br>Bot code:

``` python
--8<-- "examples/bot.py"
```

### Commands

<details><summary>AttachmentCommand</summary>
``` python
--8<-- "examples/commands/attachments.py"
```
</details>


<details><summary>CloseCommand</summary>
``` python
--8<-- "examples/commands/close.py"
```
</details>


<details><summary>DeleteCommand & DeleteLocalAttachmentCommand</summary>
``` python
--8<-- "examples/commands/delete.py"
```
</details>


<details><summary>EditCommand</summary>
``` python
--8<-- "examples/commands/edit.py"
```
</details>


<details><summary>HelpCommand</summary>
``` python
--8<-- "examples/commands/help.py"
```
</details>


<details><summary>LinkPreviewCommand</summary>
``` python
--8<-- "examples/commands/link_preview.py"
```
</details>


<details><summary>TriggeredCommand</summary>
``` python
--8<-- "examples/commands/multiple_triggered.py"
```
</details>


<details><summary>PingCommand</summary>
``` python
--8<-- "examples/commands/ping.py"
```
</details>


<details><summary>ReactCommand</summary>
``` python
--8<-- "examples/commands/reaction.py"
```
</details>


<details><summary>RegexTriggeredCommand</summary>
``` python
--8<-- "examples/commands/regex_triggered.py"
```
</details>


<details><summary>ReplyCommand</summary>
``` python
--8<-- "examples/commands/reply.py"
```
</details>


<details><summary>StylesCommand</summary>
``` python
--8<-- "examples/commands/styles.py"
```
</details>


<details><summary>TypingCommand</summary>
``` python
--8<-- "examples/commands/typing.py"
```
</details>

### Handlers

<details><summary>ReactionDetailsHandler & FilteredReactionHandler</summary>
``` python
--8<-- "examples/handlers/reaction.py"
```
</details>


<details><summary>DeletionNotifierHandler</summary>
``` python
--8<-- "examples/handlers/remote_delete.py"
```
</details>


<details><summary>WelcomeHandler</summary>
``` python
--8<-- "examples/handlers/ready.py"
```
</details>
