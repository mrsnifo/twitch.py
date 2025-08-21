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

from typing import TypedDict, TypeVar, List, Literal, NotRequired, Dict, Any, Optional

T = TypeVar('T')

class BaseUser(TypedDict):
    user_id: str
    user_login: str
    user_name: str

class BaseUserBroadcaster(TypedDict):
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str

class BaseBroadcaster(TypedDict):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str

class Pagination(TypedDict):
    cursor: NotRequired[str]

class Transport(TypedDict):
    method: Literal['webhook', 'websocket']
    callback: NotRequired[str]  # webhook only
    session_id: NotRequired[str]  # websocket only
    connected_at: NotRequired[str]
    disconnected_at: NotRequired[str]

class Subscription(TypedDict):
    id: str
    status: str
    type: str
    version: str
    cost: int
    condition: Dict[str, Any]
    transport: Transport
    created_at: str

class EventsubSubscription(TypedDict):
    total: int
    data: List[Subscription]
    total_cost: int
    max_total_cost: int
    pagination: Pagination

class PostTransport(TypedDict):
    method: Literal['webhook', 'websocket', 'conduit']
    callback: NotRequired[str]    # Webhook callback URL
    secret: NotRequired[str]      # Webhook secret
    session_id: NotRequired[str]  # WebSocket session ID
    conduit_id: NotRequired[str]  # Conduit ID


class Data[T](TypedDict):
    data: T


class DataL[T](TypedDict):
    data: List[T]


class PData[T](TypedDict):
    data: List[T]
    pagination: Pagination

# Star Commercial
class StarCommercial(TypedDict):
    length: int
    message: str
    retry_after: int


class CheermoteTier(TypedDict):
    min_bits: int
    id: str
    color: str
    images: Dict[str, Any]
    can_cheer: bool
    show_in_bits_card: bool

class Cheermote(TypedDict):
    prefix: str
    tiers: List[CheermoteTier]
    type: Literal[
        'global_first_party',
        'global_third_party',
        'channel_custom',
        'display_only',
        'sponsored'
    ]
    order: int
    last_updated: str
    is_charitable: bool

class EmoteImages(TypedDict):
    url_1x: str  # 28px x 28px
    url_2x: str  # 56px x 56px
    url_4x: str  # 112px x 112px

class BaseEmote(TypedDict):
    id: str
    name: str
    images: EmoteImages
    format: List[Literal["static", "animated"]]
    scale: List[Literal['1.0', '2.0', '3.0']]
    theme_mode: List[Literal['light', 'dark']]

class ChannelEmote(BaseEmote):
    tier: str  # Empty string if not subscription emote
    emote_type: Literal['bitstier', 'follower', 'subscriptions']
    emote_set_id: str

class GlobalEmote(BaseEmote):
    pass

class EmoteSet(BaseEmote):
    emote_type: Literal['bitstier', 'follower', 'subscriptions']
    emote_set_id: str
    owner_id: str

class EmoteData[T](TypedDict):
    data: List[T]
    template: str

# Badge Types
class BadgeVersion(TypedDict):
    id: str
    image_url_1x: str  # 18px x 18px
    image_url_2x: str  # 36px x 36px
    image_url_4x: str  # 72px x 72px
    title: str
    description: str
    click_action: Optional[str]
    click_url: Optional[str]

class ChatBadgeSet(TypedDict):
    set_id: str
    versions: List[BadgeVersion]


# Chat settings
class ChatSettings(TypedDict):
    broadcaster_id: str
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration: Optional[int]
    moderator_id: NotRequired[str]
    non_moderator_chat_delay: NotRequired[bool]
    non_moderator_chat_delay_duration: NotRequired[Optional[int]]
    slow_mode: bool
    slow_mode_wait_time: Optional[int]
    subscriber_mode: bool
    unique_chat_mode: bool


# Shared Chat
class SharedChatParticipant(TypedDict):
    broadcaster_id: str

class SharedChatSession(TypedDict):
    session_id: str
    host_broadcaster_id: str
    participants: List[SharedChatParticipant]
    created_at: str
    updated_at: str


# Send Chat Message
class MessageDropReason(TypedDict):
    code: str
    message: str

class SendMessageStatus(TypedDict):
    message_id: str
    is_sent: bool
    drop_reason: NotRequired[MessageDropReason]


# User Chat Color
class UserChatColor(BaseUser):
    color: str

# Channel Information
class ChannelInformation(BaseBroadcaster):
    broadcaster_language: str
    game_name: str
    game_id: str
    title: str
    delay: int
    tags: List[str]
    content_classification_labels: List[str]
    is_branded_content: bool


# Channel Teams
class Team(TypedDict):
    created_at: str
    updated_at: str
    info: str
    thumbnail_url: str
    team_name: str
    team_display_name: str
    banner: Optional[str]
    background_image_url: Optional[str]
    id: str

class ChannelTeam(Team):
    broadcaster_id: str
    broadcaster_login: str
    broadcaster_name: str

class TeamUsers(Team):
    users: List[BaseUser]

# Get users
class UserInfo(TypedDict):
    id: str
    login: str
    display_name: str
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    view_count: int  # deprecated
    email: Optional[str]
    created_at: str


# Games & Category & Search & Schedule
class Category(TypedDict):
    id: str
    name: str
    box_art_url: Optional[str]  # Get Game & Search Category

class Game(Category):
    igdb_id: str

class SearchChannel(TypedDict):
    id: str
    broadcaster_login: str
    display_name: str
    broadcaster_language: str
    game_id: str
    game_name: str
    is_live: bool
    tag_ids: List[str]  # deprecated
    tags: List[str]
    thumbnail_url: str
    title: str
    started_at: str


class StreamInfo(BaseUser):
    id: str
    game_id: str
    game_name: str
    type: str
    title: str
    tags: List[str]
    viewer_count: int
    started_at: str
    language: str
    thumbnail_url: str
    tag_ids: List[str]
    is_mature: bool


# Clips & Videos
class MutedSegment(TypedDict):
    duration: int
    offset: int

class Video(BaseUser):
    id: str
    stream_id: Optional[str]
    title: str
    description: str
    created_at: str
    published_at: str
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str
    duration: str
    muted_segments: Optional[List[MutedSegment]]

class Clip(TypedDict):
    id: str
    url: str
    embed_url: str
    broadcaster_id: str
    broadcaster_name: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    language: str
    title: str
    view_count: int
    created_at: str
    thumbnail_url: str
    duration: float
    vod_offset: Optional[int]
    is_featured: bool


# Content Classification Label
class ContentClassificationLabel(TypedDict):
    id: str
    description: str
    name: str


# Stream  Schedule
class ScheduleSegment(TypedDict):
    id: str
    start_time: str
    end_time: str
    title: str
    canceled_until: Optional[str]
    category: Optional[Category]
    is_recurring: bool

class ScheduleVacation(TypedDict):
    start_time: str
    end_time: str

class SchedulePagination(TypedDict):
    cursor: Optional[str]

class ChannelStreamSchedule(BaseBroadcaster):
    segments: List[ScheduleSegment]
    vacation: Optional[ScheduleVacation]
    pagination: SchedulePagination


# Drops Entitlement
class DropsEntitlement(TypedDict):
    id: str
    benefit_id: str
    timestamp: str
    user_id: str
    game_id: str
    fulfillment_status: str
    last_updated: str

class DropsEntitlementUpdate(TypedDict):
    status: str
    ids: List[str]


# Conduit
class Conduit(TypedDict):
    id: str
    shard_count: int


class ConduitShard(TypedDict):
    id: str
    status: str
    transport: Transport

class ConduitShardError(TypedDict):
    id: str
    message: str
    code: str

class UpdateConduitShards(TypedDict):
    data: List[ConduitShard]
    errors: List[ConduitShardError]


class AdSchedule(TypedDict):
    snooze_count: int
    snooze_refresh_at: Optional[str]
    next_ad_at: Optional[str]
    duration: int
    last_ad_at: Optional[str]
    preroll_free_time: int

class AdSnooze(TypedDict):
    snooze_count: int
    snooze_refresh_at: Optional[str]
    next_ad_at: Optional[str]

class AnalyticsReport(TypedDict):
    extension_id: Optional[str]
    game_id: Optional[str]
    URL: str
    type: str
    date_range: Dict[str, str]

class BitsLeaderboardEntry(BaseUser):
    rank: int
    score: int

class Amount(TypedDict):
    value: int
    decimal_places: int
    currency: str

class Charity(TypedDict):
    name: str
    description: str
    logo: str
    website: str

class CharityCampaign(BaseBroadcaster):
    id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: Amount
    target_amount: Optional[Amount]

class CharityDonation(BaseUser):
    id: str
    campaign_id: str
    amount: Amount

class CreatorGoal(BaseBroadcaster):
    id: str
    type: str
    description: str
    is_achieved: bool
    current_amount: int
    target_amount: int
    created_at: str
    updated_at: str

class Contribution(BaseUser):
    type: str
    total: int

class HypeTrainEvent(TypedDict):
    id: str
    event_data: Dict[str, Any]

class AutoModStatusMessage(TypedDict):
    msg_id: str
    msg_text: str

class AutoModSettings(TypedDict):
    broadcaster_id: str
    moderator_id: str
    overall_level: Optional[int]
    aggression: int
    bullying: int
    disability: int
    misogyny: int
    racism: int
    sexism: int
    sexuality_sex_or_gender: int
    swearing: int
    sexual_violence: int
    suicide: int
    other: int

class BannedUser(BaseUser):
    expires_at: Optional[str]
    created_at: str
    reason: str
    moderator_id: str
    moderator_login: str
    moderator_name: str

class UnbanRequest(BaseBroadcaster, BaseUser):
    id: str
    text: str
    status: str
    created_at: str
    resolved_at: Optional[str]
    resolution_text: str
    moderator_id: str
    moderator_login: str
    moderator_name: str

class BlockedTerm(TypedDict):
    broadcaster_id: str
    moderator_id: str
    id: str
    text: str
    created_at: str
    updated_at: Optional[str]
    expires_at: Optional[str]

class Moderator(BaseUser):
    created_at: str

class PollChoice(TypedDict):
    id: str
    title: str
    votes: int
    channel_points_votes: int
    bits_votes: int

class Poll(BaseBroadcaster):
    id: str
    title: str
    choices: List[PollChoice]
    bits_voting_enabled: bool
    bits_per_vote: int
    channel_points_voting_enabled: bool
    channel_points_per_vote: int
    status: str
    duration: int
    started_at: str
    ended_at: Optional[str]

class Outcome(TypedDict):
    id: str
    title: str
    users: int
    channel_points: int
    top_predictors: List[Contribution]
    color: str

class Prediction(BaseBroadcaster):
    id: str
    title: str
    winning_outcome_id: Optional[str]
    outcomes: List[Outcome]
    prediction_window: int
    status: str
    created_at: str
    ended_at: Optional[str]
    locked_at: Optional[str]

class StreamMarker(TypedDict):
    id: str
    created_at: str
    created_by: str
    position_seconds: int
    description: str
    URL: str
    video_id: str
    label: str

class UserSubscription(BaseBroadcaster):
    gifter_id: str
    gifter_login: str
    gifter_name: str
    is_gift: bool
    user_id: str
    user_login: str
    user_name: str
    tier: str

class UserExtension(TypedDict):
    id: str
    version: str
    can_activate: bool
    name: str
    type: List[str]

class ExtensionComponent(TypedDict):
    active: bool
    id: str
    version: str
    name: str
    x: int
    y: int

class ExtensionPanel(TypedDict):
    active: bool
    id: str
    version: str
    name: str

class ExtensionOverlay(TypedDict):
    active: bool
    id: str
    version: str
    name: str

class ActiveUserExtension(TypedDict):
    panel: List[ExtensionPanel]
    overlay: List[ExtensionOverlay]
    component: List[ExtensionComponent]

class SoundtrackTrack(TypedDict):
    id: str
    title: str
    artists: List[str]
    album: str

class SoundtrackPlaylist(TypedDict):
    id: str
    title: str
    image_url: str
    tracks: List[SoundtrackTrack]

class ExtensionTransaction(BaseUser, BaseBroadcaster):
    id: str
    timestamp: str
    product_type: str
    product_data: Dict[str, Any]

class ExtensionBitsProduct(TypedDict):
    sku: str
    cost: Dict[str, Any]
    name: str
    in_development: bool
    display_name: str
    expiration: str
    is_broadcast: bool

class ExtensionLiveChannel(TypedDict):
    broadcaster_id: str
    broadcaster_name: str
    game_name: str
    game_id: str
    title: str

class ExtensionSecret(TypedDict):
    format_version: int
    content: str
    active_at: str
    expires_at: str

class ExtensionConfiguration(TypedDict):
    broadcaster_id: str
    extension_id: str
    segment: str
    version: str
    content: str

class Extension(TypedDict):
    id: str
    version: str
    author_name: str
    bits_enabled: bool
    can_install: bool
    configurations: List[ExtensionConfiguration]
    description: str
    has_chat_support: bool
    icon_url: str
    name: str
    views: List[str]

class FollowedChannel(BaseBroadcaster):
    followed_at: str

class ChannelFollower(BaseUser):
    followed_at: str

class ChannelEditor(TypedDict):
    user_id: str
    user_name: str
    created_at: str

class ShieldModeStatus(TypedDict):
    is_active: bool
    moderator_id: str
    moderator_login: str
    moderator_name: str
    last_activated_at: str

class WarnReason(BaseUser):
    reason: str

class Raid(TypedDict):
    created_at: str
    is_mature: bool

class StreamKey(TypedDict):
    stream_key: str

class UserActiveExtensionUpdate(TypedDict):
    panel: List[ExtensionPanel]
    overlay: List[ExtensionOverlay]
    component: List[ExtensionComponent]

class HypeTrainRecord(TypedDict):
    level: int
    total: int
    achieved_at: str

class CurrentHypeTrain(BaseUserBroadcaster):
    id: str
    level: int
    total: int
    progress: int
    goal: int
    top_contributions: List[Contribution]
    shared_train_participants: Optional[List[BaseUserBroadcaster]]
    started_at: str
    expires_at: str
    type: Literal['treasure', 'golden_kappa', 'regular']

class HypeTrainStatus(TypedDict):
    current: Optional[CurrentHypeTrain]
    all_time_high: Optional[HypeTrainRecord]
    shared_all_time_high: Optional[HypeTrainRecord]
