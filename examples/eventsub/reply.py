from twitch.eventsub import ClientUser, Event, ChannelChatMessageEvent


client = ClientUser('CLIENT_ID', 'CLIENT_SECRET')

@client.event
async def on_chat_message_v1(message: Event[ChannelChatMessageEvent]):
    """Handle incoming chat messages and respond to commands"""
    event = message.event

    # Prevent bot from responding to its own messages (avoid loops)
    if event.chatter.id == client.user.id:
        return

    msg = event.message.text.lower()
    if msg.startswith('!pog'):
        await client.user.send_chat_message(
            f"PogChamp {event.chatter.name}!",
            reply_message_id=event.message_id  # Reply directly to user's message
        )


@client.event
async def on_ready():
    """Called when client is ready"""
    # Subscribe to chat message events for the channel
    await client.eventsub.channel_chat_message()
    print("Client connected and listening to chat")


client.run('ACCESS_TOKEN', 'REFRESH_TOKEN')