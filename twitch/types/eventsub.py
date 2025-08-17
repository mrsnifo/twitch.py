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

from typing import Optional, Any, Literal, Dict, NotRequired, List, Union, TypedDict
from .helix import Subscription

# WebSocket Messages
class Metadata(TypedDict):
    message_id: str
    message_type: str
    message_timestamp: str
    subscription_type: NotRequired[str]  # Notification & Revocation
    subscription_version: NotRequired[str]  # Notification & Revocation

class Session(TypedDict):
    id: str
    status: str
    keepalive_timeout_seconds: Optional[int]  # Reconnect
    reconnect_url: Optional[str]  # Welcome
    connected_at: str

class Transport(TypedDict):
    method: Literal['webhook', 'websocket']
    callback: NotRequired[str]  # Only present for webhook
    session_id: NotRequired[str]  # Only present for websocket
    connected_at: NotRequired[str]  # Only present for websocket

class NotificationPayload(TypedDict):
    subscription: Subscription
    event: Dict[str, Any]

class EventSubMessage(TypedDict):
    metadata: Metadata
    payload: Any

# Base Types
class BaseUser(TypedDict):
    """Base user information structure"""
    user_id: str
    user_login: str
    user_name: str

class BaseBroadcaster(TypedDict):
    """Base broadcaster information structure"""
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str

class BaseModerator(TypedDict):
    """Base moderator information structure"""
    moderator_user_id: str
    moderator_user_login: str
    moderator_user_name: str

class Emote(TypedDict):
    """Emote metadata structure"""
    id: str
    emote_set_id: str
    owner_id: NotRequired[str]
    format: NotRequired[List[Literal['animated', 'static']]]

class Cheermote(TypedDict):
    """Cheermote metadata structure"""
    prefix: str
    bits: int
    tier: int

class MessageFragment(TypedDict):
    """Message fragment structure"""
    text: str
    type: NotRequired[Literal['text', 'emote', 'cheermote', 'mention']]
    emote: NotRequired[Emote]
    cheermote: NotRequired[Cheermote]
    mention: NotRequired[BaseUser]

class Message(TypedDict):
    """Message structure"""
    text: str
    fragments: List[MessageFragment]

class ChatBadge(TypedDict):
    """Chat badge structure"""
    set_id: str
    id: str
    info: str

class MoneyAmount(TypedDict):
    """Money amount structure"""
    value: int
    decimal_places: int
    currency: str

# Automod Events
class AutomodBoundary(TypedDict):
    """Automod boundary structure"""
    start_pos: int
    end_pos: int

class Automod(TypedDict):
    """Automod information"""
    category: str
    level: int
    boundaries: List[AutomodBoundary]

class BlockedTerm(TypedDict):
    """Blocked term information"""
    term_id: str
    boundary: AutomodBoundary
    owner_broadcaster_user_id: str
    owner_broadcaster_user_login: str
    owner_broadcaster_user_name: str

class BlockedTerms(TypedDict):
    """Blocked terms collection"""
    terms_found: List[BlockedTerm]

class AutomodHoldEventV1(BaseBroadcaster, BaseUser):
    """Automod Message Hold Event V1"""
    message_id: str
    message: Message
    category: str
    level: int
    held_at: str

class AutomodHoldEventV2(BaseBroadcaster, BaseUser):
    """Automod Message Hold Event V2"""
    message_id: str
    message: Message
    held_at: str
    reason: Literal['automod', 'blocked_term']
    automod: NotRequired[Automod]
    blocked_term: NotRequired[BlockedTerms]

class AutomodUpdateEventV1(BaseBroadcaster, BaseUser, BaseModerator):
    """Automod Message Update Event V1"""
    message_id: str
    message: Message
    category: str
    level: int
    status: Literal['Approved', 'Denied', 'Expired']
    held_at: str

class AutomodUpdateEventV2(BaseBroadcaster, BaseUser, BaseModerator):
    """Automod Message Update Event V2"""
    message_id: str
    message: Message
    status: Literal['Approved', 'Denied', 'Expired']
    held_at: str
    reason: Literal['automod', 'blocked_term']
    automod: NotRequired[Automod]
    blocked_term: NotRequired[BlockedTerms]

class AutomodSettingsUpdateEventV1(BaseBroadcaster, BaseModerator):
    """Automod Settings Update Event V1"""
    bullying: int
    overall_level: Optional[int]
    disability: int
    race_ethnicity_or_religion: int
    misogyny: int
    sexuality_sex_or_gender: int
    aggression: int
    sex_based_terms: int
    swearing: int

class AutomodTermsUpdateEventV1(BaseBroadcaster, BaseModerator):
    """Automod Terms Update Event V1"""
    action: Literal['add_permitted', 'remove_permitted', 'add_blocked', 'remove_blocked']
    from_automod: bool
    terms: List[str]

# Channel Events
class ChannelAdBreakBeginEventV1(BaseBroadcaster):
    """Channel Ad Break Begin Event V1"""
    duration_seconds: int
    started_at: str
    is_automatic: bool
    requester_user_id: str
    requester_user_login: str
    requester_user_name: str

class ChannelBanEventV1(BaseBroadcaster, BaseUser, BaseModerator):
    """Channel Ban Event V1"""
    reason: str
    banned_at: str
    ends_at: Union[str, None]
    is_permanent: bool

class PowerUp(TypedDict):
    """Power-up information"""
    type: Literal['message_effect', 'celebration', 'gigantify_an_emote']
    emote: NotRequired[Emote]
    message_effect_id: NotRequired[str]

class ChannelBitsUseEventV1(BaseBroadcaster, BaseUser):
    """Channel Bits Use Event V1"""
    bits: int
    type: Literal['cheer', 'power_up']
    message: NotRequired[Message]
    power_up: NotRequired[PowerUp]

class ChannelChatClearEventV1(BaseBroadcaster):
    """Channel Chat Clear Event V1"""
    pass  # Only inherits from BaseBroadcaster

class ChannelChatClearUserMessagesEventV1(BaseBroadcaster):
    """Channel Chat Clear User Messages Event V1"""
    target_user_id: str
    target_user_name: str
    target_user_login: str

class Reply(TypedDict):
    """Reply information"""
    parent_message_id: str
    parent_message_body: str
    parent_user_id: str
    parent_user_name: str
    parent_user_login: str
    thread_message_id: str
    thread_user_id: str
    thread_user_name: str
    thread_user_login: str

class ChannelChatMessageEventV1(BaseBroadcaster):
    """Channel Chat Message Event V1"""
    chatter_user_id: str
    chatter_user_name: str
    chatter_user_login: str
    message_id: str
    message: Message
    message_type: Literal['text', 'channel_points_highlighted', 'channel_points_sub_only',
                          'user_intro', 'power_ups_message_effect', 'power_ups_gigantified_emote']
    badges: List[ChatBadge]
    cheer: NotRequired[Dict[str, int]]  # bits field
    color: str
    reply: NotRequired[Reply]
    channel_points_custom_reward_id: NotRequired[str]
    source_broadcaster_user_id: NotRequired[str]
    source_broadcaster_user_name: NotRequired[str]
    source_broadcaster_user_login: NotRequired[str]
    source_message_id: NotRequired[str]
    source_badges: NotRequired[List[ChatBadge]]
    is_source_only: NotRequired[bool]

class ChannelChatMessageDeleteEventV1(BaseBroadcaster):
    """Channel Chat Message Delete Event V1"""
    target_user_id: str
    target_user_name: str
    target_user_login: str
    message_id: str

# Subscription Events
class Sub(TypedDict):
    """Subscription information"""
    sub_tier: Literal['1000', '2000', '3000']
    is_prime: bool
    duration_months: int

class Resub(Sub):
    """Resubscription information"""
    cumulative_months: int
    streak_months: int
    is_gift: bool
    gifter_is_anonymous: NotRequired[bool]
    gifter_user_id: NotRequired[str]
    gifter_user_name: NotRequired[str]
    gifter_user_login: NotRequired[str]

class SubGift(TypedDict):
    """Subscription gift information"""
    duration_months: int
    cumulative_total: NotRequired[int]
    recipient_user_id: str
    recipient_user_name: str
    recipient_user_login: str
    sub_tier: Literal['1000', '2000', '3000']
    community_gift_id: NotRequired[str]

class CommunitySubGift(TypedDict):
    """Community subscription gift information"""
    id: str
    total: int
    sub_tier: Literal['1000', '2000', '3000']
    cumulative_total: NotRequired[int]

class Raid(BaseUser):
    """Raid information"""
    viewer_count: int
    profile_image_url: str

class Announcement(TypedDict):
    """Announcement information"""
    color: str

class Bits(TypedDict):
    """Bits badge tier information"""
    tier: int

class CharityDonation(TypedDict):
    """Charity donation information"""
    charity_name: str
    amount: MoneyAmount

class ChannelChatNotificationEventV1(BaseBroadcaster):
    """Channel Chat Notification Event V1"""
    chatter_user_id: str
    chatter_user_name: str
    chatter_is_anonymous: bool
    color: str
    badges: List[ChatBadge]
    system_message: str
    message_id: str
    message: Message
    notice_type: Literal[
        'sub', 'resub', 'sub_gift', 'community_sub_gift', 'gift_paid_upgrade',
        'prime_paid_upgrade', 'raid', 'unraid', 'pay_it_forward', 'announcement',
        'bits_badge_tier', 'charity_donation', 'shared_chat_sub', 'shared_chat_resub',
        'shared_chat_sub_gift', 'shared_chat_community_sub_gift',
        'shared_chat_gift_paid_upgrade', 'shared_chat_prime_paid_upgrade',
        'shared_chat_raid', 'shared_chat_pay_it_forward', 'shared_chat_announcement'
    ]
    sub: NotRequired[Sub]
    resub: NotRequired[Resub]
    sub_gift: NotRequired[SubGift]
    community_sub_gift: NotRequired[CommunitySubGift]
    gift_paid_upgrade: NotRequired[dict]
    prime_paid_upgrade: NotRequired[dict]
    pay_it_forward: NotRequired[dict]
    raid: NotRequired[Raid]
    unraid: NotRequired[dict]
    announcement: NotRequired[Announcement]
    bits_badge_tier: NotRequired[Bits]
    charity_donation: NotRequired[CharityDonation]
    source_broadcaster_user_id: NotRequired[str]
    source_broadcaster_user_name: NotRequired[str]
    source_broadcaster_user_login: NotRequired[str]
    source_message_id: NotRequired[str]
    source_badges: NotRequired[List[ChatBadge]]

class ChannelChatSettingsUpdateEventV1(BaseBroadcaster):
    """Channel Chat Settings Update Event V1"""
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration_minutes: Union[int, None]
    slow_mode: bool
    slow_mode_wait_time_seconds: Union[int, None]
    subscriber_mode: bool
    unique_chat_mode: bool

class ChannelSubscribeEventV1(BaseBroadcaster, BaseUser):
    """Channel Subscribe Event V1"""
    tier: Literal['1000', '2000', '3000']
    is_gift: bool

class ChannelCheerEventV1(BaseBroadcaster):
    """Channel Cheer Event V1"""
    is_anonymous: bool
    user_id: Union[str, None]
    user_login: Union[str, None]
    user_name: Union[str, None]
    message: str
    bits: int

class ChannelUpdateEventV2(BaseBroadcaster):
    """Channel Update Event V2"""
    title: str
    language: str
    category_id: str
    category_name: str
    content_classification_labels: List[str]

class ChannelUnbanEventV1(BaseBroadcaster, BaseUser, BaseModerator):
    """Channel Unban Event V1"""
    pass  # Only inherits from base classes

class ChannelFollowEventV2(BaseBroadcaster, BaseUser):
    """Channel Follow Event V2"""
    followed_at: str

class ChannelRaidEventV1(TypedDict):
    """Channel Raid Event V1"""
    from_broadcaster_user_id: str
    from_broadcaster_user_login: str
    from_broadcaster_user_name: str
    to_broadcaster_user_id: str
    to_broadcaster_user_login: str
    to_broadcaster_user_name: str
    viewers: int

# Moderation Events
class ModerationFollowers(TypedDict):
    """Followers mode information"""
    follow_duration_minutes: int

class ModerationSlow(TypedDict):
    """Slow mode information"""
    wait_time_seconds: int

class ModerationUser(BaseUser):
    """Moderation user information"""
    pass  # Inherits user info

class ModerationBan(BaseUser):
    """Ban information"""
    reason: NotRequired[str]

class ModerationTimeout(BaseUser):
    """Timeout information"""
    reason: NotRequired[str]
    expires_at: str

class ModerationDelete(BaseUser):
    """Delete message information"""
    message_id: str
    message_body: str

class ModerationAutomodTerms(TypedDict):
    """Automod terms information"""
    action: Literal['add', 'remove']
    list: Literal['blocked', 'permitted']
    terms: List[str]
    from_automod: bool

class ModerationUnbanRequest(BaseUser):
    """Unban request information"""
    is_approved: bool
    moderator_message: str

class ModerationWarn(BaseUser):
    """Warning information"""
    reason: NotRequired[str]
    chat_rules_cited: NotRequired[List[str]]

class ChannelModerateEventV1(BaseBroadcaster, BaseModerator):
    """Channel Moderate Event V1"""
    source_broadcaster_user_id: str
    source_broadcaster_user_login: str
    source_broadcaster_user_name: str
    action: Literal[
        'ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
        'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
        'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
        'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
        'mod', 'unmod', 'approve_unban_request', 'deny_unban_request',
        'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
        'shared_chat_unban', 'shared_chat_delete'
    ]
    followers: NotRequired[ModerationFollowers]
    slow: NotRequired[ModerationSlow]
    vip: NotRequired[ModerationUser]
    unvip: NotRequired[ModerationUser]
    mod: NotRequired[ModerationUser]
    unmod: NotRequired[ModerationUser]
    ban: NotRequired[ModerationBan]
    unban: NotRequired[ModerationUser]
    timeout: NotRequired[ModerationTimeout]
    untimeout: NotRequired[ModerationUser]
    raid: NotRequired[Raid]
    unraid: NotRequired[ModerationUser]
    delete: NotRequired[ModerationDelete]
    automod_terms: NotRequired[ModerationAutomodTerms]
    unban_request: NotRequired[ModerationUnbanRequest]

class ChannelModerateEventV2(BaseBroadcaster, BaseModerator):
    """Channel Moderate Event V2"""
    source_broadcaster_user_id: str
    source_broadcaster_user_login: str
    source_broadcaster_user_name: str
    action: Literal[
        'ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
        'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
        'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
        'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
        'mod', 'unmod', 'approve_unban_request', 'deny_unban_request', 'warn',
        'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
        'shared_chat_unban', 'shared_chat_delete'
    ]
    followers: NotRequired[ModerationFollowers]
    slow: NotRequired[ModerationSlow]
    vip: NotRequired[ModerationUser]
    unvip: NotRequired[ModerationUser]
    mod: NotRequired[ModerationUser]
    unmod: NotRequired[ModerationUser]
    ban: NotRequired[ModerationBan]
    unban: NotRequired[ModerationUser]
    timeout: NotRequired[ModerationTimeout]
    untimeout: NotRequired[ModerationUser]
    raid: NotRequired[Raid]
    unraid: NotRequired[ModerationUser]
    delete: NotRequired[ModerationDelete]
    automod_terms: NotRequired[ModerationAutomodTerms]
    unban_request: NotRequired[ModerationUnbanRequest]
    warn: NotRequired[ModerationWarn]

# Stream Events
class StreamOnlineEventV1(BaseBroadcaster):
    """Stream Online Event V1"""
    id: str
    type: Literal['live', 'playlist', 'watch_party', 'premiere', 'rerun']
    started_at: str

class StreamOfflineEventV1(BaseBroadcaster):
    """Stream Offline Event V1"""
    pass  # Only inherits from BaseBroadcaster

# Prediction Events
from typing import List, Optional, Literal, TypedDict, NotRequired


# --- Top Predictors and Outcomes ---

class TopPredictor(TypedDict):
    """User who used the most Channel Points on an outcome."""
    user_id: str
    user_login: str
    user_name: str
    channel_points_won: Optional[int]
    channel_points_used: int


class PredictionOutcome(TypedDict):
    """Prediction outcome details."""
    id: str
    title: str
    color: Literal['pink', 'blue']
    users: int
    channel_points: int
    top_predictors: NotRequired[List[TopPredictor]]

class ChannelPredictionBeginEventV1(BaseBroadcaster):
    """Channel Prediction Begin Event V1"""
    id: str
    title: str
    outcomes: List[PredictionOutcome]
    started_at: str
    locks_at: str


class ChannelPredictionProgressEventV1(ChannelPredictionBeginEventV1):
    """Channel Prediction Progress Event V1"""
    pass  # Same fields as Begin


class ChannelPredictionLockEventV1(BaseBroadcaster):
    """Channel Prediction Lock Event V1"""
    id: str
    title: str
    outcomes: List[PredictionOutcome]
    started_at: str
    locked_at: str


class ChannelPredictionEndEventV1(BaseBroadcaster):
    """Channel Prediction End Event V1"""
    id: str
    title: str
    winning_outcome_id: str
    outcomes: List[PredictionOutcome]
    status: Literal['resolved', 'canceled']
    started_at: str
    ended_at: str


# Chat User Message Events
class ChannelChatUserMessageHoldEventV1(BaseBroadcaster, BaseUser):
    """Channel Chat User Message Hold Event V1"""
    message_id: str
    message: Message

class ChannelChatUserMessageUpdateEventV1(BaseBroadcaster, BaseUser):
    """Channel Chat User Message Update Event V1"""
    message_id: str
    message: Message
    status: Literal['approved', 'denied', 'expired']

# Shared Chat Events
class SharedChatParticipant(TypedDict):
    """Shared chat participant information"""
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str

class ChannelSharedChatBeginEventV1(BaseBroadcaster):
    """Channel Shared Chat Begin Event V1"""
    session_id: str
    host_broadcaster_user_id: str
    host_broadcaster_user_login: str
    host_broadcaster_user_name: str
    participants: List[SharedChatParticipant]

class ChannelSharedChatUpdateEventV1(BaseBroadcaster):
    """Channel Shared Chat Update Event V1"""
    session_id: str
    host_broadcaster_user_id: str
    host_broadcaster_user_login: str
    host_broadcaster_user_name: str
    participants: List[SharedChatParticipant]

class ChannelSharedChatEndEventV1(BaseBroadcaster):
    """Channel Shared Chat End Event V1"""
    session_id: str
    host_broadcaster_user_id: str
    host_broadcaster_user_login: str
    host_broadcaster_user_name: str

# Subscription Events
class ChannelSubscriptionEndEventV1(BaseBroadcaster, BaseUser):
    """Channel Subscription End Event V1"""
    tier: Literal['1000', '2000', '3000']
    is_gift: bool

class ChannelSubscriptionGiftEventV1(BaseBroadcaster, BaseUser):
    """Channel Subscription Gift Event V1"""
    total: int
    tier: Literal['1000', '2000', '3000']
    cumulative_total: NotRequired[int]
    is_anonymous: bool

class EmoteData(TypedDict):
    """Emote data for subscription messages"""
    id: str
    begin: int
    end: int

class SubscriptionMessage(TypedDict):
    """Subscription message data"""
    text: str
    emotes: List[EmoteData]

class ChannelSubscriptionMessageEventV1(BaseBroadcaster, BaseUser):
    """Channel Subscription Message Event V1"""
    tier: Literal['1000', '2000', '3000']
    message: SubscriptionMessage
    cumulative_months: int
    streak_months: Union[int, None]
    duration_months: int

# Unban Request Events
class ChannelUnbanRequestCreateEventV1(BaseBroadcaster, BaseUser):
    """Channel Unban Request Create Event V1"""
    id: str
    text: str
    created_at: str

class ChannelUnbanRequestResolveEventV1(BaseBroadcaster, BaseUser, BaseModerator):
    """Channel Unban Request Resolve Event V1"""
    id: str
    resolution_text: str
    status: Literal['approved', 'denied']

# Moderator Events
class ChannelModeratorAddEventV1(BaseBroadcaster, BaseUser):
    """Channel Moderator Add Event V1"""
    pass  # Only inherits from base classes

class ChannelModeratorRemoveEventV1(BaseBroadcaster, BaseUser):
    """Channel Moderator Remove Event V1"""
    pass  # Only inherits from base classes

# Channel Points Events
class ChannelPointsAutomaticReward(TypedDict):
    """Automatic reward information"""
    type: str
    cost: int
    unlocked_emote: Union[Emote, None]

class ChannelPointsAutomaticRewardV2(TypedDict):
    """Automatic reward information V2"""
    type: str
    channel_points: int
    emote: Union[Emote, None]

class ChannelPointsAutomaticRewardRedemptionAddEventV1(BaseBroadcaster, BaseUser):
    """Channel Points Automatic Reward Redemption Add Event V1"""
    id: str
    reward: ChannelPointsAutomaticReward
    message: SubscriptionMessage
    user_input: str
    redeemed_at: str

class ChannelPointsAutomaticRewardRedemptionAddEventV2(BaseBroadcaster, BaseUser):
    """Channel Points Automatic Reward Redemption Add Event V2"""
    id: str
    reward: ChannelPointsAutomaticRewardV2
    message: Message
    redeemed_at: str

class CustomReward(TypedDict):
    """Custom reward information"""
    id: str
    title: str
    cost: int
    prompt: str

class GlobalCooldown(TypedDict):
    """Global cooldown information"""
    is_enabled: bool
    seconds: int

class MaxPerStream(TypedDict):
    """Max per stream information"""
    is_enabled: bool
    value: int

class MaxPerUserPerStream(TypedDict):
    """Max per user per stream information"""
    is_enabled: bool
    value: int

class Image(TypedDict):
    """Image information"""
    url_1x: str
    url_2x: str
    url_4x: str

class ChannelPointsCustomRewardAddEventV1(BaseBroadcaster):
    """Channel Points Custom Reward Add Event V1"""
    id: str
    is_enabled: bool
    is_paused: bool
    is_in_stock: bool
    title: str
    cost: int
    prompt: str
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool
    cooldown_expires_at: Union[str, None]
    redemptions_redeemed_current_stream: Union[int, None]
    max_per_stream: MaxPerStream
    max_per_user_per_stream: MaxPerUserPerStream
    global_cooldown: GlobalCooldown
    background_color: str
    image: Image
    default_image: Image

class ChannelPointsCustomRewardUpdateEventV1(ChannelPointsCustomRewardAddEventV1):
    """Channel Points Custom Reward Update Event V1"""
    pass  # Inherits all fields from add event

class ChannelPointsCustomRewardRemoveEventV1(ChannelPointsCustomRewardAddEventV1):
    """Channel Points Custom Reward Remove Event V1"""
    pass  # Inherits all fields from add event

class ChannelPointsCustomRewardRedemptionAddEventV1(BaseBroadcaster, BaseUser):
    """Channel Points Custom Reward Redemption Add Event V1"""
    id: str
    user_input: str
    status: Literal['unfulfilled', 'fulfilled', 'canceled']
    reward: CustomReward
    redeemed_at: str

class ChannelPointsCustomRewardRedemptionUpdateEventV1(ChannelPointsCustomRewardRedemptionAddEventV1):
    """Channel Points Custom Reward Redemption Update Event V1"""
    pass  # Inherits all fields from add event

# Poll Events
class PollChoice(TypedDict):
    """Poll choice information"""
    id: str
    title: str
    bits_votes: NotRequired[int]
    channel_points_votes: NotRequired[int]
    votes: NotRequired[int]

class PollVotingSettings(TypedDict):
    """Poll voting settings"""
    is_enabled: bool
    amount_per_vote: int

class ChannelPollBeginEventV1(BaseBroadcaster):
    """Channel Poll Begin Event V1"""
    id: str
    title: str
    choices: List[PollChoice]
    bits_voting: PollVotingSettings
    channel_points_voting: PollVotingSettings
    started_at: str
    ends_at: str

class ChannelPollProgressEventV1(ChannelPollBeginEventV1):
    """Channel Poll Progress Event V1"""
    pass  # Inherits all fields from begin event

class ChannelPollEndEventV1(BaseBroadcaster):
    """Channel Poll End Event V1"""
    id: str
    title: str
    choices: List[PollChoice]
    bits_voting: PollVotingSettings
    channel_points_voting: PollVotingSettings
    status: Literal['completed', 'archived', 'terminated']
    started_at: str
    ended_at: str

# Suspicious User Events
class ChannelSuspiciousUserUpdateEventV1(BaseBroadcaster, BaseModerator):
    """Channel Suspicious User Update Event V1"""
    user_id: str
    user_login: str
    user_name: str
    low_trust_status: str

class ChannelSuspiciousUserMessageEventV1(BaseBroadcaster):
    """Channel Suspicious User Message Event V1"""
    user_id: str
    user_login: str
    user_name: str
    low_trust_status: str
    shared_ban_channel_ids: List[str]
    types: List[str]
    ban_evasion_evaluation: str
    message: Message

# VIP Events
class ChannelVipAddEventV1(BaseBroadcaster, BaseUser):
    """Channel VIP Add Event V1"""
    pass  # Only inherits from base classes

class ChannelVipRemoveEventV1(BaseBroadcaster, BaseUser):
    """Channel VIP Remove Event V1"""
    pass  # Only inherits from base classes

# Warning Events
class ChannelWarningAcknowledgeEventV1(BaseBroadcaster, BaseUser):
    """Channel Warning Acknowledge Event V1"""
    pass  # Only inherits from base classes

class ChannelWarningSendEventV1(BaseBroadcaster, BaseUser, BaseModerator):
    """Channel Warning Send Event V1"""
    reason: NotRequired[str]
    chat_rules_cited: NotRequired[List[str]]

# Charity Events
class CharityDonationAmount(TypedDict):
    """Charity donation amount"""
    value: int
    decimal_places: int
    currency: str

class ChannelCharityDonationEventV1(BaseBroadcaster, BaseUser):
    """Channel Charity Donation Event V1"""
    id: str
    campaign_id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    amount: CharityDonationAmount

class ChannelCharityCampaignStartEventV1(TypedDict):
    """Channel Charity Campaign Start Event V1"""
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityDonationAmount
    target_amount: CharityDonationAmount
    started_at: str

class ChannelCharityCampaignProgressEventV1(TypedDict):
    """Channel Charity Campaign Progress Event V1"""
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityDonationAmount
    target_amount: CharityDonationAmount

class ChannelCharityCampaignStopEventV1(TypedDict):
    """Channel Charity Campaign Stop Event V1"""
    id: str
    broadcaster_id: str
    broadcaster_name: str
    broadcaster_login: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: CharityDonationAmount
    target_amount: CharityDonationAmount
    stopped_at: str

# Shield Mode Events
class ChannelShieldModeBeginEventV1(BaseBroadcaster, BaseModerator):
    """Channel Shield Mode Begin Event V1"""
    started_at: str

class ChannelShieldModeEndEventV1(BaseBroadcaster, BaseModerator):
    """Channel Shield Mode End Event V1"""
    ended_at: str

# Shoutout Events
class ChannelShoutoutCreateEventV1(BaseBroadcaster, BaseModerator):
    """Channel Shoutout Create Event V1"""
    to_broadcaster_user_id: str
    to_broadcaster_user_login: str
    to_broadcaster_user_name: str
    started_at: str
    viewer_count: int
    cooldown_ends_at: str
    target_cooldown_ends_at: str

class ChannelShoutoutReceiveEventV1(BaseBroadcaster):
    """Channel Shoutout Receive Event V1"""
    from_broadcaster_user_id: str
    from_broadcaster_user_login: str
    from_broadcaster_user_name: str
    viewer_count: int
    started_at: str

# Goal Events
class ChannelGoalBeginEventV1(BaseBroadcaster):
    """Channel Goal Begin Event V1"""
    id: str
    type: str
    description: str
    current_amount: int
    target_amount: int
    started_at: str

class ChannelGoalProgressEventV1(ChannelGoalBeginEventV1):
    """Channel Goal Progress Event V1"""
    pass  # Inherits all fields from begin event

class ChannelGoalEndEventV1(ChannelGoalBeginEventV1):
    """Channel Goal End Event V1"""
    is_achieved: bool
    ended_at: str

# Drop Events
class DropEntitlementGrantData(TypedDict):
    """Drop entitlement grant data"""
    organization_id: str
    category_id: str
    category_name: str
    campaign_id: str
    user_id: str
    user_name: str
    user_login: str
    entitlement_id: str
    benefit_id: str
    created_at: str

class DropEntitlementGrantEventV1(TypedDict):
    """Drop Entitlement Grant Event V1"""
    id: str
    data: DropEntitlementGrantData

# Extension Events
class ExtensionProduct(TypedDict):
    """Extension product information"""
    name: str
    sku: str
    bits: int
    in_development: bool

class ExtensionBitsTransactionCreateEventV1(BaseBroadcaster, BaseUser):
    """Extension Bits Transaction Create Event V1"""
    id: str
    extension_client_id: str
    product: ExtensionProduct

# User Events
class UserAuthorizationGrantEventV1(TypedDict):
    """User Authorization Grant Event V1"""
    client_id: str
    user_id: str
    user_login: str
    user_name: str

class UserAuthorizationRevokeEventV1(TypedDict):
    """User Authorization Revoke Event V1"""
    client_id: str
    user_id: str
    user_login: Union[str, None]
    user_name: Union[str, None]

class UserUpdateEventV1(BaseUser):
    """User Update Event V1"""
    email: str
    email_verified: bool
    description: str

# Whisper Events
class WhisperData(TypedDict):
    """Whisper data"""
    text: str

class UserWhisperMessageEventV1(TypedDict):
    """User Whisper Message Event V1"""
    from_user_id: str
    from_user_login: str
    from_user_name: str
    to_user_id: str
    to_user_login: str
    to_user_name: str
    whisper_id: str
    whisper: WhisperData