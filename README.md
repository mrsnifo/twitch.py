# twitch.py
[![PyPI - Version](https://img.shields.io/pypi/v/twitch.py?color=%23673AB7)](https://pypi.org/project/twitch.py)
[![Python Versions](https://img.shields.io/pypi/pyversions/twitch.py?color=%23673AB7)](https://pypi.org/project/twitch.py)

A Python wrapper for Twitch that handles real-time events via WebSocket EventSub and integrates with the Helix API, all designed for easy asynchronous use.

> **⚠️ Major Rework in Progress**  
> I'm currently working on a complete rework of the library to improve performance, add new features, and enhance the overall developer experience. Stay tuned for updates!

## Installation
To install **twitch.py**, use the appropriate command for your operating system:

For Windows:
```bash
py -3 -m pip install --upgrade twitch.py
```

For macOS/Linux:
```bash
python3 -m pip install --upgrade twitch.py
```

## Quick Start
Here's a simple example to get you started with twitch.py:

```python
from twitch import Client
from twitch.types import eventsub

client = Client(client_id='YOUR_CLIENT_ID')

@client.event
async def on_ready():
    print('Client is ready!')

@client.event
async def on_follow(data: eventsub.channels.FollowEvent):
    await client.channel.chat.send_message(f'{data["user_name"]} just followed the channel!')

client.run('YOUR_USER_ACCESS_TOKEN')
```

## OAuth Authentication
Authenticate easily with Twitch using the Device Flow authentication method:

```python
from twitch import Client
from twitch.types import eventsub
from twitch.ext.oauth import DeviceAuthFlow, Scopes

client = Client(client_id='YOUR_CLIENT_ID')

DeviceAuthFlow(
    client=client,
    scopes=[Scopes.CHANNEL_READ_SUBSCRIPTIONS]
)

@client.event
async def on_code(code: str):
    print(f'Go to https://www.twitch.tv/activate and enter this code: {code}')

@client.event
async def on_auth(access_token: str, refresh_token: str):
    print(f'Access Token: {access_token}')
    
@client.event
async def on_subscribe(data: eventsub.channels.SubscribeEvent):
    await client.channel.chat.send_message(f'{data["user_name"]} just Subscribed!')

client.run()
```

## Documentation and Support
For more detailed instructions, visit the [twitch.py Documentation](https://twitchpy.readthedocs.io/latest/).

Need help or want to join the community? Join the [Discord server](https://discord.gg/UFTkgnse7d).