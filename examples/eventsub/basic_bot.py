from twitch.eventsub import ClientUser, Event, ChannelFollowEvent, ChannelChatMessageEvent
from twitch.oauth import DeviceCodeFlow, Scopes
import asyncio


class Bot(ClientUser):

    async def on_channel_follow_v2(self, message: Event[ChannelFollowEvent]):
        """Called when someone follows your channel."""
        follower_name = message.event.user.name
        welcome_message = f"Welcome to the stream, @{follower_name}! Thanks for hitting that follow button!"
        await self.user.send_chat_message(welcome_message)

    async def on_chat_message_v1(self, message: Event[ChannelChatMessageEvent]):
        """Called when someone sends a chat message."""
        username = message.event.chatter.name
        msg = message.event.message.text.lower()

        if msg.startswith('!hello'):
            greeting = f"Hello there, @{username}! Hope you're enjoying the stream!"
            await self.user.send_chat_message(greeting)

        elif msg == "!info":
            info_msg = "This is an automated bot. Type !hello to get a greeting!"
            await self.user.send_chat_message(info_msg)

    async def on_ready(self):
        """Called when the bot connects successfully."""

        await self.eventsub.channel_follow()
        await self.eventsub.channel_chat_message()

        print("Bot is ready and connected to Twitch!")



async def main():
    bot = Bot('CLIENT_ID', 'CLIENT_SECRET')

    async with DeviceCodeFlow.from_app(bot) as flow:
        # Request device code for user authorization
        device_code = await flow.request_device_code({
            Scopes.MODERATOR_READ_FOLLOWERS,
            Scopes.USER_READ_CHAT,
            Scopes.USER_WRITE_CHAT
        })

        # Display authorization instructions to user
        print(f"Go to: {device_code.verification_uri}")
        print(f"Enter code: {device_code.user_code}")

        token = await flow.wait_for_device_token(device_code.device_code)

    async with bot:
        await bot.start(token.access_token, token.refresh_token)

asyncio.run(main())