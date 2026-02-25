---
description: "Get started with twitch.py. Learn how to install the library, set up your Twitch app, and choose the right approach for your bot with code examples for App, ClientUser, and ClientApp."
icon: lucide/zap
hide:
  - toc
search:
  exclude: true
---

# Quickstart

## Prerequisites

- Python 3.9 or higher
- A Twitch account

## Step 1: Create a Twitch Application

1. Go to the [Twitch Developer Console](https://dev.twitch.tv/console)
2. Click **Register Your Application**
3. Fill in a name and category, leave OAuth Redirect URLs empty for now
4. Click **Create** and copy your **Client ID** and **Client Secret**

!!! warning "Keep your Client Secret safe"
    Never commit your Client Secret to git or share it publicly.

## Step 2: Install the Library

```bash
pip install twitch.py
```

## Step 3: Getting a User Access Token

For `ClientUser` and `ClientApp`, you'll need a user access token.

```python
from twitch.oauth import DeviceCodeFlow, Scopes
import asyncio

async def main():
    async with DeviceCodeFlow('CLIENT_ID', 'CLIENT_SECRET') as flow:
        device_code = await flow.request_device_code({
            Scopes.USER_READ_CHAT,
            Scopes.USER_WRITE_CHAT,
            Scopes.MODERATOR_READ_FOLLOWERS
        })

        print(f"Go to: {device_code.verification_uri}")
        print(f"Enter code: {device_code.user_code}")

        token = await flow.wait_for_device_token(device_code.device_code)
        print(f"Access Token: {token.access_token}")
        print(f"Refresh Token: {token.refresh_token}")

asyncio.run(main())
```

Save the tokens, because you'll need them to run your bot.

## Step 4: Choose Your Approach

=== "App"

    Use this if you just need to fetch data from Twitch without real-time events.

    ```python
    from twitch import App
    import asyncio

    async def main():
        async with App('YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET') as app:
            results = await app.application.search_channels('gaming')
            print(f"Found {len(results)} channels")

    asyncio.run(main())
    ```

=== "ClientUser"

    Use this for a bot that works only with your own Twitch account.

    ```python
    from twitch.eventsub import ClientUser, Event, ChannelChatMessageEvent
    import logging

    client = ClientUser('YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET')

    @client.event
    async def on_chat_message_v1(message: Event[ChannelChatMessageEvent]):
        username = message.event.chatter.name
        msg = message.event.message.text.lower()

        if msg == '!hello':
            await client.user.send_chat_message(f"Hello @{username}!")

    client.run('YOUR_ACCESS_TOKEN', log_level=logging.INFO)
    ```

=== "ClientApp"

    Use this for a bot that works across multiple streamers or channels.

    ```python
    from twitch.eventsub import ClientApp, Event, StreamOnlineEvent
    import logging

    client = ClientApp('YOUR_CLIENT_ID', 'YOUR_CLIENT_SECRET')

    @client.event
    async def on_stream_online_v1(message: Event[StreamOnlineEvent]):
        print(f"{message.event.broadcaster.name} is now live!")

    @client.event
    async def on_ready():
        user = await client.add_user('USER_ACCESS_TOKEN', 'USER_REFRESH_TOKEN')
        await client.eventsub.stream_online(user.id)

    client.run('YOUR_CONDUIT_ID', shard_ids=(0,), log_level=logging.INFO)
    ```