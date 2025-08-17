from twitch.eventsub import MultiShardClientApp
from twitch import App
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("twitch")


class Bot(MultiShardClientApp):

    async def on_ready(self) -> None:
        """Called when the bot is fully initialized and ready."""
        logger.info("Bot is ready")

    async def on_shard_connect(self, shard_id: int) -> None:
        """Called when a shard connects to Twitch."""
        logger.info(f"Shard {shard_id} connected")

    async def setup_hook(self) -> None:
        # Subscribe to chat message events for specific broadcaster and user
        # await bot.eventsub.channel_chat_message(
        #     broadcaster_user_id='USER_ID',
        #     user_id='USER_ID'
        # )

        # Additional initialization can be done here:
        # - Database connections and user settings
        # - Additional event subscriptions
        # - Periodic task setup
        logger.info("Setup hook initialized")


async def main() -> None:
    async with App('CLIENT_ID', 'CLIENT_SECRET') as app:
        # Get or create a conduit for event distribution
        conduits = await app.application.get_conduits()
        conduit = conduits[0] if conduits else await app.application.create_conduit(shard_count=3)
        logger.info(f"Using conduit ID: {conduit.id} with {conduit.shard_count} shards")

    # Start the bot with all available shards
    async with Bot('CLIENT_ID', 'CLIENT_SECRET') as bot:
        await bot.start(
            conduit_id=conduit.id,
            shard_ids=tuple(range(conduit.shard_count))
        )

asyncio.run(main())