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

from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING, Any, Tuple, Optional
from .utils import from_iso_string
from types import MappingProxyType
import datetime

if TYPE_CHECKING:
    from .types import helix

__all__ = (
    'UserIdentity', 'Amount',

    # Channel & Stream related
    'ChannelInfo', 'StreamInfo', 'StreamKey', 'ChannelStreamSchedule', 'ScheduleSegment',
    'ScheduleVacation', 'StreamMarker', 'AdSchedule', 'AdSnooze', 'Raid', 'UserSubscription',

    # User & Identity related
    'UserInfo', 'ChannelEditor', 'ChannelVIP', 'Moderator', 'Chatter', 'FollowedChannel',
    'ChannelFollower', 'BannedUser', 'UnbanRequest', 'BlockedTerm',

    # Chat & Moderation
    'ChatSettings', 'SharedChatParticipant', 'SharedChatSession', 'DropReason',
    'SendMessageStatus', 'UserChatColor', 'ChatBadgeSet', 'BadgeVersion', 'AutoModSettings',
    'ShieldModeStatus', 'WarnReason', 'AutoModStatusMessage',

    # Emotes & Cheermotes
    'Cheermote', 'CheermoteTier', 'EmoteImages', 'ChannelEmote', 'GlobalEmote', 'EmoteSet',

    # Extensions
    'Extension', 'ExtensionLiveChannel', 'ExtensionSecret', 'ExtensionConfiguration',
    'UserExtension', 'ActiveUserExtension', 'ExtensionComponent', 'ExtensionPanel',
    'ExtensionOverlay', 'ExtensionTransaction', 'ExtensionBitsProduct',

    # Events & Subscriptions
    'Subscription', 'Conduit', 'ConduitShard', 'ConduitShardError', 'ConduitShardUpdate',

    # Content & Discovery
    'Category', 'Game', 'SearchChannel', 'Clip', 'Video', 'MutedSegment',
    'ContentClassificationLabel', 'AnalyticsReport',

    # Teams
    'TeamInfo', 'ChannelTeam', 'TeamUsers',

    # Monetization
    'StarCommercial', 'BitsLeaderboardEntry', 'Charity', 'CharityCampaign',
    'CharityDonation', 'CreatorGoal', 'Contribution', 'HypeTrainEvent',
    'HypeTrainRecord', 'CurrentHypeTrain', 'HypeTrainStatus',

    # Polls & Predictions
    'Poll', 'PollChoice', 'Prediction', 'Outcome',

    # User Extensions
    'UserActiveExtensionUpdate',


    'DropsEntitlement', 'DropsEntitlementUpdate'
)


class UserIdentity(NamedTuple):
    """
    Represents a user's identity information.

    Attributes
    ----------
    id: str
        Unique identifier for the user.
    login: str
        User's login name.
    name: str
        User's display name.
    """

    id: str
    login: str
    name: str

    def __eq__(self, other: UserIdentity) -> bool:
        if not isinstance(other, UserIdentity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"UserIdentity(id={self.id!r}, login={self.login!r})"

    def __call__(self, *args, **kwargs) -> str:
        return self.id


class StarCommercial(NamedTuple):
    """
    Represents the response from starting a commercial on a Twitch channel.

    Attributes
    ----------
    length: int
        The length of the commercial that was requested, in seconds.
        If a commercial longer than 180 seconds was requested, this will be 180.
    message: str
        A message indicating whether Twitch was able to serve an ad.
    retry_after: int
        The number of seconds you must wait before running another commercial.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    length: int
    message: str
    retry_after: int
    raw: helix.StarCommercial

    @classmethod
    def from_data(cls, data: helix.StarCommercial) -> StarCommercial:
        return cls(
            length=data['length'],
            message=data['message'],
            retry_after=data['retry_after'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StarCommercial(length={self.length}, message={self.message!r}, retry_after={self.retry_after})"


class CheermoteTier(NamedTuple):
    """
    Represents a tier level for a Cheermote.

    Attributes
    ----------
    min_bits: int
        The minimum number of Bits that you must cheer at this tier level.
        The maximum is determined by the next tier's min_bits minus 1.
    id: str
        The tier level ID. Possible values: "1", "100", "500", "1000", "5000", "10000", "100000".
    color: str
        The hex code of the color associated with this tier level (e.g., "#979797").
    images: MappingProxyType[str, Any]
        The animated and static image sets organized by theme, format, and size.
        Contains 'dark' and 'light' themes with 'animated' and 'static' formats.
    can_cheer: bool
        Whether users can cheer at this tier level.
    show_in_bits_card: bool
        Whether this tier level is shown in the Bits card.
    """

    min_bits: int
    id: str
    color: str
    images: MappingProxyType[str, Any]
    can_cheer: bool
    show_in_bits_card: bool

    @classmethod
    def from_data(cls, data: helix.CheermoteTier) -> CheermoteTier:
        return cls(
            min_bits=data['min_bits'],
            id=data['id'],
            color=data['color'],
            images=MappingProxyType(data['images']),
            can_cheer=data['can_cheer'],
            show_in_bits_card=data['show_in_bits_card']
        )

    def __repr__(self) -> str:
        return f"CheermoteTier(min_bits={self.min_bits}, id={self.id!r}, color={self.color!r})"


class Cheermote(NamedTuple):
    """
    Represents a single Cheermote object.

    Attributes
    ----------
    prefix: str
        The name portion of the Cheermote string used in chat to cheer Bits.
        Combined with number of Bits to form full Cheermote string (e.g., "Cheer100").
    tiers: Tuple[CheermoteTier, ...]
        A tuple of tier levels that the Cheermote supports, each with its own
        Bits range and associated imagery.
    type: str
        The type of Cheermote. Possible values:
        - "global_first_party": Twitch-defined, shown in Bits card
        - "global_third_party": Twitch-defined, not shown in Bits card
        - "channel_custom": Broadcaster-defined Cheermote
        - "display_only": Internal use only
        - "sponsored": Sponsor-defined with additional Bits contribution
    order: int
        The display order in the Bits card. Numbers may not be consecutive
        and are unique within each Cheermote type.
    last_updated: datetime.datetime
        The date and time in RFC3339 format when this Cheermote was last updated.
    is_charitable: bool
        Whether this Cheermote provides a charitable contribution match during campaigns.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    prefix: str
    tiers: Tuple[CheermoteTier, ...]
    type: str
    order: int
    last_updated: datetime.datetime
    is_charitable: bool
    raw: helix.Cheermote

    @classmethod
    def from_data(cls, data: helix.Cheermote) -> Cheermote:
        return cls(
            prefix=data['prefix'],
            tiers=tuple(CheermoteTier.from_data(tier) for tier in data['tiers']),
            type=data['type'],
            order=data['order'],
            last_updated=from_iso_string(data['last_updated']),
            is_charitable=data['is_charitable'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Cheermote(prefix={self.prefix!r}, type={self.type!r}, order={self.order})"


class EmoteImages(NamedTuple):
    """
    Represents the image URLs for an emote at different sizes.

    Attributes
    ----------
    url_1x: str
        A URL to the small version (28px x 28px) of the emote.
    url_2x: str
        A URL to the medium version (56px x 56px) of the emote.
    url_4x: str
        A URL to the large version (112px x 112px) of the emote.
    """

    url_1x: str
    url_2x: str
    url_4x: str

    @classmethod
    def from_data(cls, data: helix.EmoteImages) -> EmoteImages:
        return cls(
            url_1x=data['url_1x'],
            url_2x=data['url_2x'],
            url_4x=data['url_4x']
        )

    def __repr__(self) -> str:
        return f"EmoteImages(url_1x={self.url_1x!r}, url_2x={self.url_2x!r}, url_4x={self.url_4x!r})"


class ChannelEmote(NamedTuple):
    """
    Represents a channel-specific custom emote.

    Attributes
    ----------
    id: str
        An ID that identifies this emote.
    name: str
        The name of the emote that viewers type in chat to display it.
    images: EmoteImages
        The image URLs for the emote at different sizes.
    tier: str
        The subscriber tier at which the emote is unlocked.
        Empty string if emote_type is not 'subscriptions'.
    emote_type: str
        The type of emote. Possible values:
        - "bitstier": A custom Bits tier emote
        - "follower": A custom follower emote
        - "subscriptions": A custom subscriber emote
    emote_set_id: str
        An ID that identifies the emote set that the emote belongs to.
    format: Tuple[str, ...]
        The formats that the emote is available in ("static", "animated").
    scale: Tuple[str, ...]
        The sizes that the emote is available in ("1.0", "2.0", "3.0").
    theme_mode: Tuple[str, ...]
        The background themes that the emote is available in ("light", "dark").
    template: str
        A templated URL for generating CDN URLs for this emote.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    name: str
    images: EmoteImages
    tier: str
    emote_type: str
    emote_set_id: str
    format: Tuple[str, ...]
    scale: Tuple[str, ...]
    theme_mode: Tuple[str, ...]
    template: str
    raw: helix.ChannelEmote

    @classmethod
    def from_data(cls, data: helix.ChannelEmote, template: str) -> ChannelEmote:
        return cls(
            id=data['id'],
            name=data['name'],
            images=EmoteImages.from_data(data['images']),
            tier=data['tier'],
            emote_type=data['emote_type'],
            emote_set_id=data['emote_set_id'],
            format=tuple(data['format']),
            scale=tuple(data['scale']),
            theme_mode=tuple(data['theme_mode']),
            template=template,
            raw=MappingProxyType(data)  # type: ignore
        )

    def get_url(self, emote_format: str, theme_mode: str, scale: str) -> str:
        """
        Generate a CDN URL for this emote using the template.

        Parameters
        ----------
        emote_format: str
            The format to use ("static" or "animated"). Must be in self.format.
        theme_mode: str
            The theme mode to use ("light" or "dark"). Must be in self.theme_mode.
        scale: str
            The scale to use ("1.0", "2.0", or "3.0"). Must be in self.scale.

        Returns
        -------
        str
            The generated CDN URL for the emote.

        Raises
        ------
        ValueError
            If the provided parameters are not available for this emote.
        """
        if emote_format not in self.format:
            raise ValueError(f"Format '{emote_format}' not available. Available: {self.format}")
        if theme_mode not in self.theme_mode:
            raise ValueError(f"Theme mode '{theme_mode}' not available. Available: {self.theme_mode}")
        if scale not in self.scale:
            raise ValueError(f"Scale '{scale}' not available. Available: {self.scale}")

        return self.template.replace(
            "{{id}}", self.id).replace("{{format}}",
                                       emote_format).replace("{{theme_mode}}",
                                                             theme_mode).replace("{{scale}}", scale)

    def __repr__(self) -> str:
        return f"ChannelEmote(id={self.id!r}, name={self.name!r}, emote_type={self.emote_type!r})"


class GlobalEmote(NamedTuple):
    """
    Represents a global Twitch emote available in all channels.

    Attributes
    ----------
    id: str
        An ID that identifies this emote.
    name: str
        The name of the emote that viewers type in chat to display it.
    images: EmoteImages
        The image URLs for the emote at different sizes.
    format: Tuple[str, ...]
        The formats that the emote is available in ("static", "animated").
    scale: Tuple[str, ...]
        The sizes that the emote is available in ("1.0", "2.0", "3.0").
    theme_mode: Tuple[str, ...]
        The background themes that the emote is available in ("light", "dark").
    template: str
        A templated URL for generating CDN URLs for this emote.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    name: str
    images: EmoteImages
    format: Tuple[str, ...]
    scale: Tuple[str, ...]
    theme_mode: Tuple[str, ...]
    template: str
    raw: helix.GlobalEmote

    @classmethod
    def from_data(cls, data: helix.GlobalEmote, template: str) -> GlobalEmote:
        return cls(
            id=data['id'],
            name=data['name'],
            images=EmoteImages.from_data(data['images']),
            format=tuple(data['format']),
            scale=tuple(data['scale']),
            theme_mode=tuple(data['theme_mode']),
            template=template,
            raw=MappingProxyType(data)  # type: ignore
        )

    def get_url(self, emote_format: str, theme_mode: str, scale: str) -> str:
        """
        Generate a CDN URL for this emote using the template.

        Parameters
        ----------
        emote_format: str
            The format to use ("static" or "animated"). Must be in self.format.
        theme_mode: str
            The theme mode to use ("light" or "dark"). Must be in self.theme_mode.
        scale: str
            The scale to use ("1.0", "2.0", or "3.0"). Must be in self.scale.

        Returns
        -------
        str
            The generated CDN URL for the emote.

        Raises
        ------
        ValueError
            If the provided parameters are not available for this emote.
        """
        if emote_format not in self.format:
            raise ValueError(f"Format '{emote_format}' not available. Available: {self.format}")
        if theme_mode not in self.theme_mode:
            raise ValueError(f"Theme mode '{theme_mode}' not available. Available: {self.theme_mode}")
        if scale not in self.scale:
            raise ValueError(f"Scale '{scale}' not available. Available: {self.scale}")

        return self.template.replace(
            "{{id}}", self.id).replace("{{format}}",
                                       emote_format).replace("{{theme_mode}}",
                                                             theme_mode).replace("{{scale}}", scale)

    def __repr__(self) -> str:
        return f"GlobalEmote(id={self.id!r}, name={self.name!r})"


class EmoteSet(NamedTuple):
    """
    Represents an emote from a specific emote set.

    Attributes
    ----------
    id: str
        An ID that uniquely identifies this emote.
    name: str
        The name of the emote that viewers type in chat to display it.
    images: EmoteImages
        The image URLs for the emote at different sizes.
    emote_type: str
        The type of emote. Possible values:
        - "bitstier": A Bits tier emote
        - "follower": A follower emote
        - "subscriptions": A subscriber emote
    emote_set_id: str
        An ID that identifies the emote set that the emote belongs to.
    owner_id: str
        The ID of the broadcaster who owns the emote.
    format: Tuple[str, ...]
        The formats that the emote is available in ("static", "animated").
    scale: Tuple[str, ...]
        The sizes that the emote is available in ("1.0", "2.0", "3.0").
    theme_mode: Tuple[str, ...]
        The background themes that the emote is available in ("light", "dark").
    template: str
        A templated URL for generating CDN URLs for this emote.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    name: str
    images: EmoteImages
    emote_type: str
    emote_set_id: str
    owner_id: str
    format: Tuple[str, ...]
    scale: Tuple[str, ...]
    theme_mode: Tuple[str, ...]
    template: str
    raw: helix.EmoteSet

    @classmethod
    def from_data(cls, data: helix.EmoteSet, template: str) -> EmoteSet:
        return cls(
            id=data['id'],
            name=data['name'],
            images=EmoteImages.from_data(data['images']),
            emote_type=data['emote_type'],
            emote_set_id=data['emote_set_id'],
            owner_id=data['owner_id'],
            format=tuple(data['format']),
            scale=tuple(data['scale']),
            theme_mode=tuple(data['theme_mode']),
            template=template,
            raw=MappingProxyType(data)  # type: ignore
        )

    def get_url(self, emote_format: str, theme_mode: str, scale: str) -> str:
        """
        Generate a CDN URL for this emote using the template.

        Parameters
        ----------
        emote_format: str
            The format to use ("static" or "animated"). Must be in self.format.
        theme_mode: str
            The theme mode to use ("light" or "dark"). Must be in self.theme_mode.
        scale: str
            The scale to use ("1.0", "2.0", or "3.0"). Must be in self.scale.

        Returns
        -------
        str
            The generated CDN URL for the emote.

        Raises
        ------
        ValueError
            If the provided parameters are not available for this emote.
        """
        if emote_format not in self.format:
            raise ValueError(f"Format '{emote_format}' not available. Available: {self.format}")
        if theme_mode not in self.theme_mode:
            raise ValueError(f"Theme mode '{theme_mode}' not available. Available: {self.theme_mode}")
        if scale not in self.scale:
            raise ValueError(f"Scale '{scale}' not available. Available: {self.scale}")

        return self.template.replace(
            "{{id}}", self.id).replace("{{format}}",
                                       emote_format).replace("{{theme_mode}}",
                                                             theme_mode).replace("{{scale}}", scale)

    def __repr__(self) -> str:
        return f"EmoteSetEmote(id={self.id!r}, name={self.name!r}, owner_id={self.owner_id!r})"


class BadgeVersion(NamedTuple):
    """
    Represents a version of a chat badge.

    Attributes
    ----------
    id: str
        An ID that identifies this version of the badge.
    image_url_1x: str
        A URL to the small version (18px x 18px) of the badge.
    image_url_2x: str
        A URL to the medium version (36px x 36px) of the badge.
    image_url_4x: str
        A URL to the large version (72px x 72px) of the badge.
    title: str
        The title of the badge.
    description: str
        The description of the badge.
    click_action: Optional[str]
        The action to take when clicking on the badge. None if no action is specified.
    click_url: Optional[str]
        The URL to navigate to when clicking on the badge. None if no URL is specified.
    """

    id: str
    image_url_1x: str
    image_url_2x: str
    image_url_4x: str
    title: str
    description: str
    click_action: Optional[str]
    click_url: Optional[str]

    @classmethod
    def from_data(cls, data: helix.BadgeVersion) -> BadgeVersion:
        return cls(
            id=data['id'],
            image_url_1x=data['image_url_1x'],
            image_url_2x=data['image_url_2x'],
            image_url_4x=data['image_url_4x'],
            title=data['title'],
            description=data['description'],
            click_action=data.get('click_action'),
            click_url=data.get('click_url')
        )

    def __repr__(self) -> str:
        return f"BadgeVersion(id={self.id!r}, title={self.title!r})"


class ChatBadgeSet(NamedTuple):
    """
    Represents a set of chat badges.

    Attributes
    ----------
    set_id: str
        An ID that identifies this set of chat badges (e.g., "bits", "subscriber").
    versions: Tuple[BadgeVersion, ...]
        The list of chat badges in this set.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    set_id: str
    versions: Tuple[BadgeVersion, ...]
    raw: helix.ChatBadgeSet

    @classmethod
    def from_data(cls, data: helix.ChatBadgeSet) -> ChatBadgeSet:
        return cls(
            set_id=data['set_id'],
            versions=tuple(BadgeVersion.from_data(version) for version in data['versions']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChatBadgeSet(set_id={self.set_id!r})"


class ChatSettings(NamedTuple):
    """
    Represents a broadcaster's chat settings.

    Attributes
    ----------
    broadcaster_id: str
        The ID of the broadcaster whose chat settings these are.
    emote_mode: bool
        Whether chat messages must contain only emotes.
    follower_mode: bool
        Whether the broadcaster restricts the chat room to followers only.
    follower_mode_duration: Optional[int]
        The length of time, in minutes, that users must follow the broadcaster
        before being able to participate in the chat room. Is None if follower_mode is False.
    moderator_id: Optional[str]
        The moderator's ID. Only included if the request specified a user access token
        with the moderator:read:chat_settings scope.
    non_moderator_chat_delay: Optional[bool]
        Whether the broadcaster adds a short delay before chat messages appear in the chat room.
        Only included if the request includes appropriate moderator scope.
    non_moderator_chat_delay_duration: Optional[int]
        The amount of time, in seconds, that messages are delayed before appearing in chat.
        Is None if non_moderator_chat_delay is False.
    slow_mode: bool
        Whether the broadcaster limits how often users in the chat room are allowed
        to send messages.
    slow_mode_wait_time: Optional[int]
        The amount of time, in seconds, that users must wait between sending messages.
        Is None if slow_mode is False.
    subscriber_mode: bool
        Whether only users that subscribe to the broadcaster's channel may talk
        in the chat room.
    unique_chat_mode: bool
        Whether the broadcaster requires users to post only unique messages
        in the chat room.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_id: str
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration: Optional[int]
    moderator_id: Optional[str]
    non_moderator_chat_delay: Optional[bool]
    non_moderator_chat_delay_duration: Optional[int]
    slow_mode: bool
    slow_mode_wait_time: Optional[int]
    subscriber_mode: bool
    unique_chat_mode: bool
    raw: helix.ChatSettings

    @classmethod
    def from_data(cls, data: helix.ChatSettings) -> ChatSettings:
        return cls(
            broadcaster_id=data['broadcaster_id'],
            emote_mode=data['emote_mode'],
            follower_mode=data['follower_mode'],
            follower_mode_duration=data['follower_mode_duration'],
            moderator_id=data.get('moderator_id'),
            non_moderator_chat_delay=data.get('non_moderator_chat_delay'),
            non_moderator_chat_delay_duration=data.get('non_moderator_chat_delay_duration'),
            slow_mode=data['slow_mode'],
            slow_mode_wait_time=data['slow_mode_wait_time'],
            subscriber_mode=data['subscriber_mode'],
            unique_chat_mode=data['unique_chat_mode'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChatSettings(broadcaster_id={self.broadcaster_id!r})"


class SharedChatParticipant(NamedTuple):
    """
    Represents a participant in a shared chat session.

    Attributes
    ----------
    broadcaster_id: str
        The User ID of the participant channel.
    """

    broadcaster_id: str

    @classmethod
    def from_data(cls, data: helix.SharedChatParticipant) -> SharedChatParticipant:
        return cls(broadcaster_id=data['broadcaster_id'])

    def __repr__(self) -> str:
        return f"SharedChatParticipant(broadcaster_id={self.broadcaster_id!r})"


class SharedChatSession(NamedTuple):
    """
    Represents an active shared chat session for a channel.

    Attributes
    ----------
    session_id: str
        The unique identifier for the shared chat session.
    host_broadcaster_id: str
        The User ID of the host channel.
    participants: Tuple[SharedChatParticipant, ...]
        The list of participants in the session.
    created_at: datetime.datetime
        The UTC datetime for when the session was created.
    updated_at: datetime.datetime
        The UTC datetime for when the session was last updated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    session_id: str
    host_broadcaster_id: str
    participants: Tuple[SharedChatParticipant, ...]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    raw: helix.SharedChatSession

    @classmethod
    def from_data(cls, data: helix.SharedChatSession) -> SharedChatSession:
        return cls(
            session_id=data['session_id'],
            host_broadcaster_id=data['host_broadcaster_id'],
            participants=tuple(SharedChatParticipant.from_data(participant) for participant in data['participants']),
            created_at=from_iso_string(data['created_at']),
            updated_at=from_iso_string(data['updated_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"SharedChatSession(session_id={self.session_id!r}, host_broadcaster_id={self.host_broadcaster_id!r})"


class DropReason(NamedTuple):
    """
    Represents the reason a chat message was dropped.

    Attributes
    ----------
    code: str
        Code for why the message was dropped.
    message: str
        Message for why the message was dropped.
    """

    code: str
    message: str

    @classmethod
    def from_data(cls, data: helix.MessageDropReason) -> DropReason:
        return cls(
            code=data['code'],
            message=data['message']
        )

    def __repr__(self) -> str:
        return f"DropReason(code={self.code!r}, message={self.message!r})"


class SendMessageStatus(NamedTuple):
    """
    Represents the response from sending a chat message.

    Attributes
    ----------
    message_id: str
        The message id for the message that was sent.
    is_sent: bool
        If the message passed all checks and was sent.
    drop_reason: Optional[DropReason]
        The reason the message was dropped, if any.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    message_id: str
    is_sent: bool
    drop_reason: Optional[DropReason]
    raw: helix.SendMessageStatus

    @classmethod
    def from_data(cls, data: helix.SendMessageStatus) -> SendMessageStatus:
        return cls(
            message_id=data['message_id'],
            is_sent=data['is_sent'],
            drop_reason=DropReason.from_data(data['drop_reason']) if data.get('drop_reason') else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: SendMessageStatus) -> bool:
        if isinstance(other, SendMessageStatus):
            return self.message_id == other.message_id
        return False

    def __repr__(self) -> str:
        return f"SendChatMessageResponse(message_id={self.message_id!r}, is_sent={self.is_sent!r})"


class UserChatColor(NamedTuple):
    """
    Represents a user's chat color.

    Attributes
    ----------
    identity: UserIdentity
        The user information.
    color: str
        The Hex color code that the user uses in chat for their name.
        If the user hasn't specified a color in their settings, the string is empty.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    identity: UserIdentity
    color: str
    raw: helix.UserChatColor

    @classmethod
    def from_data(cls, data: helix.UserChatColor) -> UserChatColor:
        return cls(
            identity=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            color=data['color'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"UserChatColor(identity={self.identity!r}, color={self.color!r})"


class ChannelInfo(NamedTuple):
    """
    Represents a channel's information.

    Attributes
    ----------
    identity: UserIdentity
        The broadcaster's information.
    broadcaster_language: str
        The broadcaster's preferred language. The value is an ISO 639-1 two-letter
        language code (for example, 'en' for English). The value is set to "other"
        if the language is not a Twitch supported language.
    game_name: str
        The name of the game that the broadcaster is playing or last played.
        The value is an empty string if the broadcaster has never played a game.
    category_id: str
        An ID that uniquely identifies the game that the broadcaster is playing
        or last played. The value is an empty string if the broadcaster has never
        played a game.
    title: str
        The title of the stream that the broadcaster is currently streaming or
        last streamed. The value is an empty string if the broadcaster has never
        streamed.
    delay: int
        The value of the broadcaster's stream delay setting, in seconds. This field's
        value defaults to zero unless 1) the request specifies a user access token,
        2) the ID in the broadcaster_id query parameter matches the user ID in the
        access token, and 3) the broadcaster has partner status, and they set a
        non-zero stream delay value.
    tags: Tuple[str, ...]
        The tags applied to the channel.
    content_classification_labels: Tuple[str, ...]
        The CCLs applied to the channel.
    is_branded_content: bool
        Boolean flag indicating if the channel has branded content.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    identity: UserIdentity
    broadcaster_language: str
    game_name: str
    category_id: str
    title: str
    delay: int
    tags: Tuple[str, ...]
    content_classification_labels: Tuple[str, ...]
    is_branded_content: bool
    raw: helix.ChannelInformation

    @classmethod
    def from_data(cls, data: helix.ChannelInformation) -> ChannelInfo:
        return cls(
            identity=UserIdentity(
                id=data['broadcaster_id'],
                login=data['broadcaster_login'],
                name=data['broadcaster_name']
            ),
            broadcaster_language=data['broadcaster_language'],
            game_name=data['game_name'],
            category_id=data['game_id'],
            title=data['title'],
            delay=data['delay'],
            tags=tuple(data['tags']),
            content_classification_labels=tuple(data['content_classification_labels']),
            is_branded_content=data['is_branded_content'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelInfo(identity={self.identity!r})"


class TeamInfo(NamedTuple):
    """
    Represents a team's information.

    Attributes
    ----------
    id: str
        An ID that uniquely identifies the team.
    team_name: str
        The team's name.
    team_display_name: str
        The team's display name.
    info: str
        The team's information/description.
    thumbnail_url: str
        A URL to the team's thumbnail image.
    banner: Optional[str]
        A URL to the team's banner image. None if no banner is set.
    background_image_url: Optional[str]
        A URL to the team's background image. None if no background image is set.
    created_at: datetime.datetime
        The UTC date and time of when the team was created.
    updated_at: datetime.datetime
        The UTC date and time of when the team was last updated.
    """

    id: str
    team_name: str
    team_display_name: str
    info: str
    thumbnail_url: str
    banner: Optional[str]
    background_image_url: Optional[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def __repr__(self) -> str:
        return f"TeamInfo(id={self.id!r}, team_name={self.team_name!r})"


class ChannelTeam(NamedTuple):
    """
    Represents a channel team's information.

    Attributes
    ----------
    team: TeamInfo
        The team's information.
    identity: UserIdentity
        The broadcaster's information.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    team: TeamInfo
    identity: UserIdentity
    raw: helix.ChannelTeam

    @classmethod
    def from_data(cls, data: helix.ChannelTeam) -> ChannelTeam:
        return cls(
            team=TeamInfo(
                id=data['id'],
                team_name=data['team_name'],
                team_display_name=data['team_display_name'],
                info=data['info'],
                thumbnail_url=data['thumbnail_url'],
                banner=data.get('banner'),
                background_image_url=data.get('background_image_url'),
                created_at=from_iso_string(data['created_at']),
                updated_at=from_iso_string(data['updated_at']),
            ),
            identity=UserIdentity(
                id=data['broadcaster_id'],
                login=data['broadcaster_login'],
                name=data['broadcaster_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelTeam(team={self.team!r}, identity={self.identity!r})"


class TeamUsers(NamedTuple):
    """
    Represents a collection of team users.

    Attributes
    ----------
    team: TeamInfo
        The team's information.
    users: Tuple[BaseUser, ...]
        A tuple of users that belong to the team.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    team: TeamInfo
    users: Tuple[UserIdentity, ...]
    raw: helix.TeamUsers

    @classmethod
    def from_data(cls, data: helix.TeamUsers) -> TeamUsers:
        return cls(
            team=TeamInfo(
                id=data['id'],
                team_name=data['team_name'],
                team_display_name=data['team_display_name'],
                info=data['info'],
                thumbnail_url=data['thumbnail_url'],
                banner=data.get('banner'),
                background_image_url=data.get('background_image_url'),
                created_at=from_iso_string(data['created_at']),
                updated_at=from_iso_string(data['updated_at']),
            ),
            users=tuple(UserIdentity(user['user_id'], user['user_login'], user['user_name']) for user in data['users']),
            raw=MappingProxyType(data)  # type: ignore
        )

    @property
    def total_users(self) -> int:
        """Returns the total number of users in the team."""
        return len(self.users)

    def __repr__(self) -> str:
        return f"TeamUsers(team={self.team!r}, total_users={self.total_users})"


class UserInfo(NamedTuple):
    """
    Represents user information.

    Attributes
    ----------
    identity: UserIdentity
        The user identity.
    type: str
        The type of user. Possible values are:
        - "admin" — Twitch administrator
        - "global_mod"
        - "staff" — Twitch staff
        - "" — Normal user
    broadcaster_type: str
        The type of broadcaster. Possible values are:
        - "affiliate" — An affiliate broadcaster
        - "partner" — A partner broadcaster
        - "" — A normal broadcaster
    description: str
        The user's description of their channel.
    profile_image_url: str
        A URL to the user's profile image.
    offline_image_url: str
        A URL to the user's offline image.
    email: Optional[str]
        The user's verified email address. Only included if the user access token
        includes the user:read:email scope.
    created_at: datetime
        The UTC date and time that the user's account was created.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    identity: UserIdentity
    type: str
    broadcaster_type: str
    description: str
    profile_image_url: str
    offline_image_url: str
    email: Optional[str]
    created_at: datetime.datetime
    raw: helix.UserInfo

    @classmethod
    def from_data(cls, data: helix.UserInfo) -> UserInfo:
        return cls(
            identity=UserIdentity(
                id=data['id'],
                login=data['login'],
                name=data['display_name']
            ),
            type=data['type'],
            broadcaster_type=data['broadcaster_type'],
            description=data['description'],
            profile_image_url=data['profile_image_url'],
            offline_image_url=data['offline_image_url'],
            email=data.get('email'),
            created_at=from_iso_string(data['created_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"User(identity={self.identity!r} type={self.type!r})"


class Category(NamedTuple):
    """
    Represents a Twitch category from search results.

    Attributes
    ----------
    id: str
        An ID that uniquely identifies the game or category.
    name: str
        The name of the game or category.
    box_art_url: Optional[str]
        A URL to an image of the game's box art or streaming category.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    name: str
    box_art_url: Optional[str]
    raw: helix.Category

    @classmethod
    def from_data(cls, data: helix.Category) -> Category:
        return cls(
            id=data['id'],
            name=data['name'],
            box_art_url=data.get('box_art_url'),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Category):
            return self.id == other.id
        return False


class Game(NamedTuple):
    """
    Represents a Twitch game.

    Attributes
    ----------
    category: Category
        The category information for this game including id, name, and box_art_url.
    igdb_id: str
        The ID that IGDB uses to identify this game. If the IGDB ID is not
        available to Twitch, this field is set to an empty string.
    raw: helix.Game
        The original game data from the API.
    """

    category: Category
    igdb_id: str
    raw: helix.Game

    @classmethod
    def from_data(cls, data: helix.Game) -> Game:
        category = Category.from_data({
            'id': data['id'],
            'name': data['name'],
            'box_art_url': data['box_art_url']
        })
        return cls(
            category=category,
            igdb_id=data['igdb_id'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Game(igdb_id={self.igdb_id!r}, category={self.category!r})"

    def __eq__(self, other: Game) -> bool:
        if isinstance(other, Game):
            return self.igdb_id == other.igdb_id
        return False


class SearchChannel(NamedTuple):
    """
    Represents a Twitch channel from search results.

    Attributes
    ----------
    identity: UserIdentity
        The broadcaster's identity information including id, login, and display name.
    broadcaster_language: str
        The ISO 639-1 two-letter language code of the language used by the broadcaster.
        For example, "en" for English. If the broadcaster uses a language not in the
        list of supported stream languages, the value is "other".
    category: Category
        The category/game information that the broadcaster is playing or last played.
    is_live: bool
        A Boolean value that determines whether the broadcaster is streaming live.
        Is True if the broadcaster is streaming live; otherwise, False.
    tags: Tuple[str, ...]
        The tags applied to the channel.
    thumbnail_url: str
        A URL to a thumbnail of the broadcaster's profile image.
    title: str
        The stream's title. Is an empty string if the broadcaster didn't set it.
    started_at: Optional[datetime]
        The UTC datetime of when the broadcaster started streaming.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    identity: UserIdentity
    broadcaster_language: str
    category: Category
    is_live: bool
    tags: Tuple[str, ...]
    thumbnail_url: str
    title: str
    started_at: Optional[str]
    raw: helix.SearchChannel

    @classmethod
    def from_data(cls, data: helix.SearchChannel) -> SearchChannel:
        user = UserIdentity(
            id=data['id'],
            login=data['broadcaster_login'],
            name=data['display_name']
        )
        category = Category.from_data({
            'id': data['game_id'],
            'name': data['game_name'],
            'box_art_url': None  # Not provided.
        })
        return cls(
            identity=user,
            broadcaster_language=data['broadcaster_language'],
            category=category,
            is_live=data['is_live'],
            tags=tuple(data['tags']),
            thumbnail_url=data['thumbnail_url'],
            title=data['title'],
            started_at=from_iso_string(data['started_at']) if data['started_at'] else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"SearchChannel(identity={self.identity!r}, is_live={self.is_live})"


class Clip(NamedTuple):
    """
    Represents a Twitch clip.

    Attributes
    ----------
    id: str
        An ID that uniquely identifies the clip.
    url: str
        A URL to the clip.
    embed_url: str
        A URL that you can use in an iframe to embed the clip.
    broadcaster: UserIdentity
        The broadcaster that the video was clipped from.
    creator: UserIdentity
        The user that created the clip.
    video_id: str
        An ID that identifies the video that the clip came from. This field
        contains an empty string if the video is not available.
    category_id: str
        The category/game ID that was being played when the clip was created.
    language: str
        The ISO 639-1 two-letter language code that the broadcaster broadcasts in.
        For example, "en" for English. The value is "other" if the broadcaster
        uses a language that Twitch doesn't support.
    title: str
        The title of the clip.
    view_count: int
        The number of times the clip has been viewed.
    created_at: datetime
        The datetime when the clip was created.
    thumbnail_url: str
        A URL to a thumbnail image of the clip.
    duration: float
        The length of the clip, in seconds. Precision is 0.1.
    vod_offset: Optional[int]
        The zero-based offset, in seconds, to where the clip starts in the video (VOD).
        Is None if the video is not available or hasn't been created yet from the live stream.
    is_featured: bool
        A Boolean value that indicates if the clip is featured or not.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    url: str
    embed_url: str
    broadcaster: UserIdentity
    creator: UserIdentity
    video_id: str
    category_id: str
    language: str
    title: str
    view_count: int
    created_at: datetime.datetime
    thumbnail_url: str
    duration: float
    vod_offset: Optional[int]
    is_featured: bool
    raw: helix.Clip

    @classmethod
    def from_data(cls, data: helix.Clip) -> Clip:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_name'].lower(),
            name=data['broadcaster_name']
        )
        creator = UserIdentity(
            id=data['creator_id'],
            login=data['creator_name'].lower(),
            name=data['creator_name']
        )
        return cls(
            id=data['id'],
            url=data['url'],
            embed_url=data['embed_url'],
            broadcaster=broadcaster,
            creator=creator,
            video_id=data['video_id'],
            category_id=data['game_id'],
            language=data['language'],
            title=data['title'],
            view_count=data['view_count'],
            created_at=from_iso_string(data['created_at']),
            thumbnail_url=data['thumbnail_url'],
            duration=data['duration'],
            vod_offset=data['vod_offset'],
            is_featured=data['is_featured'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Clip(id={self.id!r}, title={self.title!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Clip):
            return self.id == other.id
        return False


class MutedSegment(NamedTuple):
    """
    Represents a muted segment in a video.

    Attributes
    ----------
    duration: int
        The duration of the muted segment, in seconds.
    offset: int
        The offset, in seconds, from the beginning of the video to where the muted segment begins.
    """
    duration: int
    offset: int


class Video(NamedTuple):
    """
    Represents a Twitch video.

    Attributes
    ----------
    id: str
        An ID that identifies the video.
    stream_id: Optional[str]
        The ID of the stream that the video originated from if the video's type
        is "archive" otherwise, None.
    user: UserIdentity
        The broadcaster that owns the video.
    title: str
        The video's title.
    description: str
        The video's description.
    created_at: datetime.datetime
        The datetime when the video was created.
    published_at: datetime.datetime
        The datetime when the video was published.
    url: str
        The video's URL.
    thumbnail_url: str
        A URL to a thumbnail image of the video. Replace %{width} and %{height}
        placeholders with desired dimensions (must be 320x180).
    viewable: str
        The video's viewable state. Always set to "public".
    view_count: int
        The number of times that users have watched the video.
    language: str
        The ISO 639-1 two-letter language code that the video was broadcast in.
        The value is "other" if the language is not supported.
    type: str
        The video's type. Possible values: "archive", "highlight", "upload".
    duration: str
        The video's length in ISO 8601 duration format (e.g., "3m21s").
    muted_segments: tuple[MutedSegment, ...]
        The segments that Twitch Audio Recognition muted
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    stream_id: Optional[str]
    user: UserIdentity
    title: str
    description: str
    created_at: datetime.datetime
    published_at: datetime.datetime
    url: str
    thumbnail_url: str
    viewable: str
    view_count: int
    language: str
    type: str
    duration: str
    muted_segments: tuple[MutedSegment, ...]
    raw: helix.Video

    @classmethod
    def from_data(cls, data: helix.Video) -> Video:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'].lower(),
            name=data['user_name']
        )

        muted_segments = ()
        if data.get('muted_segments'):
            muted_segments = tuple(
                MutedSegment(duration=segment['duration'], offset=segment['offset'])
                for segment in data['muted_segments']
            )
        thumbnail_url = data['thumbnail_url'].replace("%{width}", "320").replace(
            "%{height}", "180")
        return cls(
            id=data['id'],
            stream_id=data.get('stream_id'),
            user=user,
            title=data['title'],
            description=data['description'],
            created_at=from_iso_string(data['created_at']),
            published_at=from_iso_string(data['published_at']),
            url=data['url'],
            thumbnail_url=thumbnail_url,
            viewable=data['viewable'],
            view_count=data['view_count'],
            language=data['language'],
            type=data['type'],
            duration=data['duration'],
            muted_segments=muted_segments,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Video(id={self.id!r}, title={self.title!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Video):
            return self.id == other.id
        return False


class StreamInfo(NamedTuple):
    """
    Represents a Twitch stream.

    Attributes
    ----------
    identity: UserIdentity
        The broadcaster's identity information including id, login, and display name.
    category: Category
        The category/game information that the broadcaster is streaming.
    type: str
        The type of stream. Possible values are: live.
        If an error occurs, this field is set to an empty string.
    title: str
        The stream's title. Is an empty string if not set.
    tags: Tuple[str, ...]
        The tags applied to the stream.
    viewer_count: int
        The number of users watching the stream.
    started_at: Optional[datetime]
        The UTC datetime of when the broadcast began.
    language: str
        The language that the stream uses. This is an ISO 639-1 two-letter language code
        or "other" if the stream uses a language not in the list of supported stream languages.
    thumbnail_url: str
        A URL to an image of a frame from the last 5 minutes of the stream.
        Replace the width and height placeholders in the URL ({width}x{height})
        with the size of the image you want, in pixels.
    is_mature: bool
        A Boolean value that indicates whether the stream is meant for mature audiences.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    identity: UserIdentity
    category: Category
    type: str
    title: str
    tags: Tuple[str, ...]
    viewer_count: int
    started_at: Optional[datetime]
    language: str
    thumbnail_url: str
    is_mature: bool
    raw: helix.StreamInfo

    @classmethod
    def from_data(cls, data: helix.StreamInfo) -> StreamInfo:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        category = Category.from_data({
            'id': data['game_id'],
            'name': data['game_name'],
            'box_art_url': None  # Not provided.
        })
        return cls(
            identity=user,
            category=category,
            type=data['type'],
            title=data['title'],
            tags=tuple(data['tags']),
            viewer_count=data['viewer_count'],
            started_at=from_iso_string(data['started_at']) if data['started_at'] else None,
            language=data['language'],
            thumbnail_url=data['thumbnail_url'],
            is_mature=data['is_mature'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StreamInfo(identity={self.identity!r}, viewer_count={self.viewer_count})"


class ContentClassificationLabel(NamedTuple):
    """
    Represents a Twitch content classification label.

    Attributes
    ----------
    id: str
        Unique identifier for the content classification label.
    description: str
        Localized description of the content classification label.
    name: str
        Localized name of the content classification label.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    description: str
    name: str
    raw: helix.ContentClassificationLabel

    @classmethod
    def from_data(cls, data: helix.ContentClassificationLabel) -> ContentClassificationLabel:
        return cls(
            id=data['id'],
            description=data['description'],
            name=data['name'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ContentClassificationLabel(id={self.id!r}, name={self.name!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, ContentClassificationLabel):
            return self.id == other.id
        return False


class ScheduleSegment(NamedTuple):
    """
    Represents a broadcast segment in a streaming schedule.

    Attributes
    ----------
    id: str
        An ID that identifies this broadcast segment.
    start_time: datetime.datetime
        The UTC date and time of when the broadcast starts.
    end_time: datetime.datetime
        The UTC date and time of when the broadcast ends.
    title: str
        The broadcast segment's title.
    canceled_until: Optional[datetime.datetime]
        Indicates whether the broadcaster canceled this segment. Set to end_time if canceled, null otherwise.
    category: Optional[ScheduleCategory]
        The type of content that the broadcaster plans to stream.
    is_recurring: bool
        Whether the broadcast is part of a recurring series.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    title: str
    canceled_until: Optional[datetime.datetime]
    category: Optional[Category]
    is_recurring: bool
    raw: helix.ScheduleSegment

    @classmethod
    def from_data(cls, data: helix.ScheduleSegment) -> ScheduleSegment:
        category = None
        if data.get('category'):
            category = Category.from_data(data['category'])

        return cls(
            id=data['id'],
            start_time=from_iso_string(data['start_time']),
            end_time=from_iso_string(data['end_time']),
            title=data['title'],
            canceled_until=from_iso_string(data['canceled_until']) if data.get('canceled_until') else None,
            category=category,
            is_recurring=data['is_recurring'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ScheduleSegment(id={self.id!r}, title={self.title!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, ScheduleSegment):
            return self.id == other.id
        return False


class ScheduleVacation(NamedTuple):
    """
    Represents vacation dates when the broadcaster is not streaming.

    Attributes
    ----------
    start_time: datetime.datetime
        The UTC date and time of when the vacation starts.
    end_time: datetime.datetime
        The UTC date and time of when the vacation ends.
    """
    start_time: datetime.datetime
    end_time: datetime.datetime

    def __repr__(self) -> str:
        return f"ScheduleVacation(start_time={self.start_time!r}, end_time={self.end_time!r})"


class ChannelStreamSchedule(NamedTuple):
    """
    Represents a broadcaster's streaming schedule.

    Attributes
    ----------
    segments: Tuple[ScheduleSegment, ...]
        The tuple of broadcasts in the broadcaster's streaming schedule.
    identity: UserIdentity
        The broadcaster's identity information including id, login, and display name.
    vacation: Optional[ScheduleVacation]
        The dates when the broadcaster is on vacation and not streaming.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    segments: Tuple[ScheduleSegment, ...]
    identity: UserIdentity
    vacation: Optional[ScheduleVacation]
    raw: helix.ChannelStreamSchedule

    @classmethod
    def from_data(cls, data: helix.ChannelStreamSchedule) -> ChannelStreamSchedule:
        segments = tuple(ScheduleSegment.from_data(segment) for segment in data['segments'])
        vacation = None
        if data.get('vacation'):
            vacation = ScheduleVacation(
                start_time=from_iso_string(data['vacation']['start_time']),
                end_time=from_iso_string(data['vacation']['end_time'])
            )

        return cls(
            segments=segments,
            identity=UserIdentity(data['broadcaster_id'], data['broadcaster_name'], data['broadcaster_login']),
            vacation=vacation,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelStreamSchedule(identity={self.identity!r})"


class DropsEntitlement(NamedTuple):
    """
    Represents a drop entitlement.

    Attributes
    ----------
    id: str
        An ID that identifies the entitlement.
    benefit_id: str
        An ID that identifies the benefit (reward).
    timestamp: str
        The UTC date and time (in RFC3339 format) of when the entitlement was granted.
    user_id: str
        An ID that identifies the user who was granted the entitlement.
    game_id: str
        An ID that identifies the game the user was playing when the reward was entitled.
    fulfillment_status: str
        The entitlement's fulfillment status. Possible values are: CLAIMED, FULFILLED.
    last_updated: str
        The UTC date and time (in RFC3339 format) of when the entitlement was last updated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    benefit_id: str
    timestamp: str
    user_id: str
    game_id: str
    fulfillment_status: str
    last_updated: str
    raw: helix.DropsEntitlement

    @classmethod
    def from_data(cls, data: helix.DropsEntitlement) -> DropsEntitlement:
        return cls(
            id=data['id'],
            benefit_id=data['benefit_id'],
            timestamp=data['timestamp'],
            user_id=data['user_id'],
            game_id=data['game_id'],
            fulfillment_status=data['fulfillment_status'],
            last_updated=data['last_updated'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"DropsEntitlement(id={self.id!r}, user_id={self.user_id!r}, game_id={self.game_id!r})"

    def __eq__(self, other: DropsEntitlement) -> bool:
        if isinstance(other, DropsEntitlement):
            return self.id == other.id
        return False


class DropsEntitlementUpdate(NamedTuple):
    """
    Represents a drops entitlement update result.

    Attributes
    ----------
    status: str
        A string that indicates whether the status of the entitlements in the ids field were successfully updated.
        Possible values are:
        * INVALID_ID — The entitlement IDs in the ids field are not valid.
        * NOT_FOUND — The entitlement IDs in the ids field were not found.
        * SUCCESS — The status of the entitlements in the ids field were successfully updated.
        * UNAUTHORIZED — The user or organization identified by the user access token is not authorized to update the entitlements.
        * UPDATE_FAILED — The update failed. These are considered transient errors and the request should be retried later.
    ids: Tuple[str, ...]
        The list of entitlements that the status in the status field applies to.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    status: str
    ids: Tuple[str, ...]
    raw: helix.DropsEntitlementUpdate

    @classmethod
    def from_data(cls, data: helix.DropsEntitlementUpdate) -> DropsEntitlementUpdate:
        return cls(
            status=data['status'],
            ids=tuple(data['ids']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"DropsEntitlementUpdate(status={self.status!r}, ids_count={len(self.ids)})"


class Subscription(NamedTuple):
    """
    Twitch EventSub subscription.

    Attributes
    ----------
    id: str
        Unique subscription identifier
    status: str
        Subscription status (enabled, webhook_callback_verification_pending, etc.)
    type: str
        Type of subscription event
    version: str
        API version for the subscription
    condition: MappingProxyType[str, str]
        Subscription condition parameters
    transport: MappingProxyType[str, str]
        Transport information for the subscription
    created_at: datetime.datetime
        Subscription creation timestamp
    cost: int
        Cost points for this subscription
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    status: str
    type: str
    version: str
    condition: MappingProxyType[str, str]
    transport: helix.Transport
    created_at: datetime.datetime
    cost: int
    raw: helix.Subscription

    @classmethod
    def from_data(cls, data: helix.Subscription) -> Subscription:
        return cls(
            id=data['id'],
            status=data['status'],
            type=data['type'],
            version=data['version'],
            condition=MappingProxyType(data['condition']),
            transport=MappingProxyType(data['transport']),  # type: ignore
            created_at=from_iso_string(data['created_at']),
            cost=data['cost'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Subscription(id={self.id!r}, type={self.type!r}, version={self.version!r}, status={self.status!r})"

    def __eq__(self, other: Subscription) -> bool:
        if not isinstance(other, Subscription):
            return False
        return (
                self.version == other.version
                and self.type == other.type
                and self.transport == other.transport
                and self.condition == other.condition
        )

    @property
    def __bool__(self) -> bool:
        return self.status == 'enabled'

    def __hash__(self) -> int:
        return hash(self.id)


class Conduit(NamedTuple):
    """
    Represents a Twitch EventSub conduit.

    Attributes
    ----------
    id: str
        Conduit ID.
    shard_count: int
        Number of shards created for this conduit.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    id: str
    shard_count: int
    raw: helix.Conduit

    @classmethod
    def from_data(cls, data: helix.Conduit) -> Conduit:
        return cls(
            id=data['id'],
            shard_count=data['shard_count'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Conduit(id={self.id!r}, shard_count={self.shard_count})"

    def __eq__(self, other: Conduit) -> bool:
        if isinstance(other, Conduit):
            return self.id == other.id
        return False


class ConduitShard(NamedTuple):
    """
    Represents a conduit shard.

    Attributes
    ----------
    id: str
        Shard ID.
    status: str
        The shard status. Possible values include:
        - enabled
        - webhook_callback_verification_pending
        - webhook_callback_verification_failed
        - notification_failures_exceeded
        - websocket_disconnected
        - websocket_failed_ping_pong
        - websocket_received_inbound_traffic
        - websocket_internal_error
        - websocket_network_timeout
        - websocket_network_error
        - websocket_failed_to_reconnect
    method: str
        The transport method (webhook or websocket).
    callback: Optional[str]
        The callback URL for webhook transport.
    session_id: Optional[str]
        WebSocket session ID for websocket transport.
    connected_at: Optional[datetime]
        UTC datetime when WebSocket connection was established.
    disconnected_at: Optional[datetime]
        UTC datetime when WebSocket connection was lost.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    status: str
    method: str
    callback: Optional[str]
    session_id: Optional[str]
    connected_at: Optional[datetime]
    disconnected_at: Optional[datetime]
    raw: helix.ConduitShard

    @classmethod
    def from_data(cls, data: helix.ConduitShard) -> ConduitShard:
        transport = data['transport']
        connected_at = transport.get('connected_at')
        disconnected_at = transport.get('disconnected_at')
        return cls(
            id=data['id'],
            status=data['status'],
            method=transport['method'],
            callback=transport.get('callback'),
            session_id=transport.get('session_id'),
            connected_at=from_iso_string(connected_at) if connected_at else None,
            disconnected_at=from_iso_string(disconnected_at) if disconnected_at else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ConduitShard(id={self.id!r}, status={self.status!r}, method={self.method!r})"

    def __eq__(self, other: ConduitShard) -> bool:
        if isinstance(other, ConduitShard):
            return self.id == other.id
        return False


class ConduitShardError(NamedTuple):
    """
    Represents an error that occurred while updating a conduit shard.

    Attributes
    ----------
    id: str
        Shard ID that failed to update.
    message: str
        The error message describing what went wrong.
    code: str
        Error code representing the specific error condition.
    """
    id: str
    message: str
    code: str

    @classmethod
    def from_data(cls, data: helix.ConduitShardError) -> ConduitShardError:
        return cls(
            id=data['id'],
            message=data['message'],
            code=data['code'],
        )

    def __repr__(self) -> str:
        return f"ConduitShardError(id={self.id!r}, code={self.code!r})"


class ConduitShardUpdate(NamedTuple):
    """
    Represents the result of updating conduit shards.

    Attributes
    ----------
    shards: Tuple[ConduitShard, ...]
        Tuple of successfully updated shards.
    errors: Tuple[ConduitShardError, ...]
        Tuple of shards that failed to update.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    shards: Tuple[ConduitShard, ...]
    errors: Tuple[ConduitShardError, ...]
    raw: helix.UpdateConduitShards

    @classmethod
    def from_data(cls, data: helix.UpdateConduitShards) -> ConduitShardUpdate:
        successful_shards = tuple(
            ConduitShard.from_data(shard) for shard in data.get('data', [])
        )
        error_shards = tuple(
            ConduitShardError.from_data(error) for error in data.get('errors', [])
        )

        return cls(
            shards=successful_shards,
            errors=error_shards,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ConduitShardUpdate()"


class ExtensionLiveChannel(NamedTuple):
    """
    Represents a live channel with an extension installed or activated.

    Attributes
    ----------
    broadcaster: UserIdentity
        The broadcaster.
    game_name: str
        The name of the game being played.
    game_id: str
        The ID of the game being played.
    title: str
        The title of the stream.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster: UserIdentity
    game_name: str
    game_id: str
    title: str
    raw: helix.ExtensionLiveChannel

    @classmethod
    def from_data(cls, data: helix.ExtensionLiveChannel) -> ExtensionLiveChannel:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login='',  # Not provided in this endpoint
            name=data['broadcaster_name']
        )
        return cls(
            broadcaster=broadcaster,
            game_name=data['game_name'],
            game_id=data['game_id'],
            title=data['title'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ExtensionLiveChannel(broadcaster_id={self.broadcaster.id!r})"


class ExtensionSecret(NamedTuple):
    """
    Represents an extension secret.

    Attributes
    ----------
    format_version: int
        The secret format version.
    content: str
        The secret content.
    active_at: datetime
        The time when the secret becomes active.
    expires_at: datetime
        The time when the secret expires.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    format_version: int
    content: str
    active_at: datetime
    expires_at: datetime
    raw: helix.ExtensionSecret

    @classmethod
    def from_data(cls, data: helix.ExtensionSecret) -> ExtensionSecret:
        return cls(
            format_version=data['format_version'],
            content=data['content'],
            active_at=from_iso_string(data['active_at']),
            expires_at=from_iso_string(data['expires_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ExtensionSecret(format_version={self.format_version})"


class ExtensionConfiguration(NamedTuple):
    """
    Represents an extension configuration.

    Attributes
    ----------
    broadcaster_id: str
        The ID of the broadcaster.
    extension_id: str
        The ID of the extension.
    segment: str
        The segment type (e.g., global, broadcaster, viewer).
    version: str
        The configuration version.
    content: str
        The configuration content.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_id: str
    extension_id: str
    segment: str
    version: str
    content: str
    raw: helix.ExtensionConfiguration

    @classmethod
    def from_data(cls, data: helix.ExtensionConfiguration) -> ExtensionConfiguration:
        return cls(
            broadcaster_id=data['broadcaster_id'],
            extension_id=data['extension_id'],
            segment=data['segment'],
            version=data['version'],
            content=data['content'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ExtensionConfiguration(extension_id={self.extension_id!r}, segment={self.segment!r})"


class Extension(NamedTuple):
    """
    Represents an extension.

    Attributes
    ----------
    id: str
        The extension ID.
    version: str
        The extension version.
    author_name: str
        The extension author name.
    bits_enabled: bool
        Whether Bits are enabled.
    can_install: bool
        Whether the extension can be installed.
    configurations: Tuple[ExtensionConfiguration, ...]
        The configurations.
    description: str
        The extension description.
    has_chat_support: bool
        Whether the extension has chat support.
    icon_url: str
        The icon URL.
    name: str
        The extension name.
    views: Tuple[str, ...]
        The views.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    version: str
    author_name: str
    bits_enabled: bool
    can_install: bool
    configurations: Tuple[ExtensionConfiguration, ...]
    description: str
    has_chat_support: bool
    icon_url: str
    name: str
    views: Tuple[str, ...]
    raw: helix.Extension

    @classmethod
    def from_data(cls, data: helix.Extension) -> Extension:
        configurations = tuple(ExtensionConfiguration.from_data(config) for config in data.get('configurations', []))
        return cls(
            id=data['id'],
            version=data['version'],
            author_name=data['author_name'],
            bits_enabled=data['bits_enabled'],
            can_install=data['can_install'],
            configurations=configurations,
            description=data['description'],
            has_chat_support=data['has_chat_support'],
            icon_url=data['icon_url'],
            name=data['name'],
            views=tuple(data['views']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Extension(id={self.id!r}, name={self.name!r})"


class FollowedChannel(NamedTuple):
    """
    Represents a followed channel.

    Attributes
    ----------
    broadcaster: UserIdentity
        The broadcaster that this user is following.
    followed_at: datetime
        The UTC timestamp when the user started following the broadcaster.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster: UserIdentity
    followed_at: datetime
    raw: helix.FollowedChannel

    @classmethod
    def from_data(cls, data: helix.FollowedChannel) -> FollowedChannel:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        return cls(
            broadcaster=broadcaster,
            followed_at=from_iso_string(data['followed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"FollowedChannel(broadcaster_id={self.broadcaster.id!r})"


class ChannelFollower(NamedTuple):
    """
    Represents a channel follower.

    Attributes
    ----------
    user: UserIdentity
        The follower.
    followed_at: datetime
        The UTC timestamp when the user started following the broadcaster.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    followed_at: datetime
    raw: helix.ChannelFollower

    @classmethod
    def from_data(cls, data: helix.ChannelFollower) -> ChannelFollower:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            followed_at=from_iso_string(data['followed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelFollower(user_id={self.user.id!r})"


class ChannelEditor(NamedTuple):
    """
    Represents a channel editor.

    Attributes
    ----------
    user: UserIdentity
        The user that was granted editor privileges.
    created_at: datetime
        The date and time that the user was granted editor privileges.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    created_at: datetime
    raw: helix.ChannelEditor

    @classmethod
    def from_data(cls, data: helix.ChannelEditor) -> ChannelEditor:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_name'].lower(),
            name=data['user_name']
        )
        return cls(
            user=user,
            created_at=from_iso_string(data['created_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelEditor(user_id={self.user.id!r})"


class ChannelVIP(NamedTuple):
    """
    Represents a channel VIP.

    Attributes
    ----------
    user: UserIdentity
        The VIP user.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    raw: helix.BaseUser

    @classmethod
    def from_data(cls, data: helix.BaseUser) -> ChannelVIP:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelVIP(user_id={self.user.id!r})"


class ShieldModeStatus(NamedTuple):
    """
    Represents the Shield Mode status.

    Attributes
    ----------
    is_active: bool
        A Boolean value that determines whether Shield Mode is active. Is true if Shield Mode is active; otherwise, false.
    moderator: UserIdentity
        The moderator that last activated Shield Mode.
    last_activated_at: datetime
        The UTC date and time (in RFC3339 format) of when Shield Mode was last activated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    is_active: bool
    moderator: UserIdentity
    last_activated_at: datetime
    raw: helix.ShieldModeStatus

    @classmethod
    def from_data(cls, data: helix.ShieldModeStatus) -> ShieldModeStatus:
        moderator = UserIdentity(
            id=data['moderator_id'],
            login=data['moderator_login'],
            name=data['moderator_name']
        )
        return cls(
            is_active=data['is_active'],
            moderator=moderator,
            last_activated_at=from_iso_string(data['last_activated_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ShieldModeStatus(is_active={self.is_active})"


class WarnReason(NamedTuple):
    """
    Represents a warn reason.

    Attributes
    ----------
    user: UserIdentity
        The warned user.
    reason: str
        The reason for the warning.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    reason: str
    raw: helix.WarnReason

    @classmethod
    def from_data(cls, data: helix.WarnReason) -> WarnReason:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            reason=data['reason'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"WarnReason(user_id={self.user.id!r}, reason={self.reason!r})"


class Raid(NamedTuple):
    """
    Represents a raid.

    Attributes
    ----------
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the raid was started.
    is_mature: bool
        Indicates whether the channel being raided contains mature content.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    created_at: datetime
    is_mature: bool
    raw: helix.Raid

    @classmethod
    def from_data(cls, data: helix.Raid) -> Raid:
        return cls(
            created_at=from_iso_string(data['created_at']),
            is_mature=data['is_mature'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Raid(created_at={self.created_at!r})"


class StreamKey(NamedTuple):
    """
    Represents a stream key.

    Attributes
    ----------
    stream_key: str
        The stream key.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    stream_key: str
    raw: helix.StreamKey

    @classmethod
    def from_data(cls, data: helix.StreamKey) -> StreamKey:
        return cls(
            stream_key=data['stream_key'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StreamKey(stream_key={self.stream_key!r})"


class UserActiveExtensionUpdate(NamedTuple):
    """
    Represents an update to user active extensions.

    Attributes
    ----------
    panel: Tuple[ExtensionPanel, ...]
        The updated panel extensions.
    overlay: Tuple[ExtensionOverlay, ...]
        The updated overlay extensions.
    component: Tuple[ExtensionComponent, ...]
        The updated component extensions.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """
    panel: Tuple[ExtensionPanel, ...]
    overlay: Tuple[ExtensionOverlay, ...]
    component: Tuple[ExtensionComponent, ...]
    raw: helix.UserActiveExtensionUpdate

    @classmethod
    def from_data(cls, data: helix.UserActiveExtensionUpdate) -> UserActiveExtensionUpdate:
        panels = tuple(
            ExtensionPanel(
                active=panel['active'],
                id=panel['id'],
                version=panel['version'],
                name=panel['name']
            ) for panel in data.get('panel', [])
        )
        overlays = tuple(
            ExtensionOverlay(
                active=overlay['active'],
                id=overlay['id'],
                version=overlay['version'],
                name=overlay['name']
            ) for overlay in data.get('overlay', [])
        )
        components = tuple(
            ExtensionComponent(
                active=component['active'],
                id=component['id'],
                version=component['version'],
                name=component['name'],
                x=component['x'],
                y=component['y']
            ) for component in data.get('component', [])
        )
        return cls(
            panel=panels,
            overlay=overlays,
            component=components,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"UserActiveExtensionUpdate()"


class AdSchedule(NamedTuple):
    """
    Represents an ad schedule entry.

    Attributes
    ----------
    snooze_count: int
        The number of snoozes available for the broadcaster.
    snooze_refresh_at: Optional[datetime]
        The UTC timestamp when the broadcaster will gain an additional snooze, in RFC3339 format.
    next_ad_at: Optional[datetime]
        The UTC timestamp of the broadcaster's next scheduled ad,
        in RFC3339 format. None if the channel has no ad scheduled or is not live.
    duration: int
        The length in seconds of the scheduled upcoming ad break.
    last_ad_at: Optional[datetime]
        The UTC timestamp of the broadcaster's last ad-break, in RFC3339 format.
        None if the channel has not run an ad or is not live.
    preroll_free_time: int
        The amount of pre-roll free time remaining for the channel in seconds.
        Returns 0 if they are currently not pre-roll free.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    snooze_count: int
    snooze_refresh_at: Optional[datetime]
    next_ad_at: Optional[datetime]
    duration: int
    last_ad_at: Optional[datetime]
    preroll_free_time: int
    raw: helix.AdSchedule

    @classmethod
    def from_data(cls, data: helix.AdSchedule) -> AdSchedule:
        snooze_refresh_at = from_iso_string(data['snooze_refresh_at']) if data['snooze_refresh_at'] else None
        next_ad_at = from_iso_string(data['next_ad_at']) if data['next_ad_at'] else None
        last_ad_at = from_iso_string(data['last_ad_at']) if data['last_ad_at'] else None
        return cls(
            snooze_count=data['snooze_count'],
            snooze_refresh_at=snooze_refresh_at,
            next_ad_at=next_ad_at,
            duration=data['duration'],
            last_ad_at=last_ad_at,
            preroll_free_time=data['preroll_free_time'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"AdSchedule(snooze_count={self.snooze_count}, duration={self.duration})"


class AdSnooze(NamedTuple):
    """
    Represents an ad snooze response.

    Attributes
    ----------
    snooze_count: int
        The number of snoozes available for the broadcaster.
    snooze_refresh_at: Optional[datetime]
        The UTC timestamp when the broadcaster will gain an additional snooze, in RFC3339 format.
    next_ad_at: Optional[datetime]
        The UTC timestamp of the broadcaster's next scheduled ad, in RFC3339 format.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    snooze_count: int
    snooze_refresh_at: Optional[datetime]
    next_ad_at: Optional[datetime]
    raw: helix.AdSnooze

    @classmethod
    def from_data(cls, data: helix.AdSnooze) -> AdSnooze:
        snooze_refresh_at = from_iso_string(data['snooze_refresh_at']) if data['snooze_refresh_at'] else None
        next_ad_at = from_iso_string(data['next_ad_at']) if data['next_ad_at'] else None
        return cls(
            snooze_count=data['snooze_count'],
            snooze_refresh_at=snooze_refresh_at,
            next_ad_at=next_ad_at,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"AdSnooze(snooze_count={self.snooze_count})"


class AnalyticsReport(NamedTuple):
    """
    Represents an analytics report.

    Attributes
    ----------
    extension_id: Optional[str]
        An ID that identifies the extension that the report was generated for. None for game analytics.
    game_id: Optional[str]
        An ID that identifies the game that the report was generated for. None for extension analytics.
    url: str
        The URL that you use to download the report. The URL is valid for 5 minutes.
    type: str
        The type of report.
    started_at: datetime
        The reporting window's start date.
    ended_at: datetime
        The reporting window's end date.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    extension_id: Optional[str]
    game_id: Optional[str]
    url: str
    type: str
    started_at: datetime
    ended_at: datetime
    raw: helix.AnalyticsReport

    @classmethod
    def from_data(cls, data: helix.AnalyticsReport) -> AnalyticsReport:
        date_range = data['date_range']
        return cls(
            extension_id=data.get('extension_id'),
            game_id=data.get('game_id'),
            url=data['URL'],
            type=data['type'],
            started_at=from_iso_string(date_range['started_at']),
            ended_at=from_iso_string(date_range['ended_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"AnalyticsReport(type={self.type!r}, url={self.url!r})"


class BitsLeaderboardEntry(NamedTuple):
    """
    Represents an entry in the Bits leaderboard.

    Attributes
    ----------
    user: UserIdentity
        The user on the leaderboard.
    rank: int
        The user's position on the leaderboard.
    score: int
        The number of Bits the user has cheered.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    rank: int
    score: int
    raw: helix.BitsLeaderboardEntry

    @classmethod
    def from_data(cls, data: helix.BitsLeaderboardEntry) -> BitsLeaderboardEntry:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            rank=data['rank'],
            score=data['score'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"BitsLeaderboardEntry(user_id={self.user.id!r}, rank={self.rank}, score={self.score})"


class Amount(NamedTuple):
    """
    Represents a monetary amount.

    Attributes
    ----------
    value: int
        The monetary amount. The amount is specified in the currency's minor unit.
    decimal_places: int
        The number of decimal places used by the currency.
    currency: str
        The ISO-4217 three-letter currency code that identifies the type of currency in value.
    """

    value: int
    decimal_places: int
    currency: str

    def __repr__(self) -> str:
        return f"Amount(value={self.value}, currency={self.currency!r})"


class Charity(NamedTuple):
    """
    Represents a charity in a campaign.

    Attributes
    ----------
    name: str
        The charity's name.
    description: str
        A description of the charity.
    logo: str
        A URL to an image of the charity's logo. The image's type is PNG and its size is 100px X 100px.
    website: str
        A URL to the charity's website.
    """

    name: str
    description: str
    logo: str
    website: str

    def __repr__(self) -> str:
        return f"Charity(name={self.name!r})"


class CharityCampaign(NamedTuple):
    """
    Represents a charity campaign.

    Attributes
    ----------
    id: str
        An ID that identifies the charity campaign.
    broadcaster: UserIdentity
        Information about the broadcaster that's running the campaign.
    charity: Charity
        Information about the charity.
    current_amount: Amount
        The current amount of donations that the campaign has received.
    target_amount: Optional[Amount]
        The campaign's fundraising goal. None if the broadcaster has not defined a fundraising goal.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster: UserIdentity
    charity: Charity
    current_amount: Amount
    target_amount: Optional[Amount]
    raw: helix.CharityCampaign

    @classmethod
    def from_data(cls, data: helix.CharityCampaign) -> CharityCampaign:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        charity = Charity(
            name=data['charity_name'],
            description=data['charity_description'],
            logo=data['charity_logo'],
            website=data['charity_website']
        )
        current_amount = Amount(
            value=data['current_amount']['value'],
            decimal_places=data['current_amount']['decimal_places'],
            currency=data['current_amount']['currency']
        )
        target_amount_data = data.get('target_amount')
        target_amount = Amount(
            value=target_amount_data['value'],
            decimal_places=target_amount_data['decimal_places'],
            currency=target_amount_data['currency']
        ) if target_amount_data else None
        return cls(
            id=data['id'],
            broadcaster=broadcaster,
            charity=charity,
            current_amount=current_amount,
            target_amount=target_amount,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"CharityCampaign(id={self.id!r}, broadcaster_id={self.broadcaster.id!r})"


class CharityDonation(NamedTuple):
    """
    Represents a charity donation.

    Attributes
    ----------
    id: str
        An ID that identifies the donation. The ID is unique across campaigns.
    campaign_id: str
        An ID that identifies the charity campaign that the donation applies to.
    user: UserIdentity
        The user that donated money to the campaign.
    amount: Amount
        An object that contains the amount of money that the user donated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    campaign_id: str
    user: UserIdentity
    amount: Amount
    raw: helix.CharityDonation

    @classmethod
    def from_data(cls, data: helix.CharityDonation) -> CharityDonation:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        amount = Amount(
            value=data['amount']['value'],
            decimal_places=data['amount']['decimal_places'],
            currency=data['amount']['currency']
        )
        return cls(
            id=data['id'],
            campaign_id=data['campaign_id'],
            user=user,
            amount=amount,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"CharityDonation(id={self.id!r}, user_id={self.user.id!r})"


class Chatter(NamedTuple):
    """
    Represents a chatter in a channel.

    Attributes
    ----------
    user: UserIdentity
        The chatter's identity.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    raw: helix.BaseUser

    @classmethod
    def from_data(cls, data: helix.BaseUser) -> Chatter:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Chatter(user_id={self.user.id!r}, user_name={self.user.name!r})"


class CreatorGoal(NamedTuple):
    """
    Represents a creator goal.

    Attributes
    ----------
    id: str
        An ID that identifies this goal.
    broadcaster: UserIdentity
        The broadcaster that created the goal.
    type: str
        The type of goal.
    description: str
        A description of the goal, if specified. The description may be an empty string if not specified.
    is_achieved: bool
        A Boolean value that indicates whether the broadcaster achieved their goal.
    current_amount: int
        The goal's current value.
    target_amount: int
        The goal's target value.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the broadcaster created the goal.
    updated_at: datetime
        The UTC date and time (in RFC3339 format) of when the broadcaster last updated the goal.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster: UserIdentity
    type: str
    description: str
    is_achieved: bool
    current_amount: int
    target_amount: int
    created_at: datetime
    updated_at: datetime
    raw: helix.CreatorGoal

    @classmethod
    def from_data(cls, data: helix.CreatorGoal) -> CreatorGoal:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        return cls(
            id=data['id'],
            broadcaster=broadcaster,
            type=data['type'],
            description=data['description'],
            is_achieved=data['is_achieved'],
            current_amount=data['current_amount'],
            target_amount=data['target_amount'],
            created_at=from_iso_string(data['created_at']),
            updated_at=from_iso_string(data['updated_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"CreatorGoal(id={self.id!r}, type={self.type!r})"


class Contribution(NamedTuple):
    """
    Represents a contribution to a Hype Train.

    Attributes
    ----------
    user: UserIdentity
        The user who contributed.
    type: str
        The contribution method. Possible values are: bits, channel_points, subscription.
    total: int
        Total aggregated amount of all contributions made during the Hype Train.
    """

    user: UserIdentity
    type: str
    total: int


class HypeTrainEvent(NamedTuple):
    """
    Represents a Hype Train event.

    Attributes
    ----------
    id: str
        The Hype Train ID.
    broadcaster_id: str
        Broadcaster user ID Hype Train takes place in.
    cooldown_end_time: datetime
        The time when the Hype Train cooldown ends so that the next Hype Train can start.
    expires_at: datetime
        The time when the Hype Train expires. The expiration is extended when the Hype Train level increases. If the Hype Train level doesn't increase before this time, the Hype Train ends.
    goal: int
        The requested goal value required to reach the next level.
    last_contribution: Contribution
        The most recent contribution towards the Hype Train's goal.
    level: int
        The current level of Hype Train event. Values are between 1 (minimum) and 5 (maximum).
    started_at: datetime
        The time when the Hype Train started.
    top_contributions: Tuple[Contribution, ...]
        The contributors with the most points contributed.
    contributions: Tuple[Contribution, ...]
        All contributions from this Hype Train.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster_id: str
    cooldown_end_time: datetime
    expires_at: datetime
    goal: int
    last_contribution: Contribution
    level: int
    started_at: datetime
    top_contributions: Tuple[Contribution, ...]
    contributions: Tuple[Contribution, ...]
    raw: helix.HypeTrainEvent

    @classmethod
    def from_data(cls, data: helix.HypeTrainEvent) -> HypeTrainEvent:
        event_data = data['event_data']
        last_contribution = Contribution(
            user=UserIdentity(
                id=event_data['last_contribution']['user_id'],
                login=event_data['last_contribution']['user_login'],
                name=event_data['last_contribution']['user_name']
            ),
            type=event_data['last_contribution']['type'],
            total=event_data['last_contribution']['total']
        )
        top_contributions = tuple(
            Contribution(
                user=UserIdentity(
                    id=contrib['user_id'],
                    login=contrib['user_login'],
                    name=contrib['user_name']
                ),
                type=contrib['type'],
                total=contrib['total']
            ) for contrib in event_data['top_contributions']
        )
        contributions = tuple(
            Contribution(
                user=UserIdentity(
                    id=contrib['user_id'],
                    login=contrib['user_login'],
                    name=contrib['user_name']
                ),
                type=contrib['type'],
                total=contrib['total']
            ) for contrib in event_data['contributions']
        )
        return cls(
            id=data['id'],
            broadcaster_id=event_data['broadcaster_id'],
            cooldown_end_time=from_iso_string(event_data['cooldown_end_time']),
            expires_at=from_iso_string(event_data['expires_at']),
            goal=event_data['goal'],
            last_contribution=last_contribution,
            level=event_data['level'],
            started_at=from_iso_string(event_data['started_at']),
            top_contributions=top_contributions,
            contributions=contributions,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"HypeTrainEvent(id={self.id!r}, level={self.level})"


class HypeTrainRecord(NamedTuple):
    """
    Represents a Hype Train record.

    Attributes
    ----------
    level: int
        The level achieved in this Hype Train record.
    total: int
        The total points/contributions achieved.
    achieved_at: datetime
        The time when this record was achieved.
    """

    level: int
    total: int
    achieved_at: datetime

    def __repr__(self):
        return f"HypeTrainRecord(level={self.level}, total={self.total})"


class CurrentHypeTrain(NamedTuple):
    """
    Represents the current active Hype Train.

    Attributes
    ----------
    id: str
        The unique identifier for this Hype Train.
    broadcaster: UserIdentity
        The broadcaster whose channel the Hype Train is taking place in.
    level: int
        The current level of the Hype Train.
    total: int
        The total contributions made to this Hype Train.
    progress: int
        The current progress towards the next level.
    goal: int
        The goal amount needed to reach the next level.
    top_contributions: Tuple[Contribution, ...]
        The top contributors to this Hype Train.
    shared_train_participants: Optional[Tuple[UserIdentity, ...]]
        Participants in shared Hype Train events, if applicable.
    started_at: datetime
        The time when this Hype Train started.
    expires_at: datetime
        The time when this Hype Train will expire.
    type: str
        The type of Hype Train. Possible values are: treasure, golden_kappa, regular.
    """

    id: str
    broadcaster: UserIdentity
    level: int
    total: int
    progress: int
    goal: int
    top_contributions: Tuple[Contribution, ...]
    shared_train_participants: Optional[Tuple[UserIdentity, ...]]
    started_at: datetime
    expires_at: datetime
    type: str

    @classmethod
    def from_data(cls, data: helix.CurrentHypeTrain) -> CurrentHypeTrain:
        return cls(
            id=data['id'],
            broadcaster=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            level=data['level'],
            total=data['total'],
            progress=data['progress'],
            goal=data['goal'],
            top_contributions=tuple(
                Contribution(
                    user=UserIdentity(
                        id=contrib['user_id'],
                        login=contrib['user_login'],
                        name=contrib['user_name']
                    ),
                    type=contrib['type'],
                    total=contrib['total']
                ) for contrib in data['top_contributions']
            ),
            shared_train_participants=tuple(
                UserIdentity(
                    id=participant['broadcaster_user_id'],
                    login=participant['broadcaster_user_login'],
                    name=participant['broadcaster_user_name']
                ) for participant in data['shared_train_participants']
            ) if data.get('shared_train_participants', None) else None,
            started_at=from_iso_string(data['started_at']),
            expires_at=from_iso_string(data['expires_at']),
            type=data['type']
        )

    def __repr__(self) -> str:
        return f"CurrentHypeTrain(id={self.id!r}, level={self.level}, type={self.type!r})"


class HypeTrainStatus(NamedTuple):
    """
    Represents comprehensive Hype Train data including current and historical records.

    Attributes
    ----------
    current: Optional[CurrentHypeTrain]
        The currently active Hype Train, if any.
    all_time_high: Optional[HypeTrainRecord]
        The all-time high Hype Train record for this channel.
    shared_all_time_high: Optional[HypeTrainRecord]
        The all-time high shared Hype Train record, if applicable.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    current: Optional[CurrentHypeTrain]
    all_time_high: Optional[HypeTrainRecord]
    shared_all_time_high: Optional[HypeTrainRecord]
    raw: helix.HypeTrainStatus

    @classmethod
    def from_data(cls, data: helix.HypeTrainStatus) -> HypeTrainStatus:
        return cls(
            current=CurrentHypeTrain.from_data(data['current']) if data.get('current', None) else None,
            all_time_high=HypeTrainRecord(
                level=data['all_time_high']['level'],
                total=data['all_time_high']['total'],
                achieved_at=from_iso_string(data['all_time_high']['achieved_at'])
            ) if data.get('all_time_high', None) else None,
            shared_all_time_high=HypeTrainRecord(
                level=data['shared_all_time_high']['level'],
                total=data['shared_all_time_high']['total'],
                achieved_at=from_iso_string(data['shared_all_time_high']['achieved_at'])
            ) if data.get('shared_all_time_high', None) else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"HypeTrainStatus()"


class AutoModSettings(NamedTuple):
    """
    Represents AutoMod settings.

    Attributes
    ----------
    broadcaster_id: str
        The ID of the broadcaster specified in the request.
    moderator_id: str
        The ID of a user that has permission to moderate the broadcaster's chat room.
    overall_level: Optional[int]
        The default AutoMod level for the broadcaster.
        This field is null if the broadcaster has not set an overall level of AutoMod filtering.
    aggression: int
        The Automod level for hostility involving aggression.
    bullying: int
        The Automod level for hostility involving name-calling or insults.
    disability: int
        The Automod level for discrimination against disability.
    misogyny: int
        The Automod level for discrimination against women.
    racism: int
        The Automod level for discrimination based on ethnicity, color, or national origin.
    sexism: int
        The Automod level for discrimination based on sex.
    sexuality_sex_or_gender: int
        The AutoMod level for discrimination based on sexuality, sex, or gender.
    swearing: int
        The Automod level for profanity.
    sexual_violence: int
        The Automod level for sexual violence.
    suicide: int
        The Automod level for suicide or self-harm.
    other: int
        The Automod level for other types of discrimination.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

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
    raw: helix.AutoModSettings

    @classmethod
    def from_data(cls, data: helix.AutoModSettings) -> AutoModSettings:
        return cls(
            broadcaster_id=data['broadcaster_id'],
            moderator_id=data['moderator_id'],
            overall_level=data.get('overall_level'),
            aggression=data['aggression'],
            bullying=data['bullying'],
            disability=data['disability'],
            misogyny=data['misogyny'],
            racism=data['racism'],
            sexism=data['sexism'],
            sexuality_sex_or_gender=data['sexuality_sex_or_gender'],
            swearing=data['swearing'],
            sexual_violence=data['sexual_violence'],
            suicide=data['suicide'],
            other=data['other'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"AutoModSettings(broadcaster_id={self.broadcaster_id!r})"


class AutoModStatusMessage(NamedTuple):
    """
    Represents the status of an AutoMod message.

    Attributes
    ----------
    msg_id: str
        The unique ID of the message flagged by AutoMod.
    msg_text: str
        The text content of the flagged message.
    """

    msg_id: str
    msg_text: str

    @classmethod
    def from_data(cls, data: helix.AutoModStatusMessage) -> AutoModStatusMessage:
        return cls(
            msg_id=data['msg_id'],
            msg_text=data['msg_text']
        )

    def __repr__(self) -> str:
        return f"AutoModStatusMessage(msg_id={self.msg_id!r})"


class BannedUser(NamedTuple):
    """
    Represents a banned user.

    Attributes
    ----------
    user: UserIdentity
        The banned user.
    expires_at: Optional[datetime]
        The UTC date and time (in RFC3339 format) of when the timeout expires,
        or None if the user was banned and not timed out.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the user was banned or timed out.
    reason: str
        The reason the user was banned or timed out, if a reason was provided.
    moderator: UserIdentity
        The moderator that banned the user or added the timeout.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    expires_at: Optional[datetime]
    created_at: datetime
    reason: str
    moderator: UserIdentity
    raw: helix.BannedUser

    @classmethod
    def from_data(cls, data: helix.BannedUser) -> BannedUser:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        moderator = UserIdentity(
            id=data['moderator_id'],
            login=data['moderator_login'],
            name=data['moderator_name']
        )
        expires_at = from_iso_string(data['expires_at']) if data['expires_at'] else None
        return cls(
            user=user,
            expires_at=expires_at,
            created_at=from_iso_string(data['created_at']),
            reason=data['reason'],
            moderator=moderator,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"BannedUser(user_id={self.user.id!r}, reason={self.reason!r})"


class UnbanRequest(NamedTuple):
    """
    Represents an unban request.

    Attributes
    ----------
    id: str
        An ID that identifies the unban request.
    broadcaster: UserIdentity
        The broadcaster whose chat room the user is requesting an unban from.
    user: UserIdentity
        The user requesting the unban.
    text: str
        The unban request message.
    status: str
        The status of the unban request. Possible values are:
        pending, approved, denied, acknowledged, canceled.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the unban request was created.
    resolved_at: Optional[datetime]
        The UTC date and time (in RFC3339 format) of when the unban request was resolved.
        None if the request is still pending.
    resolution_text: str
        The moderator's message to the user explaining why the request was denied.
        The string is empty if the request is pending or approved.
    moderator: UserIdentity
        The moderator that resolved the request. Empty fields if the request is pending.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster: UserIdentity
    user: UserIdentity
    text: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]
    resolution_text: str
    moderator: UserIdentity
    raw: helix.UnbanRequest

    @classmethod
    def from_data(cls, data: helix.UnbanRequest) -> UnbanRequest:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        moderator = UserIdentity(
            id=data['moderator_id'],
            login=data['moderator_login'],
            name=data['moderator_name']
        )
        resolved_at = from_iso_string(data['resolved_at']) if data['resolved_at'] else None
        return cls(
            id=data['id'],
            broadcaster=broadcaster,
            user=user,
            text=data['text'],
            status=data['status'],
            created_at=from_iso_string(data['created_at']),
            resolved_at=resolved_at,
            resolution_text=data['resolution_text'],
            moderator=moderator,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"UnbanRequest(id={self.id!r}, status={self.status!r})"


class BlockedTerm(NamedTuple):
    """
    Represents a blocked term.

    Attributes
    ----------
    broadcaster_id: str
        The broadcaster that owns the list of blocked terms.
    moderator_id: str
        The moderator that last updated the blocked term.
    id: str
        An ID that uniquely identifies the blocked term.
    text: str
        The blocked term.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the term was blocked.
    updated_at: Optional[datetime]
        The UTC date and time (in RFC3339 format) of when the term was updated. None if the term hasn't been updated.
    expires_at: Optional[datetime]
        The UTC date and time (in RFC3339 format) of when the blocked term is set to expire. None if not set.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_id: str
    moderator_id: str
    id: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    raw: helix.BlockedTerm

    @classmethod
    def from_data(cls, data: helix.BlockedTerm) -> BlockedTerm:
        updated_at = from_iso_string(data['updated_at']) if data.get('updated_at') else None
        expires_at = from_iso_string(data['expires_at']) if data.get('expires_at') else None
        return cls(
            broadcaster_id=data['broadcaster_id'],
            moderator_id=data['moderator_id'],
            id=data['id'],
            text=data['text'],
            created_at=from_iso_string(data['created_at']),
            updated_at=updated_at,
            expires_at=expires_at,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"BlockedTerm(id={self.id!r}, text={self.text!r})"


class Moderator(NamedTuple):
    """
    Represents a moderator.

    Attributes
    ----------
    user: UserIdentity
        The moderator.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the moderator was added.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    created_at: datetime
    raw: helix.Moderator

    @classmethod
    def from_data(cls, data: helix.Moderator) -> Moderator:
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            user=user,
            created_at=from_iso_string(data['created_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Moderator(user_id={self.user.id!r}, user_name={self.user.name!r})"


class PollChoice(NamedTuple):
    """
    Represents a poll choice.

    Attributes
    ----------
    id: str
        ID for the choice.
    title: str
        Text displayed for the choice.
    votes: int
        Total number of votes received for this choice.
    channel_points_votes: int
        Number of votes received for this choice that used Channel Points.
    bits_votes: int
        Number of votes received for this choice that used Bits.
    """

    id: str
    title: str
    votes: int
    channel_points_votes: int
    bits_votes: int


class Poll(NamedTuple):
    """
    Represents a poll.

    Attributes
    ----------
    id: str
        ID of the poll.
    broadcaster: UserIdentity
        The broadcaster that created the poll.
    title: str
        Question displayed for the poll.
    choices: Tuple[PollChoice, ...]
        Array of the poll choices.
    bits_voting_enabled: bool
        Indicates if Bits can be used for voting.
    bits_per_vote: int
        Number of Bits required to vote once with Bits.
    channel_points_voting_enabled: bool
        Indicates if Channel Points can be used for voting.
    channel_points_per_vote: int
        Number of Channel Points required to vote once with Channel Points.
    status: str
        The poll status. Valid values are ACTIVE, COMPLETED, TERMINATED, ARCHIVED, MODERATED, INVALID.
    duration: int
        The length of the poll in seconds.
    started_at: datetime
        UTC timestamp for the poll's start time.
    ended_at: Optional[datetime]
        UTC timestamp for the poll's end time. None if the poll has not ended.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster: UserIdentity
    title: str
    choices: Tuple[PollChoice, ...]
    bits_voting_enabled: bool
    bits_per_vote: int
    channel_points_voting_enabled: bool
    channel_points_per_vote: int
    status: str
    duration: int
    started_at: datetime
    ended_at: Optional[datetime]
    raw: helix.Poll

    @classmethod
    def from_data(cls, data: helix.Poll) -> Poll:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        choices = tuple(
            PollChoice(
                id=choice['id'],
                title=choice['title'],
                votes=choice['votes'],
                channel_points_votes=choice['channel_points_votes'],
                bits_votes=choice['bits_votes']
            ) for choice in data['choices']
        )
        ended_at = from_iso_string(data['ended_at']) if data.get('ended_at') else None
        return cls(
            id=data['id'],
            broadcaster=broadcaster,
            title=data['title'],
            choices=choices,
            bits_voting_enabled=data['bits_voting_enabled'],
            bits_per_vote=data['bits_per_vote'],
            channel_points_voting_enabled=data['channel_points_voting_enabled'],
            channel_points_per_vote=data['channel_points_per_vote'],
            status=data['status'],
            duration=data['duration'],
            started_at=from_iso_string(data['started_at']),
            ended_at=ended_at,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Poll(id={self.id!r}, title={self.title!r})"


class Outcome(NamedTuple):
    """
    Represents a prediction outcome.

    Attributes
    ----------
    id: str
        ID of the outcome.
    title: str
        Text displayed for the outcome.
    users: int
        Number of unique users that chose the outcome.
    channel_points: int
        Number of Channel Points used for the outcome.
    top_predictors: Tuple[Contribution, ...]
        Array of users who were the top predictors.
    color: str
        Color for the outcome.
    """

    id: str
    title: str
    users: int
    channel_points: int
    top_predictors: Tuple[Contribution, ...]
    color: str


class Prediction(NamedTuple):
    """
    Represents a prediction.

    Attributes
    ----------
    id: str
        ID of the Prediction.
    broadcaster: UserIdentity
        The broadcaster.
    title: str
        Title for the Prediction.
    winning_outcome_id: Optional[str]
        ID of the winning outcome. None if not resolved.
    outcomes: Tuple[Outcome, ...]
        Array of possible outcomes for the Prediction.
    prediction_window: int
        Total duration of the Prediction (in seconds).
    status: str
        Status of the Prediction. Valid values: ACTIVE, RESOLVED, CANCELED, LOCKED.
    created_at: datetime
        UTC timestamp for when the Prediction was created.
    ended_at: Optional[datetime]
        UTC timestamp for when the Prediction ended. None if not ended.
    locked_at: Optional[datetime]
        UTC timestamp for when the Prediction was locked. None if not locked.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster: UserIdentity
    title: str
    winning_outcome_id: Optional[str]
    outcomes: Tuple[Outcome, ...]
    prediction_window: int
    status: str
    created_at: datetime
    ended_at: Optional[datetime]
    locked_at: Optional[datetime]
    raw: helix.Prediction

    @classmethod
    def from_data(cls, data: helix.Prediction) -> Prediction:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        outcomes = tuple(
            Outcome(
                id=outcome['id'],
                title=outcome['title'],
                users=outcome['users'],
                channel_points=outcome['channel_points'],
                top_predictors=tuple(
                    Contribution(
                        user=UserIdentity(
                            id=predictor['user_id'],
                            login=predictor['user_login'],
                            name=predictor['user_name']
                        ),
                        type=predictor['type'],
                        total=predictor['total']
                    ) for predictor in outcome.get('top_predictors', [])
                ),
                color=outcome['color']
            ) for outcome in data['outcomes']
        )
        ended_at = from_iso_string(data['ended_at']) if data.get('ended_at') else None
        locked_at = from_iso_string(data['locked_at']) if data.get('locked_at') else None
        return cls(
            id=data['id'],
            broadcaster=broadcaster,
            title=data['title'],
            winning_outcome_id=data.get('winning_outcome_id'),
            outcomes=outcomes,
            prediction_window=data['prediction_window'],
            status=data['status'],
            created_at=from_iso_string(data['created_at']),
            ended_at=ended_at,
            locked_at=locked_at,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"Prediction(id={self.id!r}, title={self.title!r})"


class StreamMarker(NamedTuple):
    """
    Represents a stream marker.

    Attributes
    ----------
    id: str
        An ID that identifies this marker.
    created_at: datetime
        The UTC date and time (in RFC3339 format) of when the moderator created this marker.
    created_by: str
        The ID of the user that created the marker.
    position_seconds: int
        The relative offset (in seconds) from where the marker is placed in the stream to the created_at time. Typically, the difference is a negative number.
    description: str
        A short description of the marker.
    url: str
        A URL that opens the video in the Highlighter at the marker's location.
    video_id: str
        The ID of the video that the marker is placed in.
    label: str
        The label of the marker, for example "Best Moment".
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    created_at: datetime
    created_by: str
    position_seconds: int
    description: str
    url: str
    video_id: str
    label: str
    raw: helix.StreamMarker

    @classmethod
    def from_data(cls, data: helix.StreamMarker) -> StreamMarker:
        return cls(
            id=data['id'],
            created_at=from_iso_string(data['created_at']),
            created_by=data['created_by'],
            position_seconds=data['position_seconds'],
            description=data['description'],
            url=data['URL'],
            video_id=data['video_id'],
            label=data['label'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StreamMarker(id={self.id!r}, label={self.label!r})"


class UserSubscription(NamedTuple):
    """
    Represents a user subscription.

    Attributes
    ----------
    broadcaster: UserIdentity
        The broadcaster.
    gifter: UserIdentity
        The user who gifted the subscription. Empty fields if not gifted.
    is_gift: bool
        Flag indicating if the subscription is a gift.
    user: UserIdentity
        The subscriber.
    tier: str
        The subscription tier. Possible values are 1000 (Tier 1), 2000 (Tier 2), 3000 (Tier 3).
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster: UserIdentity
    gifter: UserIdentity
    is_gift: bool
    user: UserIdentity
    tier: str
    raw: helix.UserSubscription

    @classmethod
    def from_data(cls, data: helix.UserSubscription) -> UserSubscription:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        gifter = UserIdentity(
            id=data['gifter_id'],
            login=data['gifter_login'],
            name=data['gifter_name']
        )
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        return cls(
            broadcaster=broadcaster,
            gifter=gifter,
            is_gift=data['is_gift'],
            user=user,
            tier=data['tier'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"UserSubscription(user_id={self.user.id!r}, tier={self.tier!r})"


class UserExtension(NamedTuple):
    """
    Represents a user extension.

    Attributes
    ----------
    id: str
        The ID of the extension.
    version: str
        The extension version.
    can_activate: bool
        Indicates whether the user can install or activate the extension.
    name: str
        The extension name.
    types: Tuple[str, ...]
        The types of extensions, such as panel, overlay, component.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    version: str
    can_activate: bool
    name: str
    types: Tuple[str, ...]
    raw: helix.UserExtension

    @classmethod
    def from_data(cls, data: helix.UserExtension) -> UserExtension:
        return cls(
            id=data['id'],
            version=data['version'],
            can_activate=data['can_activate'],
            name=data['name'],
            types=tuple(data['type']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"UserExtension(id={self.id!r}, name={self.name!r})"


class ExtensionComponent(NamedTuple):
    """
    Represents an extension component configuration.

    Attributes
    ----------
    active: bool
        Whether the component is active.
    id: str
        The component ID.
    version: str
        The component version.
    name: str
        The component name.
    x: int
        The x coordinate.
    y: int
        The y coordinate.
    """

    active: bool
    id: str
    version: str
    name: str
    x: int
    y: int


class ExtensionPanel(NamedTuple):
    """
    Represents an extension panel configuration.

    Attributes
    ----------
    active: bool
        Whether the panel is active.
    id: str
        The panel ID.
    version: str
        The panel version.
    name: str
        The panel name.
    """

    active: bool
    id: str
    version: str
    name: str


class ExtensionOverlay(NamedTuple):
    """
    Represents an extension overlay configuration.

    Attributes
    ----------
    active: bool
        Whether the overlay is active.
    id: str
        The overlay ID.
    version: str
        The overlay version.
    name: str
        The overlay name.
    """

    active: bool
    id: str
    version: str
    name: str


class ActiveUserExtension(NamedTuple):
    """
    Represents active user extensions.

    Attributes
    ----------
    panel: Tuple[ExtensionPanel, ...]
        The active panel extensions.
    overlay: Tuple[ExtensionOverlay, ...]
        The active overlay extensions.
    component: Tuple[ExtensionComponent, ...]
        The active component extensions.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    panel: Tuple[ExtensionPanel, ...]
    overlay: Tuple[ExtensionOverlay, ...]
    component: Tuple[ExtensionComponent, ...]
    raw: helix.ActiveUserExtension

    @classmethod
    def from_data(cls, data: helix.ActiveUserExtension) -> ActiveUserExtension:
        panels = tuple(
            ExtensionPanel(
                active=panel['active'],
                id=panel['id'],
                version=panel['version'],
                name=panel['name']
            ) for panel in data.get('panel', [])
        )
        overlays = tuple(
            ExtensionOverlay(
                active=overlay['active'],
                id=overlay['id'],
                version=overlay['version'],
                name=overlay['name']
            ) for overlay in data.get('overlay', [])
        )
        components = tuple(
            ExtensionComponent(
                active=component['active'],
                id=component['id'],
                version=component['version'],
                name=component['name'],
                x=component['x'],
                y=component['y']
            ) for component in data.get('component', [])
        )
        return cls(
            panel=panels,
            overlay=overlays,
            component=components,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ActiveUserExtension()"


class ExtensionTransaction(NamedTuple):
    """
    Represents an extension transaction.

    Attributes
    ----------
    id: str
        An ID that identifies the transaction.
    timestamp: datetime
        The UTC date and time (in RFC3339 format) of the transaction.
    broadcaster: UserIdentity
        The broadcaster that owns the channel where the transaction occurred.
    user: UserIdentity
        The user that purchased the digital product.
    product_type: str
        The type of transaction. Possible values are: BITS_IN_EXTENSION.
    domain: str
        Set to twitch.ext. + the extension's ID.
    broadcast: bool
        A Boolean value that determines whether the data was broadcast to all instances of the extension.
    expiration: str
        This field is always empty since you may purchase only unexpired products.
    sku: str
        An ID that identifies the digital product.
    cost: Amount
        Contains details about the digital product's cost.
    display_name: str
        The name of the digital product.
    in_development: bool
        A Boolean value that determines whether the product is in development.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    timestamp: datetime
    broadcaster: UserIdentity
    user: UserIdentity
    product_type: str
    domain: str
    broadcast: bool
    expiration: str
    sku: str
    cost: Amount
    display_name: str
    in_development: bool
    raw: helix.ExtensionTransaction

    @classmethod
    def from_data(cls, data: helix.ExtensionTransaction) -> ExtensionTransaction:
        broadcaster = UserIdentity(
            id=data['broadcaster_id'],
            login=data['broadcaster_login'],
            name=data['broadcaster_name']
        )
        user = UserIdentity(
            id=data['user_id'],
            login=data['user_login'],
            name=data['user_name']
        )
        product_data = data['product_data']
        cost = Amount(
            value=product_data['cost']['amount'],
            decimal_places=0,  # Assuming no decimal for bits
            currency=product_data['cost']['type']
        )
        return cls(
            id=data['id'],
            timestamp=from_iso_string(data['timestamp']),
            broadcaster=broadcaster,
            user=user,
            product_type=data['product_type'],
            domain=product_data['domain'],
            broadcast=product_data['broadcast'],
            expiration=product_data['expiration'],
            sku=product_data['sku'],
            cost=cost,
            display_name=product_data['displayName'],
            in_development=product_data['inDevelopment'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ExtensionTransaction(id={self.id!r})"


class ExtensionBitsProduct(NamedTuple):
    """
    Represents an extension Bits product.

    Attributes
    ----------
    sku: str
        An ID that identifies the digital product.
    cost: Amount
        Contains details about the digital product's cost.
    name: str
        The name of the product.
    in_development: bool
        A Boolean value that determines whether the product is in development.
    display_name: str
        The product's display name.
    expiration: str
        The expiration date.
    is_broadcast: bool
        Whether the product is broadcast.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    sku: str
    cost: Amount
    name: str
    in_development: bool
    display_name: str
    expiration: str
    is_broadcast: bool
    raw: helix.ExtensionBitsProduct

    @classmethod
    def from_data(cls, data: helix.ExtensionBitsProduct) -> ExtensionBitsProduct:
        cost = Amount(
            value=data['cost']['amount'],
            decimal_places=0,
            currency=data['cost']['type']
        )
        return cls(
            sku=data['sku'],
            cost=cost,
            name=data['name'],
            in_development=data['in_development'],
            display_name=data['display_name'],
            expiration=data['expiration'],
            is_broadcast=data['is_broadcast'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ExtensionBitsProduct(sku={self.sku!r}, name={self.name!r})"