---
icon: lucide/bug
hide:
  - toc
---

# Debugging
___

## Overview

Testing EventSub events via the command-line interface ([CLI](https://dev.twitch.tv/docs/cli/)) mock WebSocket server lets you
simulate and test events.

!!! danger "Twitch CLI Compatibility"

    The Twitch CLI tool may be outdated and could have compatibility issues with current EventSub implementations.
    Use this debugging method with caution and consider it experimental.

!!! warning "ClientUser Only"

    The mock WebSocket debugging functionality only works with [ClientUser][twitch.eventsub.client.ClientUser]. 


## Setup
___

### Starting the Mock WebSocket Server

To start the mock WebSocket server, use the following command in your terminal:

```bash
twitch event websocket start-server
```

This command will start a WebSocket server on `127.0.0.1:8080` and provide endpoints for simulating EventSub events.
You should see output similar to:

```
2023/03/19 11:45:17 `Ctrl + C` to exit mock WebSocket servers.
2023/03/19 11:45:17 Started WebSocket server on 127.0.0.1:8080
2023/03/19 11:45:17 Simulate subscribing to events at: http://127.0.0.1:8080/eventsub/subscriptions
2023/03/19 11:45:17 Events can be forwarded to this server from another terminal with --transport=websocket
2023/03/19 11:45:17 Connect to the WebSocket server at: ws://127.0.0.1:8080/ws
```

### Connecting to the Mock Server

Use `ClientUser` and pass the mock WebSocket URL to the `start()` or `run()` method:

```python
from twitch.eventsub import ClientUser, Event, ChannelFollowEvent
from logging import DEBUG


client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_channel_follow_v2(message: Event[ChannelFollowEvent]):
    ...

@client.event
async def on_ready():
    """Called when client is ready"""
    await client.eventsub.channel_follow()

client.run(
    access_token='YOUR_USER_ACCESS_TOKEN',
    refresh_token='YOUR_REFRESH_TOKEN',  # Optional
    mock_url='ws://127.0.0.1:8080/ws',
    log_level=DEBUG
)
```

### Forwarding Mock Events

To forward mock events to your client, use the `twitch event trigger` command with the `--transport=websocket` flag.
For example, to trigger a channel ban event:

```bash
twitch event trigger channel.ban --transport=websocket
```

To target a specific client, use the `--session` flag with the session ID:

```bash
twitch event trigger channel.ban --transport=websocket --session=your_session_id
```
