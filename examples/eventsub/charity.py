from twitch.eventsub import (ClientUser, Event, ChannelCharityCampaignStartEvent, ChannelCharityCampaignProgressEvent,
                             ChannelCharityCampaignStopEvent, ChannelCharityCampaignDonationEvent)

client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')


@client.event
async def on_channel_charity_start_v1(message: Event[ChannelCharityCampaignStartEvent]):
    """Handle charity campaign start event"""
    event = message.event
    await client.user.send_chat_message(
        f"Charity campaign started for {event.charity_name}! Goal: ${event.target_amount}"
    )


@client.event
async def on_channel_charity_progress_v1(message: Event[ChannelCharityCampaignProgressEvent]):
    """Handle charity campaign progress updates"""
    event = message.event
    progress_percent = (event.current_amount.value / event.target_amount.value) * 100
    await client.user.send_chat_message(
        f"Charity progress: {event.target_amount.currency}{event.current_amount.value}/"
        f"{event.target_amount.currency}{event.target_amount.value} ({progress_percent:.1f}%)"
    )


@client.event
async def on_channel_charity_stop_v1(message: Event[ChannelCharityCampaignStopEvent]):
    """Handle charity campaign end event"""
    event = message.event
    await client.user.send_chat_message(
        f"Charity campaign ended! Final amount raised: ${event.current_amount.value} for {event.charity_name}"
    )


@client.event
async def on_channel_charity_donate_v1(message: Event[ChannelCharityCampaignDonationEvent]):
    """Handle individual charity donations"""
    event = message.event
    await client.user.send_chat_message(
        f"Thank you {event.user.name} for donating {event.amount.currency}{event.amount.value} to the charity!"
    )


@client.event
async def on_ready():
    """Called when client is ready and connected"""
    print("Client connected and listening to charity events")


# Start the client with OAuth tokens
client.run('ACCESS_TOKEN', 'REFRESH_TOKEN')