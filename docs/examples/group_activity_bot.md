This bot showcases combining two `Handler` subclasses — [DataMessageHandler][signalbot.DataMessageHandler] and [GroupUpdateHandler][signalbot.GroupUpdateHandler] — on a single class via multiple inheritance, so they can share state directly.
``` python
--8<-- "examples/group_activity_bot.py"
```
