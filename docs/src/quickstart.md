---
title: "Quickstart"
description: "Get started with twitch.py. Learn how to install the library, set up your Twitch app, and choose the right approach for your bot with code examples for App, ClientUser, and ClientApp."
icon: material/clock-start
hide:
  - toc
search:
  exclude: true
---

# Quickstart

## Setup

### Create Twitch Application

Before using the library, you need to create a Twitch application:

1. Visit the [Twitch Developer Console](https://dev.twitch.tv/console)
2. Click **"Register Your Application"**
3. Fill in the application details:
   - **Name**: Your bot or application name
   - **OAuth Redirect URLs**: Leave empty (not needed for these examples)
   - **Category**: Select the most appropriate category
4. Click **"Create"** to register your application
5. Copy your **Client ID** and **Client Secret** for use in your code

## Installing
To install the library, you can just run the following command:
```bash
# Linux/macOS
python3 -m pip install -U twitch.py
# Windows
py -3 -m pip install -U twitch.py
```

For the development version:
```bash
git clone https://github.com/mrsnifo/twitch.py
cd twitch.py
python3 -m pip install -U .
```

## Choose Your Approach

=== "App"

    Quick data fetching

    ```python
    from twitch import App
    import asyncio

    async def main():
        async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
            results = await app.application.search_channels('gaming')
            print(f"Found {len(results)} channels")

    asyncio.run(main())
    ```

=== "ClientUser"

    Simple personal bot

    ```python
    from twitch.eventsub import ClientUser, Event, ChannelChatMessageEvent

    client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

    @client.event
    async def on_chat_message_v1(message: Event[ChannelChatMessageEvent]):
        if '!hello' in message.event.message.text:
            await client.user.send_chat_message(f"Hi {message.event.chatter.name}!")

    @client.event
    async def on_ready():
        await client.eventsub.channel_chat_message()

    client.run('ACCESS_TOKEN')
    ```

=== "ClientApp"

    Bot for multiple streamers

    ```python
    from twitch.eventsub import ClientApp, Event, StreamOnlineEvent

    client = ClientApp('CLIENT_ID', 'CLIENT_SECRET')

    @client.event
    async def on_stream_online_v1(message: Event[StreamOnlineEvent]):
        print(f"{message.event.broadcaster.name} went live!")

    @client.event
    async def on_ready():
        user = await client.add_user('STREAMER_TOKEN')
        await client.eventsub.stream_online(user.id)

    client.run('CONDUIT_ID', shard_ids=(0,))
    ```
