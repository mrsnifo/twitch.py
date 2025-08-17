from twitch.eventsub import ClientApp, Event, StreamOnlineEvent, StreamOfflineEvent


class LiveAlert(ClientApp):
    def __init__(self, client_id: str, client_secret: str):
        super().__init__(client_id, client_secret)
        self.bot = None

    async def on_stream_online_v1(self, message: Event[StreamOnlineEvent]):
        """Send message when streamer goes live."""
        await self.application.send_chat_message(
            sender_id=self.bot.id,
            broadcaster_id=message.event.broadcaster.id,
            message="Stream is now live!"
        )

    async def on_stream_offline_v1(self, message: Event[StreamOfflineEvent]):
        """Send message when streamer goes offline."""
        await self.application.send_chat_message(
            sender_id=self.bot.id,
            broadcaster_id=message.event.broadcaster.id,
            message="Stream has ended. Thanks for watching!"
        )

    async def on_ready(self):
        """Setup bot when ready."""

        # Bot user: This is the account that will send chat messages
        # Replace with actual bot account tokens
        bot_access_token = "BOT_ACCESS_TOKEN_HERE"
        bot_refresh_token = "BOT_REFRESH_TOKEN_HERE"
        self.bot = await self.add_user(bot_access_token, bot_refresh_token)

        # Streamer user: This is the channel you want to monitor for live/offline events
        # Replace with the streamer's tokens (they need to authorize your app)
        # Or if streamer is already authorized by the app, ignore this step and just directly subscribe
        streamer_access_token = "STREAMER_ACCESS_TOKEN_HERE"
        streamer_refresh_token = "STREAMER_REFRESH_TOKEN_HERE"
        user = await self.add_user(streamer_access_token, streamer_refresh_token)

        # Subscribe to stream events for the monitored user
        await self.eventsub.stream_online(user.id)
        await self.eventsub.stream_offline(user.id)


alerts = LiveAlert('CLIENT_ID', 'CLIENT_SECRET')
alerts.run('CONDUIT_ID')