---
icon: material/information-slab-circle
hide:
  - toc
---

# Introduction
___

EventSub provides real-time notifications for Twitch events like follows, subscriptions, chat messages, and stream updates.

For other events, check the docstrings of each method in the [Classes](classes.md) section.

## Basic Events

Every client includes these default events:

```python
@client.event
async def on_ready():
    """Called when client is ready and session is open"""
    pass

@client.event
async def setup_hook():
    """Called during client initialization"""
    pass
```

## Token Management Events

```python
@client.event
async def on_token_update(user_id, access_token, refresh_token):
    """Called when a token is updated"""
    pass

@client.event
async def on_token_remove(user_id):
    """Called when a token is removed"""
    pass
```

## Connection Events

```python
@client.event
async def on_connect():
    """Called when client connects"""
    pass

@client.event
async def on_shard_connect(shard_id):
    """Called when a shard connects"""
    pass

@client.event
async def on_shard_disconnect(shard_id):
    """Called when a shard disconnects"""
    pass

@client.event
async def on_disconnect():
    """Called when client disconnects"""
    pass
```

## Subscription Limits

Cost-based system for **ClientUser**:

* **3 subscriptions max** with identical type and condition values
* **No cost** for user-authorized subscriptions (e.g., `channel.subscribe`)  
* **Costs apply** for user-specified subscriptions without authorization (e.g., `stream.online`)