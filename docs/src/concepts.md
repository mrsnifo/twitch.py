---
description: "Understand the three main parts of twitch.py: the main App class for API calls, EventSub for real-time notifications, and OAuth for authentication. Learn which tool to use for your bot or application."
icon: lucide/lightbulb
search:
  exclude: true
---

# Concepts

twitch.py has three main components:

- [**App**](#app) for Helix API calls
- [**EventSub**](#eventsub) for real-time event notifications
- [**OAuth**](#oauth) for authentication

## App

The `App` class is your primary tool for working with the Helix API. Use it when you need to search for channels, get user or stream data, or carry out one-time operations.

```python
from twitch import App
import asyncio

async def main():
    async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
        results = await app.application.search_channels('gaming')
        for channel in results:
            print(f"{channel.name} - {channel.game_name}")

asyncio.run(main())
```

## EventSub

EventSub is Twitch's system for real-time event notifications. Instead of checking for changes repeatedly, you subscribe to events, and Twitch sends them to your app as they happen.

### ClientUser

`ClientUser` is for **self-bots** that act as your own Twitch account and is designed for simple, personal use.

!!! tip "Event handlers"
    Event handlers registered with `@client.event` are **auto-subscribed**, a behavior **exclusive to `ClientUser`**.

    Class-based require manual EventSub subscriptions.


```python
from twitch.eventsub import ClientUser, Event, ChannelChatMessageEvent
import logging

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_chat_message_v1(self, message: Event[ChannelChatMessageEvent]):
    if '!hello' in message.event.message.text:
        await self.user.send_chat_message(f"Hi @{message.event.chatter.name}!")

client.run('ACCESS_TOKEN', log_level=logging.INFO)
```

### ClientApp

This is better for bots that work with multiple streamers. It uses conduits and shards to scale.

```python
from twitch.eventsub import ClientApp, Event, StreamOnlineEvent
import logging

class LiveAlert(ClientApp):
    async def on_stream_online_v1(self, message: Event[StreamOnlineEvent]):
        print(f"{message.event.broadcaster.name} is now live!")

    async def on_ready(self):
        user = await self.add_user('STREAMER_TOKEN', 'STREAMER_REFRESH')
        await self.eventsub.stream_online(user.id)

alerts = LiveAlert('CLIENT_ID', 'CLIENT_SECRET')
alerts.run('CONDUIT_ID', log_level=logging.INFO)
```

## OAuth

OAuth is how users give permission to your application. Twitch uses OAuth 2.0 to allow your app to act on behalf of a user.

**App Access Token** represents your application, not a user. It's used for app-level tasks like searching channels. No user login is needed.

**User Access Token** represents a specific Twitch user. It allows actions on their behalf, like sending chat messages or moderating. User authorization is required.

### Device Code Flow

This is recommended for bots and CLI tools. The user authorizes in their browser, while your app waits.

```python
from twitch.oauth import DeviceCodeFlow, Scopes

async with DeviceCodeFlow('CLIENT_ID', 'CLIENT_SECRET') as flow:
    device_code = await flow.request_device_code({
        Scopes.USER_READ_CHAT,
        Scopes.USER_WRITE_CHAT
    })

    print(f"Go to: {device_code.verification_uri}")
    print(f"Enter code: {device_code.user_code}")

    token = await flow.wait_for_device_token(device_code.device_code)
```

### Authorization Code Flow

This is for web apps with a backend server. The user is redirected to Twitch and back with an authorization code.

## Choosing the Right Tool

=== "I need to fetch data"
    Use `App` for searching channels, getting stream info, or any one-time Helix API call.

=== "I'm building a personal bot"
    Use `ClientUser` if the bot acts as your own account on a single channel.

=== "I'm building a bot for many streamers"
    Use `ClientApp` with a conduit if you need to handle events across multiple channels.

=== "I need user login"
    Use `DeviceCodeFlow` for CLI tools and bots, or `AuthorizationCodeFlow` for web apps.