# twitch.py
[![PyPI - Version](https://img.shields.io/pypi/v/twitch.py?color=%236A5ACD)](https://pypi.org/project/twitch.py)
[![Python Versions](https://img.shields.io/pypi/pyversions/twitch.py?color=%236A5ACD)](https://pypi.org/project/twitch.py)

An async Python wrapper for Twitch that handles real-time events via WebSocket EventSub and integrates with the Helix API.

## Key Features
* Async/await support throughout
* Complete Twitch Helix API integration
* WebSocket EventSub for real-time events
* Built-in authentication and token management

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

## Quick Example
```python
from twitch import App

async def main():
    async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
        emotes = await app.application.get_global_emotes()
        print(f'Found {len(emotes)} global emotes')

import asyncio
asyncio.run(main())
```

## Client App Example
```python
from twitch.eventsub import ClientApp, Event, ChannelChatMessageEvent

client = ClientApp('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_chat_message_v1(message: Event[ChannelChatMessageEvent]):
    print(message.event.message)

@client.event
async def on_ready():
    user = await client.add_user('ACCESS_TOKEN')
    await client.eventsub.channel_chat_message(broadcaster_user_id=user.id, user_id=user.id)

# Uses availability-based shard selection. For multi-sharding use MultiShardClientApp.
client.run('CONDUIT_ID', shard_ids=(0,))
```

## Client User Example
```python
from twitch.eventsub import ClientUser, Event, ChannelFollowEvent

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_ready():
    print('Client is ready!')
    await client.eventsub.channel_follow()

@client.event
async def on_channel_follow_v2(message: Event[ChannelFollowEvent]):
    print(f'{message.event.user.name} just followed!')

client.run('ACCESS_TOKEN')
```

More usage examples available in the examples folder.

## Links
- [Documentation](https://twitchpy.readthedocs.io/latest/)
- [Twitch API](https://discord.gg/UFTkgnse7d)