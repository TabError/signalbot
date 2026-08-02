This bot showcases how to use the scheduler together with [ReadyHandler][signalbot.ReadyHandler], which runs once the bot has finished connecting, and [SignalBot.wait_until_ready()][signalbot.bot.SignalBot.wait_until_ready], which lets a scheduled job wait for that same point without needing a `DataMessageHandler`.
``` python
--8<-- "examples/bot_with_scheduler.py"
```
