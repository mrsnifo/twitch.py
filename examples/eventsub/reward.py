from twitch.eventsub import ClientUser, Event, ChannelPointsCustomRewardRedemptionAddEvent

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_channel_reward_redeem_add_v1(message: Event[ChannelPointsCustomRewardRedemptionAddEvent]):
    """Handle channel point reward redemptions"""
    event = message.event

    if event.status == 'fulfilled':
        await client.user.send_chat_message(f'{event.user.name} has redeemed {event.reward.title}!')

        # Special action for specific reward - grant VIP status
        if event.reward.title == 'MAXWIN':
            await client.user.add_channel_vip(event.user.id)

async def on_ready():
    """Called when client is ready"""
    print("Client connected.")

client.run('ACCESS_TOKEN', 'REFRESH_TOKEN')