---
description: "Learn how to set up and configure logging for twitch.py to monitor your bot's activity, debug issues, and track events."
icon: lucide/file-text
hide:
  - toc
---

# Logging

twitch.py relies on Python’s standard `logging` module. That is helpful for debugging during development or auditing after deployment. 

## Quick Setup

Pass `log_level` to the `run()` method:

```python
from twitch.eventsub import ClientUser
import logging

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_ready():
    print('Pog!')

client.run('ACCESS_TOKEN', log_level=logging.INFO)
```

## Log to File

```python
from twitch.eventsub import ClientUser
import logging

handler = logging.FileHandler(filename='twitch.log', encoding='utf-8', mode='w')

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')
client.run('ACCESS_TOKEN', log_handler=handler, log_level=logging.DEBUG)
```

## Disable Library Logging

If you want to set up logging yourself, pass `log_handler=None`:

```python
from twitch.eventsub import ClientUser
import logging

logging.basicConfig(level=logging.DEBUG)

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')
client.run('ACCESS_TOKEN', log_handler=None)
```

## Configure Root Logger

To make the logging configuration affect all loggers rather than just twitch.py, pass `root_logger=True`:

```python
from twitch.eventsub import ClientUser
import logging

handler = logging.FileHandler(filename='twitch.log', encoding='utf-8', mode='w')

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')
client.run('ACCESS_TOKEN', log_handler=handler, log_level=logging.DEBUG, root_logger=True)
```

## Using `setup_logging()`

If you want to set up logging without using `run()`, you can use `utils.setup_logging()`:

```python
from twitch import utils
import logging

utils.setup_logging(level=logging.INFO, root=False)
```

## Log Levels

| Level     | Description                                |
|-----------|--------------------------------------------|
| `DEBUG`   | Detailed information for debugging         |
| `INFO`    | General operational events                 |
| `WARNING` | Potential issues that don't stop the bot   |
| `ERROR`   | Serious problems that affect functionality |

## Module-Specific Logging

You can configure logging per module:

```python
import logging

logger = logging.getLogger('twitch')
logger.setLevel(logging.DEBUG)

logging.getLogger('twitch.http').setLevel(logging.WARNING)
```
