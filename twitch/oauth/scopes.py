"""
The MIT License (MIT)

Copyright (c) 2025-present mrsnifo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from enum import Enum

__all__ = ('Scopes',)


class Scopes(str, Enum):
    """
    An enumeration of available Twitch OAuth scopes.

    Each scope grants specific permissions for accessing or managing resources
    via the Twitch API. Scopes should be requested based on the minimum permissions
    required for your application's functionality.

    Attributes
    ----------
    ANALYTICS_READ_EXTENSIONS: str
        View analytics data for the Twitch Extensions owned by the authenticated account.
    ANALYTICS_READ_GAMES: str
        View analytics data for the games owned by the authenticated account.
    BITS_READ: str
        View Bits information for a channel.
    CHANNEL_BOT: str
        Joins your channel’s chatroom as a bot user, and perform chat-related actions as that user.
    CHANNEL_MANAGE_ADS: str
        Manage ads schedule on a channel.
    CHANNEL_READ_ADS: str
        Read the ads schedule and details on your channel.
    CHANNEL_MANAGE_BROADCAST: str
        Manage a channel’s broadcast configuration, including updating channel configuration and managing
        stream markers and stream tags.
    CHANNEL_READ_CHARITY: str
        Read charity campaign details and user donations on your channel.
    CHANNEL_EDIT_COMMERCIAL: str
        Run commercials on a channel.
    CHANNEL_READ_EDITORS: str
        View a list of users with the editor role for a channel.
    CHANNEL_MANAGE_EXTENSIONS: str
        Manage a channel’s Extension configuration, including activating Extensions.
    CHANNEL_READ_GOALS: str
        View Creator Goals for a channel.
    CHANNEL_READ_GUEST_STAR: str
        Read Guest Star details for your channel.
    CHANNEL_MANAGE_GUEST_STAR: str
        Manage Guest Star for your channel.
    CHANNEL_READ_HYPE_TRAIN: str
        View Hype Train information for a channel.
    CHANNEL_MANAGE_MODERATORS: str
        Add or remove the moderator role from users in your channel.
    CHANNEL_READ_POLLS: str
        View a channel’s polls.
    CHANNEL_MANAGE_POLLS: str
        Manage a channel’s polls.
    CHANNEL_READ_PREDICTIONS: str
        View a channel’s Channel Points Predictions.
    CHANNEL_MANAGE_PREDICTIONS: str
        Manage a channel’s Channel Points Predictions.
    CHANNEL_MANAGE_RAIDS: str
        Manage a channel raiding another channel.
    CHANNEL_READ_REDEMPTIONS: str
        View Channel Points custom rewards and their redemptions on a channel.
    CHANNEL_MANAGE_REDEMPTIONS: str
        Manage Channel Points custom rewards and their redemptions on a channel.
    CHANNEL_MANAGE_SCHEDULE: str
        Manage a channel’s stream schedule.
    CHANNEL_READ_STREAM_KEY: str
        View an authorized user’s stream key.
    CHANNEL_READ_SUBSCRIPTIONS: str
        View a list of all subscribers to a channel and check if a user is subscribed to a channel.
    CHANNEL_MANAGE_VIDEOS: str
        Manage a channel’s videos, including deleting videos.
    CHANNEL_READ_VIPS: str
        Read the list of VIPs in your channel.
    CHANNEL_MANAGE_VIPS: str
        Add or remove the VIP role from users in your channel.
    CHANNEL_MODERATE: str
        Perform moderation actions in a channel.
    CLIPS_EDIT: str
        Manage Clips for a channel.
    MODERATION_READ: str
        View a channel’s moderation data including Moderators, Bans, Timeouts, and AutoMod settings.
    MODERATOR_MANAGE_ANNOUNCEMENTS: str
        Send announcements in channels where you have the moderator role.
    MODERATOR_MANAGE_AUTOMOD: str
        Manage messages held for review by AutoMod in channels where you are a moderator.
    MODERATOR_READ_AUTOMOD_SETTINGS: str
        View a broadcaster’s AutoMod settings.
    MODERATOR_MANAGE_AUTOMOD_SETTINGS: str
        Manage a broadcaster’s AutoMod settings.
    MODERATOR_READ_BANNED_USERS: str
        Read the list of bans or unbans in channels where you have the moderator role.
    MODERATOR_MANAGE_BANNED_USERS: str
        Ban and unban users.
    MODERATOR_READ_BLOCKED_TERMS: str
        View a broadcaster’s list of blocked terms.
    MODERATOR_MANAGE_BLOCKED_TERMS: str
        Manage a broadcaster’s list of blocked terms.
    MODERATOR_READ_CHAT_MESSAGES: str
        Read deleted chat messages in channels where you have the moderator role.
    MODERATOR_MANAGE_CHAT_MESSAGES: str
        Delete chat messages in channels where you have the moderator role.
    MODERATOR_READ_CHAT_SETTINGS: str
        View a broadcaster’s chat room settings.
    MODERATOR_MANAGE_CHAT_SETTINGS: str
        Manage a broadcaster’s chat room settings.
    MODERATOR_READ_CHATTERS: str
        View the chatters in a broadcaster’s chat room.
    MODERATOR_READ_FOLLOWERS: str
        Read the followers of a broadcaster.
    MODERATOR_READ_GUEST_STAR: str
        Read Guest Star details for a channel.
    MODERATOR_MANAGE_GUEST_STAR: str
        Manage Guest Star for a channel.
    MODERATOR_READ_SHIELD_MODE: str
        View a broadcaster’s Shield Mode status.
    MODERATOR_MANAGE_SHIELD_MODE: str
        Manage a broadcaster’s Shield Mode status.
    MODERATOR_READ_SHOUTOUTS: str
        View a broadcaster’s shoutouts.
    MODERATOR_MANAGE_SHOUTOUTS: str
        Manage a broadcaster’s shoutouts.
    MODERATOR_READ_SUSPICIOUS_USERS: str
        View Suspicious User details for a broadcaster’s channel.
    MODERATOR_READ_UNBAN_REQUESTS: str
        View a broadcaster’s unban requests.
    MODERATOR_MANAGE_UNBAN_REQUESTS: str
        Manage a broadcaster’s unban requests.
    MODERATOR_READ_WARNINGS: str
        View a broadcaster’s warnings.
    MODERATOR_MANAGE_WARNINGS: str
        Manage a broadcaster’s warnings.
    USER_BOT: str
        Joins chatrooms as a bot user, and perform chat-related actions as that user.
    USER_EDIT: str
        Manage a user object.
    USER_EDIT_BROADCAST: str
        Edit your channel’s broadcast configuration including extension configuration.
    USER_READ_BLOCKED_USERS: str
        Read the list of users that you have blocked.
    USER_MANAGE_BLOCKED_USERS: str
        Manage the block list of a user.
    USER_READ_BROADCAST: str
        View a user’s broadcasting configuration, including Extension configurations.
    USER_READ_CHAT: str
        View chat messages.
    USER_MANAGE_CHAT_COLOR: str
        Update the color used for the user’s name in chat.
    USER_READ_EMAIL: str
        View a user’s email address.
    USER_READ_EMOTES: str
        View an authorized user’s emotes.
    USER_READ_FOLLOWS: str
        View the list of channels a user follows.
    USER_READ_MODERATED_CHANNELS: str
        View the list of channels a user has moderator privileges in.
    USER_READ_SUBSCRIPTIONS: str
        View a user’s subscriptions.
    USER_READ_WHISPERS: str
        View your whisper messages.
    USER_MANAGE_WHISPERS: str
        Send whisper messages.
    USER_WRITE_CHAT: str
        Send chat messages for the user.
    """

    # Analytics
    ANALYTICS_READ_EXTENSIONS = 'analytics:read:extensions'
    ANALYTICS_READ_GAMES = 'analytics:read:games'

    # Bits
    BITS_READ = 'bits:read'

    # Channel
    CHANNEL_BOT = 'channel:bot'
    CHANNEL_MANAGE_ADS = 'channel:manage:ads'
    CHANNEL_READ_ADS = 'channel:read:ads'
    CHANNEL_MANAGE_BROADCAST = 'channel:manage:broadcast'
    CHANNEL_READ_CHARITY = 'channel:read:charity'
    CHANNEL_EDIT_COMMERCIAL = 'channel:edit:commercial'
    CHANNEL_READ_EDITORS = 'channel:read:editors'
    CHANNEL_MANAGE_EXTENSIONS = 'channel:manage:extensions'
    CHANNEL_READ_GOALS = 'channel:read:goals'
    CHANNEL_READ_GUEST_STAR = 'channel:read:guest_star'
    CHANNEL_MANAGE_GUEST_STAR = 'channel:manage:guest_star'
    CHANNEL_READ_HYPE_TRAIN = 'channel:read:hype_train'
    CHANNEL_MANAGE_MODERATORS = 'channel:manage:moderators'
    CHANNEL_READ_POLLS = 'channel:read:polls'
    CHANNEL_MANAGE_POLLS = 'channel:manage:polls'
    CHANNEL_READ_PREDICTIONS = 'channel:read:predictions'
    CHANNEL_MANAGE_PREDICTIONS = 'channel:manage:predictions'
    CHANNEL_MANAGE_RAIDS = 'channel:manage:raids'
    CHANNEL_READ_REDEMPTIONS = 'channel:read:redemptions'
    CHANNEL_MANAGE_REDEMPTIONS = 'channel:manage:redemptions'
    CHANNEL_MANAGE_SCHEDULE = 'channel:manage:schedule'
    CHANNEL_READ_STREAM_KEY = 'channel:read:stream_key'
    CHANNEL_READ_SUBSCRIPTIONS = 'channel:read:subscriptions'
    CHANNEL_MANAGE_VIDEOS = 'channel:manage:videos'
    CHANNEL_READ_VIPS = 'channel:read:vips'
    CHANNEL_MANAGE_VIPS = 'channel:manage:vips'
    CHANNEL_MODERATE = 'channel:moderate'
    CLIPS_EDIT = 'clips:edit'

    # Moderation
    MODERATION_READ = 'moderation:read'
    MODERATOR_MANAGE_ANNOUNCEMENTS = 'moderator:manage:announcements'
    MODERATOR_MANAGE_AUTOMOD = 'moderator:manage:automod'
    MODERATOR_READ_AUTOMOD_SETTINGS = 'moderator:read:automod_settings'
    MODERATOR_MANAGE_AUTOMOD_SETTINGS = 'moderator:manage:automod_settings'
    MODERATOR_READ_BANNED_USERS = 'moderator:read:banned_users'
    MODERATOR_MANAGE_BANNED_USERS = 'moderator:manage:banned_users'
    MODERATOR_READ_BLOCKED_TERMS = 'moderator:read:blocked_terms'
    MODERATOR_MANAGE_BLOCKED_TERMS = 'moderator:manage:blocked_terms'
    MODERATOR_READ_CHAT_MESSAGES = 'moderator:read:chat_messages'
    MODERATOR_MANAGE_CHAT_MESSAGES = 'moderator:manage:chat_messages'
    MODERATOR_READ_CHAT_SETTINGS = 'moderator:read:chat_settings'
    MODERATOR_MANAGE_CHAT_SETTINGS = 'moderator:manage:chat_settings'
    MODERATOR_READ_CHATTERS = 'moderator:read:chatters'
    MODERATOR_READ_FOLLOWERS = 'moderator:read:followers'
    MODERATOR_READ_GUEST_STAR = 'moderator:read:guest_star'
    MODERATOR_MANAGE_GUEST_STAR = 'moderator:manage:guest_star'
    MODERATOR_READ_SHIELD_MODE = 'moderator:read:shield_mode'
    MODERATOR_MANAGE_SHIELD_MODE = 'moderator:manage:shield_mode'
    MODERATOR_READ_SHOUTOUTS = 'moderator:read:shoutouts'
    MODERATOR_MANAGE_SHOUTOUTS = 'moderator:manage:shoutouts'
    MODERATOR_READ_SUSPICIOUS_USERS = 'moderator:read:suspicious_users'
    MODERATOR_READ_UNBAN_REQUESTS = 'moderator:read:unban_requests'
    MODERATOR_MANAGE_UNBAN_REQUESTS = 'moderator:manage:unban_requests'
    MODERATOR_READ_WARNINGS = 'moderator:read:warnings'
    MODERATOR_MANAGE_WARNINGS = 'moderator:manage:warnings'

    # User
    USER_BOT = 'user:bot'
    USER_EDIT = 'user:edit'
    USER_EDIT_BROADCAST = 'user:edit:broadcast'
    USER_READ_BLOCKED_USERS = 'user:read:blocked_users'
    USER_MANAGE_BLOCKED_USERS = 'user:manage:blocked_users'
    USER_READ_BROADCAST = 'user:read:broadcast'
    USER_READ_CHAT = 'user:read:chat'
    USER_MANAGE_CHAT_COLOR = 'user:manage:chat_color'
    USER_READ_EMAIL = 'user:read:email'
    USER_READ_EMOTES = 'user:read:emotes'
    USER_READ_FOLLOWS = 'user:read:follows'
    USER_READ_MODERATED_CHANNELS = 'user:read:moderated_channels'
    USER_READ_SUBSCRIPTIONS = 'user:read:subscriptions'
    USER_READ_WHISPERS = 'user:read:whispers'
    USER_MANAGE_WHISPERS = 'user:manage:whispers'
    USER_WRITE_CHAT = 'user:write:chat'