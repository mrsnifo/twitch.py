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

from typing import NamedTuple, TYPE_CHECKING, Literal, Tuple, Optional
from ..utils import from_iso_string
from types import MappingProxyType
from ..models import UserIdentity
import datetime

if TYPE_CHECKING:
    from ..types import eventsub

__all__ = (
    'AutomodHoldEventV1',
    'AutomodHoldEventV2',
    'AutomodUpdateEventV1',
    'AutomodUpdateEventV2',
    'AutomodSettingsUpdateEvent',
    'AutomodTermsUpdateEvent',

    'ChannelBitsUseEvent',

    'ChannelUpdateEvent',
    'ChannelFollowEvent',
    'ChannelAdBreakBeginEvent',

    'ChannelChatClearEvent',
    'ChannelChatClearUserMessagesEvent',
    'ChannelChatMessageEvent',
    'ChannelChatMessageDeleteEvent',
    'ChannelChatNotificationEvent',
    'ChannelChatSettingsUpdateEvent',
    'ChannelChatUserMessageHoldEvent',
    'ChannelChatUserMessageUpdateEvent',

    'ChannelSharedChatBeginEvent',
    'ChannelSharedChatUpdateEvent',
    'ChannelSharedChatEndEvent',

    'ChannelSubscribeEvent',
    'ChannelSubscriptionEndEvent',
    'ChannelSubscriptionGiftEvent',
    'ChannelSubscriptionMessageEvent',

    'ChannelCheerEvent',

    'ChannelRaidEvent',

    'ChannelBanEvent',
    'ChannelUnbanEvent',
    'ChannelUnbanRequestCreateEvent',
    'ChannelUnbanRequestResolveEvent',
    'ChannelModerateEventV1',
    'ChannelModerateEventV2',
    'ChannelModeratorAddEvent',
    'ChannelModeratorRemoveEvent',

    'ChannelPointsAutomaticRewardRedemptionAddEventV1',
    'ChannelPointsAutomaticRewardRedemptionAddEventV2',
    'ChannelPointsCustomRewardAddEvent',
    'ChannelPointsCustomRewardUpdateEvent',
    'ChannelPointsCustomRewardRemoveEvent',
    'ChannelPointsCustomRewardRedemptionAddEvent',
    'ChannelPointsCustomRewardRedemptionUpdateEvent',

    'ChannelPollBeginEvent',
    'ChannelPollProgressEvent',
    'ChannelPollEndEvent',

    'ChannelPredictionBeginEvent',
    'ChannelPredictionProgressEvent',
    'ChannelPredictionLockEvent',
    'ChannelPredictionEndEvent',

    'ChannelSuspiciousUserMessageEvent',
    'ChannelSuspiciousUserUpdateEvent',

    'ChannelVipAddEvent',
    'ChannelVipRemoveEvent',

    'ChannelWarningAcknowledgeEvent',
    'ChannelWarningSendEvent',

    'ChannelCharityCampaignDonationEvent',
    'ChannelCharityCampaignStartEvent',
    'ChannelCharityCampaignProgressEvent',
    'ChannelCharityCampaignStopEvent',

    'DropEntitlementGrantEvent',
    'ExtensionBitsTransactionCreateEvent',

    'ChannelGoalBeginEvent',
    'ChannelGoalProgressEvent',
    'ChannelGoalEndEvent',

    'ChannelShieldModeBeginEvent',
    'ChannelShieldModeEndEvent',

    'ChannelShoutoutCreateEvent',
    'ChannelShoutoutReceiveEvent',

    'StreamOnlineEvent',
    'StreamOfflineEvent',

    'UserAuthorizationGrantEvent',
    'UserAuthorizationRevokeEvent',
    'UserUpdateEvent',
    'UserWhisperMessageEvent',
)


class EventEmote(NamedTuple):
    """
    Represents an emote in an event.

    Attributes
    ----------
    id: str
        Unique identifier for the emote.
    emote_set_id: str
        Identifier for the emote set this emote belongs to.
    owner_id: Optional[str]
        Identifier of the emote owner.
    format: Optional[Tuple[Literal['animated', 'static'], ...]]
        Available formats for the emote.
    """

    id: str
    emote_set_id: str
    owner_id: Optional[str] = None
    format: Optional[Tuple[Literal['animated', 'static'], ...]] = None

    @classmethod
    def from_data(cls, data: eventsub.Emote) -> EventEmote:
        format_data = data.get('format')
        format_tuple = tuple(format_data) if format_data is not None else None
        return cls(
            id=data['id'],
            emote_set_id=data['emote_set_id'],
            owner_id=data.get('owner_id'),
            format=format_tuple
        )

    def __eq__(self, other: EventEmote) -> bool:
        if not isinstance(other, EventEmote):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"EventEmote(id={self.id!r}, emote_set_id={self.emote_set_id!r})"


class EventCheermote(NamedTuple):
    """
    Represents a cheermote in an event.

    Attributes
    ----------
    prefix: str
        Cheermote prefix text.
    bits: int
        Number of bits associated with the cheermote.
    tier: int
        Tier level of the cheermote.
    """

    prefix: str
    bits: int
    tier: int

    @classmethod
    def from_data(cls, data: eventsub.Cheermote) -> EventCheermote:
        return cls(
            prefix=data['prefix'],
            bits=data['bits'],
            tier=data['tier']
        )

    def __eq__(self, other: EventCheermote) -> bool:
        if not isinstance(other, EventCheermote):
            return False
        return self.prefix == other.prefix and self.bits == other.bits

    def __hash__(self) -> int:
        return hash((self.prefix, self.bits))


class EventMessageFragment(NamedTuple):
    """
    Represents a fragment of a message in an event.

    Attributes
    ----------
    text: str
        Text content of the fragment.
    type: Optional[Literal['text', 'emote', 'cheermote', 'mention']]
        Type of the message fragment.
    emote: Optional[EventEmote]
        Emote data if the fragment is an emote.
    cheermote: Optional[EventCheermote]
        Cheermote data if the fragment is a cheermote.
    mention: Optional[UserIdentity]
        User data if the fragment is a mention.
    """

    text: str
    type: Optional[Literal['text', 'emote', 'cheermote', 'mention']] = None
    emote: Optional[EventEmote] = None
    cheermote: Optional[EventCheermote] = None
    mention: Optional[UserIdentity] = None

    @classmethod
    def from_data(cls, data: eventsub.MessageFragment) -> EventMessageFragment:
        emote_data = data.get('emote')
        cheermote_data = data.get('cheermote')
        mention_data = data.get('mention')
        return cls(
            text=data['text'],
            type=data.get('type'),
            emote=EventEmote.from_data(emote_data) if emote_data is not None else None,
            cheermote=EventCheermote.from_data(cheermote_data) if cheermote_data is not None else None,
            mention=UserIdentity(
                id=mention_data['user_id'],
                login=mention_data['user_login'],
                name=mention_data['user_name']
            ) if mention_data is not None else None
        )

    def __eq__(self, other: EventMessageFragment) -> bool:
        if not isinstance(other, EventMessageFragment):
            return False
        return self.text == other.text and self.type == other.type

    def __hash__(self) -> int:
        return hash((self.text, self.type))

    def __repr__(self) -> str:
        return f"EventMessageFragment(text={self.text!r}, type={self.type!r})"


class EventMessage(NamedTuple):
    """
    Represents a message in an event.

    Attributes
    ----------
    text: str
        Full text content of the message.
    fragments: Tuple[EventMessageFragment, ...]
        Individual fragments that make up the message.
    """

    text: str
    fragments: Tuple[EventMessageFragment, ...]

    @classmethod
    def from_data(cls, data: eventsub.Message) -> EventMessage:
        fragments_data = data.get('fragments', [])
        fragments_tuple = tuple(EventMessageFragment.from_data(fragment) for fragment in fragments_data)
        return cls(
            text=data['text'],
            fragments=fragments_tuple
        )

    def __str__(self) -> str:
        return self.text

    def __hash__(self) -> int:
        return hash(self.text)

    def __repr__(self) -> str:
        return f"EventMessage(text={self.text!r})"


class EventChatBadge(NamedTuple):
    """
    Represents a chat badge in an event.

    Attributes
    ----------
    set_id: str
        Identifier for the badge set.
    id: str
        Unique identifier for the badge.
    info: str
        Additional information about the badge.
    """

    set_id: str
    id: str
    info: str

    @classmethod
    def from_data(cls, data: eventsub.ChatBadge) -> EventChatBadge:
        return cls(
            set_id=data['set_id'],
            id=data['id'],
            info=data['info']
        )


class EventMoneyAmount(NamedTuple):
    """
    Represents a monetary amount in an event.

    Attributes
    ----------
    value: int
        Monetary value as an integer.
    decimal_places: int
        Number of decimal places for the currency.
    currency: str
        Currency code.
    """

    value: int
    decimal_places: int
    currency: str

    @classmethod
    def from_data(cls, data: eventsub.MoneyAmount) -> EventMoneyAmount:
        return cls(
            value=data['value'],
            decimal_places=data['decimal_places'],
            currency=data['currency']
        )


class EventAutomodBoundary(NamedTuple):
    """
    Represents a boundary in automod detection.

    Attributes
    ----------
    start_pos: int
        Starting position of the boundary.
    end_pos: int
        Ending position of the boundary.
    """

    start_pos: int
    end_pos: int

    @classmethod
    def from_data(cls, data: eventsub.AutomodBoundary) -> EventAutomodBoundary:
        return cls(
            start_pos=data['start_pos'],
            end_pos=data['end_pos']
        )


class EventAutomod(NamedTuple):
    """
    Represents automod detection information.

    Attributes
    ----------
    category: str
        Category of automod detection.
    level: int
        Severity level of the detection.
    boundaries: Tuple[EventAutomodBoundary, ...]
        Text boundaries where violations were detected.
    """

    category: str
    level: int
    boundaries: Tuple[EventAutomodBoundary, ...]

    @classmethod
    def from_data(cls, data: eventsub.Automod) -> EventAutomod:
        boundaries_data = data.get('boundaries', [])
        boundaries_tuple = tuple(EventAutomodBoundary.from_data(boundary) for boundary in boundaries_data)
        return cls(
            category=data['category'],
            level=data['level'],
            boundaries=boundaries_tuple
        )

    def __repr__(self) -> str:
        return f"EventAutomod(category={self.category!r}, level={self.level})"


class EventBlockedTerm(NamedTuple):
    """
    Represents a blocked term detection.

    Attributes
    ----------
    term_id: str
        Unique identifier for the blocked term.
    boundary: EventAutomodBoundary
        Text boundary where the term was found.
    owner_broadcaster_user: UserIdentity
        User who owns the blocked term configuration.
    """

    term_id: str
    boundary: EventAutomodBoundary
    owner_broadcaster_user: UserIdentity

    @classmethod
    def from_data(cls, data: eventsub.BlockedTerm) -> EventBlockedTerm:
        return cls(
            term_id=data['term_id'],
            boundary=EventAutomodBoundary.from_data(data['boundary']),
            owner_broadcaster_user=UserIdentity(
                id=data['owner_broadcaster_user_id'],
                login=data['owner_broadcaster_user_login'],
                name=data['owner_broadcaster_user_name']
            )
        )

    def __eq__(self, other: EventBlockedTerm) -> bool:
        if not isinstance(other, EventBlockedTerm):
            return False
        return self.term_id == other.term_id

    def __hash__(self) -> int:
        return hash(self.term_id)

    def __repr__(self) -> str:
        return f"EventBlockedTerm(term_id={self.term_id!r}, owner={self.owner_broadcaster_user.login!r})"


class EventBlockedTerms(NamedTuple):
    """
    Represents a collection of blocked terms found in content.

    Attributes
    ----------
    terms_found: Tuple[EventBlockedTerm, ...]
        Collection of blocked terms that were detected.
    """

    terms_found: Tuple[EventBlockedTerm, ...]

    @property
    def total_terms_found(self) -> int:
        """
        Return the total number of blocked terms found.

        Returns
        -------
        int
            The number of blocked terms in the collection.
        """
        return len(self.terms_found)

    @classmethod
    def from_data(cls, data: eventsub.BlockedTerms) -> EventBlockedTerms:
        terms_data = data.get('terms_found', [])
        terms_tuple = tuple(EventBlockedTerm.from_data(term) for term in terms_data)
        return cls(terms_found=terms_tuple)

    def __repr__(self) -> str:
        return f"EventBlockedTerms(total_terms_found={self.total_terms_found})"


class AutomodHoldEventV1(NamedTuple):
    """
    Represents an automod hold event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User whose message was held.
    message_id: str
        Unique identifier for the held message.
    message: EventMessage
        Content of the held message.
    category: str
        Automod category that triggered the hold.
    level: int
        Severity level of the automod detection.
    held_at: datetime.datetime
        Timestamp when the message was held.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    message_id: str
    message: EventMessage
    category: str
    level: int
    held_at: datetime.datetime
    raw: eventsub.AutomodHoldEventV1

    @classmethod
    def from_data(cls, data: eventsub.AutomodHoldEventV1) -> AutomodHoldEventV1:
        message_data = data['message']
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(message_data),
            category=data['category'],
            level=data['level'],
            held_at=from_iso_string(data['held_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: AutomodHoldEventV1) -> bool:
        if not isinstance(other, AutomodHoldEventV1):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return (f"AutomodHoldEventV1("
                f"message_id={self.message_id!r}, user={self.user.login!r}, category={self.category!r})")


class AutomodHoldEventV2(NamedTuple):
    """
    Represents an automod hold event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User whose message was held.
    message_id: str
        Unique identifier for the held message.
    message: EventMessage
        Content of the held message.
    held_at: datetime.datetime
        Timestamp when the message was held.
    reason: Literal['automod', 'blocked_term']
        Reason why the message was held.
    automod: Optional[EventAutomod]
        Automod detection details if reason is automod.
    blocked_term: Optional[EventBlockedTerms]
        Blocked term details if reason is blocked_term.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    message_id: str
    message: EventMessage
    held_at: datetime.datetime
    reason: Literal['automod', 'blocked_term']
    raw: MappingProxyType
    automod: Optional[EventAutomod] = None
    blocked_term: Optional[EventBlockedTerms] = None

    @classmethod
    def from_data(cls, data: eventsub.AutomodHoldEventV2) -> AutomodHoldEventV2:
        message_data = data['message']
        automod_data = data.get('automod')
        blocked_term_data = data.get('blocked_term')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(message_data),
            held_at=from_iso_string(data['held_at']),
            reason=data['reason'],
            automod=EventAutomod.from_data(automod_data) if automod_data is not None else None,
            blocked_term=EventBlockedTerms.from_data(blocked_term_data) if blocked_term_data is not None else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: AutomodHoldEventV2) -> bool:
        if not isinstance(other, AutomodHoldEventV2):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"AutomodHoldEventV2(message_id={self.message_id!r}, user={self.user.login!r}, reason={self.reason!r})"


class AutomodUpdateEventV1(NamedTuple):
    """
    Represents an automod update event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User whose message was updated.
    moderator_user: UserIdentity
        Moderator who performed the update.
    message_id: str
        Unique identifier for the updated message.
    message: EventMessage
        Content of the updated message.
    category: str
        Automod category that was involved.
    level: int
        Severity level of the automod detection.
    status: Literal['Approved', 'Denied', 'Expired']
        Final status of the message.
    held_at: datetime.datetime
        Timestamp when the message was originally held.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    message_id: str
    message: EventMessage
    category: str
    level: int
    status: Literal['Approved', 'Denied', 'Expired']
    held_at: datetime.datetime
    raw: eventsub.AutomodUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.AutomodUpdateEventV1) -> AutomodUpdateEventV1:
        message_data = data['message']
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(message_data),
            category=data['category'],
            level=data['level'],
            status=data['status'],
            held_at=from_iso_string(data['held_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: AutomodUpdateEventV1) -> bool:
        if not isinstance(other, AutomodUpdateEventV1):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"AutomodUpdateEventV1(message_id={self.message_id!r}, status={self.status!r})"


class AutomodUpdateEventV2(NamedTuple):
    """
    Represents an automod update event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User whose message was updated.
    moderator_user: UserIdentity
        Moderator who performed the update.
    message_id: str
        Unique identifier for the updated message.
    message: EventMessage
        Content of the updated message.
    status: Literal['Approved', 'Denied', 'Expired']
        Final status of the message.
    held_at: datetime.datetime
        Timestamp when the message was originally held.
    reason: Literal['automod', 'blocked_term']
        Reason why the message was originally held.
    automod: Optional[EventAutomod]
        Automod detection details if reason is automod.
    blocked_term: Optional[EventBlockedTerms]
        Blocked term details if reason is blocked_term.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    message_id: str
    message: EventMessage
    status: Literal['Approved', 'Denied', 'Expired']
    held_at: datetime.datetime
    reason: Literal['automod', 'blocked_term']
    raw: eventsub.AutomodUpdateEventV2
    automod: Optional[EventAutomod] = None
    blocked_term: Optional[EventBlockedTerms] = None

    @classmethod
    def from_data(cls, data: eventsub.AutomodUpdateEventV2) -> AutomodUpdateEventV2:
        message_data = data['message']
        automod_data = data.get('automod')
        blocked_term_data = data.get('blocked_term')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(message_data),
            status=data['status'],
            held_at=from_iso_string(data['held_at']),
            reason=data['reason'],
            automod=EventAutomod.from_data(automod_data) if automod_data is not None else None,
            blocked_term=EventBlockedTerms.from_data(blocked_term_data) if blocked_term_data is not None else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: AutomodUpdateEventV2) -> bool:
        if not isinstance(other, AutomodUpdateEventV2):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"AutomodUpdateEventV2(message_id={self.message_id!r}, status={self.status!r}, reason={self.reason!r})"


class AutomodSettingsUpdateEvent(NamedTuple):
    """
    Represents an automod settings update event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who updated the settings.
    bullying: int
        Bullying detection level setting.
    overall_level: Optional[int]
        Overall automod level setting.
    disability: int
        Disability-related content detection level.
    race_ethnicity_or_religion: int
        Race, ethnicity, or religion content detection level.
    misogyny: int
        Misogyny detection level setting.
    sexuality_sex_or_gender: int
        Sexuality, sex, or gender content detection level.
    aggression: int
        Aggression detection level setting.
    sex_based_terms: int
        Sex-based terms detection level setting.
    swearing: int
        Swearing detection level setting.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    bullying: int
    overall_level: Optional[int]
    disability: int
    race_ethnicity_or_religion: int
    misogyny: int
    sexuality_sex_or_gender: int
    aggression: int
    sex_based_terms: int
    swearing: int
    raw: eventsub.AutomodSettingsUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.AutomodSettingsUpdateEventV1) -> AutomodSettingsUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            bullying=data['bullying'],
            overall_level=data.get('overall_level'),
            disability=data['disability'],
            race_ethnicity_or_religion=data['race_ethnicity_or_religion'],
            misogyny=data['misogyny'],
            sexuality_sex_or_gender=data['sexuality_sex_or_gender'],
            aggression=data['aggression'],
            sex_based_terms=data['sex_based_terms'],
            swearing=data['swearing'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return (f"AutomodSettingsUpdateEvent(broadcaster={self.broadcaster_user.login!r},"
                f" moderator={self.moderator_user.login!r})")


class AutomodTermsUpdateEvent(NamedTuple):
    """
    Represents an automod terms update event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who updated the terms.
    action: Literal['add_permitted', 'remove_permitted', 'add_blocked', 'remove_blocked']
        Action performed on the terms.
    from_automod: bool
        Whether the update originated from automod.
    terms: Tuple[str, ...]
        Collection of terms that were updated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    action: Literal['add_permitted', 'remove_permitted', 'add_blocked', 'remove_blocked']
    from_automod: bool
    terms: Tuple[str, ...]
    raw: eventsub.AutomodTermsUpdateEventV1

    @property
    def total_terms(self) -> int:
        """
        Return the total number of terms in the collection.

        Returns
        -------
        int
            The number of terms that were updated.
        """
        return len(self.terms)

    @classmethod
    def from_data(cls, data: eventsub.AutomodTermsUpdateEventV1) -> AutomodTermsUpdateEvent:
        terms_data = data.get('terms', [])
        terms_tuple = tuple(terms_data)
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            action=data['action'],
            from_automod=data['from_automod'],
            terms=terms_tuple,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return (f"AutomodTermsUpdateEvent(action={self.action!r}, total_terms={self.total_terms},"
                f" from_automod={self.from_automod})")


class ChannelAdBreakBeginEvent(NamedTuple):
    """
    Represents a channel ad break begin event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    duration_seconds: int
        Duration of the ad break in seconds.
    started_at: datetime.datetime
        Timestamp when the ad break started.
    is_automatic: bool
        Whether the ad break was automatically triggered.
    requester_user: UserIdentity
        User who requested the ad break.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    duration_seconds: int
    started_at: datetime.datetime
    is_automatic: bool
    requester_user: UserIdentity
    raw: eventsub.ChannelAdBreakBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelAdBreakBeginEventV1) -> ChannelAdBreakBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            duration_seconds=data['duration_seconds'],
            started_at=from_iso_string(data['started_at']),
            is_automatic=data['is_automatic'],
            requester_user=UserIdentity(
                id=data['requester_user_id'],
                login=data['requester_user_login'],
                name=data['requester_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelAdBreakBeginEvent(broadcaster={self.broadcaster_user.login!r}, duration={self.duration_seconds})"


class ChannelBanEvent(NamedTuple):
    """
    Represents a channel ban event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was banned.
    moderator_user: UserIdentity
        Moderator who performed the ban.
    reason: str
        Reason for the ban.
    banned_at: datetime.datetime
        Timestamp when the user was banned.
    ends_at: Optional[datetime.datetime]
        Timestamp when the ban expires
    is_permanent: bool
        Whether the ban is permanent.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    reason: str
    banned_at: datetime.datetime
    ends_at: Optional[datetime.datetime]
    is_permanent: bool
    raw: eventsub.ChannelBanEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelBanEventV1) -> ChannelBanEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            reason=data['reason'],
            banned_at=from_iso_string(data['banned_at']),
            ends_at=from_iso_string(data['ends_at']) if data['ends_at'] else None,
            is_permanent=data['is_permanent'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelBanEvent) -> bool:
        if not isinstance(other, ChannelBanEvent):
            return False
        return self.broadcaster_user.id == other.broadcaster_user.id and self.user.id == other.user.id

    def __hash__(self) -> int:
        return hash((self.broadcaster_user.id, self.user.id))

    def __repr__(self) -> str:
        return f"ChannelBanEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class EventPowerUp(NamedTuple):
    """
    Represents a power-up event data.

    Attributes
    ----------
    type: Literal['message_effect', 'celebration', 'gigantify_an_emote']
        Type of power-up.
    emote: Optional[EventEmote]
        Emote associated with the power-up
    message_effect_id: Optional[str]
        Unique identifier for the message effect
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    type: Literal['message_effect', 'celebration', 'gigantify_an_emote']
    emote: Optional[EventEmote]
    message_effect_id: Optional[str]
    raw: eventsub.PowerUp

    @classmethod
    def from_data(cls, data: eventsub.PowerUp) -> EventPowerUp:
        emote_data = data.get('emote')
        return cls(
            type=data['type'],
            emote=EventEmote.from_data(emote_data) if emote_data else None,
            message_effect_id=data.get('message_effect_id'),
            raw=MappingProxyType(data)  # type: ignore
        )


class ChannelBitsUseEvent(NamedTuple):
    """
    Represents a channel bits use event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who used the bits.
    bits: int
        Number of bits used.
    type: Literal['cheer', 'power_up']
        Type of bits usage.
    message: Optional[EventMessage]
        Message associated with the bits usage
    power_up: Optional[EventPowerUp]
        Power-up associated with the bits usage
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    bits: int
    type: Literal['cheer', 'power_up']
    message: Optional[EventMessage]
    power_up: Optional[EventPowerUp]
    raw: eventsub.ChannelBitsUseEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelBitsUseEventV1) -> ChannelBitsUseEvent:
        message_data = data.get('message')
        power_up_data = data.get('power_up')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            bits=data['bits'],
            type=data['type'],
            message=EventMessage.from_data(message_data) if message_data else None,
            power_up=EventPowerUp.from_data(power_up_data) if power_up_data else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelBitsUseEvent(user={self.user.login!r}, bits={self.bits}, type={self.type!r})"


class ChannelChatClearEvent(NamedTuple):
    """
    Represents a channel chat clear event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    raw: eventsub.ChannelChatClearEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatClearEventV1) -> ChannelChatClearEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelChatClearEvent(broadcaster={self.broadcaster_user.login!r})"


class ChannelChatClearUserMessagesEvent(NamedTuple):
    """
    Represents a channel chat clear user messages event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    target_user: UserIdentity
        User whose messages were cleared.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    target_user: UserIdentity
    raw: eventsub.ChannelChatClearUserMessagesEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatClearUserMessagesEventV1) -> ChannelChatClearUserMessagesEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            target_user=UserIdentity(
                id=data['target_user_id'],
                login=data['target_user_login'],
                name=data['target_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelChatClearUserMessagesEvent(target_user={self.target_user.login!r})"


class EventReply(NamedTuple):
    """
    Represents a reply to a chat message.

    Attributes
    ----------
    parent_message_id: str
        ID of the parent message being replied to.
    parent_message_body: str
        Body text of the parent message.
    parent_user: UserIdentity
        User who sent the parent message.
    thread_message_id: str
        ID of the thread message.
    thread_user: UserIdentity
        User who sent the thread message.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    parent_message_id: str
    parent_message_body: str
    parent_user: UserIdentity
    thread_message_id: str
    thread_user: UserIdentity
    raw: eventsub.Reply

    @classmethod
    def from_data(cls, data: eventsub.Reply) -> EventReply:
        return cls(
            parent_message_id=data['parent_message_id'],
            parent_message_body=data['parent_message_body'],
            parent_user=UserIdentity(
                id=data['parent_user_id'],
                login=data['parent_user_login'],
                name=data['parent_user_name']
            ),
            thread_message_id=data['thread_message_id'],
            thread_user=UserIdentity(
                id=data['thread_user_id'],
                login=data['thread_user_login'],
                name=data['thread_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )


class ChannelChatMessageEvent(NamedTuple):
    """
    Represents a channel chat message event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    chatter: UserIdentity
        User who sent the message.
    message_id: str
        Unique identifier for the message.
    message: EventMessage
        Message content and metadata.
    message_type: Literal['text', 'channel_points_highlighted', 'channel_points_sub_only', 'user_intro', 'power_ups_message_effect', 'power_ups_gigantified_emote']
        Type of the chat message.
    badges: Tuple[EventChatBadge, ...]
        Chat badges associated with the user.
    cheer: Optional[dict[str, int]]
        Cheer information if the message contains bits.
    color: str
        Color of the user's name in chat.
    reply: Optional[EventReply]
        Reply information if this message is a reply.
    channel_points_custom_reward_id: Optional[str]
        Custom reward ID if message is associated with channel points.
    source_broadcaster_user: Optional[UserIdentity]
        Source broadcaster user for shared chat messages.
    source_message_id: Optional[str]
        Source message ID for shared chat messages.
    source_badges: Optional[Tuple[EventChatBadge, ...]]
        Source badges for shared chat messages.
    is_source_only: Optional[bool]
        Whether the message is source-only for shared chat.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    chatter: UserIdentity
    message_id: str
    message: EventMessage
    message_type: Literal['text', 'channel_points_highlighted', 'channel_points_sub_only',
                         'user_intro', 'power_ups_message_effect', 'power_ups_gigantified_emote']
    badges: Tuple[EventChatBadge, ...]
    cheer: Optional[dict[str, int]]
    color: str
    reply: Optional[EventReply]
    channel_points_custom_reward_id: Optional[str]
    source_broadcaster_user: Optional[UserIdentity]
    source_message_id: Optional[str]
    source_badges: Optional[Tuple[EventChatBadge, ...]]
    is_source_only: Optional[bool]
    raw: eventsub.ChannelChatMessageEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatMessageEventV1) -> ChannelChatMessageEvent:
        source_broadcaster_data = data.get('source_broadcaster_user_id')
        reply_data = data.get('reply')
        badges_data = data.get('badges', [])
        source_badges_data = data.get('source_badges', [])
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            chatter=UserIdentity(
                id=data['chatter_user_id'],
                login=data['chatter_user_login'],
                name=data['chatter_user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(data['message']),
            message_type=data['message_type'],
            badges=tuple(EventChatBadge.from_data(badge) for badge in badges_data),
            cheer=data.get('cheer'),
            color=data['color'],
            reply=EventReply.from_data(reply_data) if reply_data else None,
            channel_points_custom_reward_id=data.get('channel_points_custom_reward_id'),
            source_broadcaster_user=UserIdentity(
                id=data['source_broadcaster_user_id'],
                login=data['source_broadcaster_user_login'],
                name=data['source_broadcaster_user_name']
            ) if source_broadcaster_data else None,
            source_message_id=data.get('source_message_id'),
            source_badges=tuple(EventChatBadge.from_data(badge) for badge in source_badges_data)
            if source_badges_data else None,
            is_source_only=data.get('is_source_only'),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelChatMessageEvent) -> bool:
        if not isinstance(other, ChannelChatMessageEvent):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"ChannelChatMessageEvent(message_id={self.message_id!r}, chatter={self.chatter!r})"


class ChannelChatMessageDeleteEvent(NamedTuple):
    """
    Represents a channel chat message delete event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    target_user: UserIdentity
        User whose message was deleted.
    message_id: str
        ID of the deleted message.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    target_user: UserIdentity
    message_id: str
    raw: eventsub.ChannelChatMessageDeleteEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatMessageDeleteEventV1) -> ChannelChatMessageDeleteEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            target_user=UserIdentity(
                id=data['target_user_id'],
                login=data['target_user_login'],
                name=data['target_user_name']
            ),
            message_id=data['message_id'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelChatMessageDeleteEvent) -> bool:
        if not isinstance(other, ChannelChatMessageDeleteEvent):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"ChannelChatMessageDeleteEvent(message_id={self.message_id!r}, target_user={self.target_user.login!r})"


class EventSub(NamedTuple):
    """
    Represents subscription information for an event.

    Attributes
    ----------
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    is_prime: bool
        Whether the subscription is a Prime subscription.
    duration_months: int
        Duration of the subscription in months.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    tier: Literal['1000', '2000', '3000']
    is_prime: bool
    duration_months: int
    raw: eventsub.Sub

    @classmethod
    def from_data(cls, data: eventsub.Sub) -> EventSub:
        return cls(
            tier=data['sub_tier'],
            is_prime=data['is_prime'],
            duration_months=data['duration_months'],
            raw=MappingProxyType(data)  # type: ignore
        )


class EventResub(NamedTuple):
    """
    Represents resubscription information for an event.

    Attributes
    ----------
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    is_prime: bool
        Whether the subscription is a Prime subscription.
    duration_months: int
        Duration of the subscription in months.
    cumulative_months: int
        Total months the user has been subscribed.
    streak_months: int
        Current consecutive months subscribed.
    is_gift: bool
        Whether this is a gift subscription.
    gifter_is_anonymous: Optional[bool]
        Whether the gifter is anonymous
    gifter_user: Optional[UserIdentity]
        User who gifted the subscription
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    tier: Literal['1000', '2000', '3000']
    is_prime: bool
    duration_months: int
    cumulative_months: int
    streak_months: int
    is_gift: bool
    gifter_is_anonymous: Optional[bool]
    gifter_user: Optional[UserIdentity]
    raw: eventsub.Resub

    @classmethod
    def from_data(cls, data: eventsub.Resub) -> EventResub:
        gifter_id = data.get('gifter_user_id')
        return cls(
            tier=data['sub_tier'],
            is_prime=data['is_prime'],
            duration_months=data['duration_months'],
            cumulative_months=data['cumulative_months'],
            streak_months=data['streak_months'],
            is_gift=data['is_gift'],
            gifter_is_anonymous=data.get('gifter_is_anonymous'),
            gifter_user=UserIdentity(
                id=data['gifter_user_id'],
                login=data['gifter_user_login'],
                name=data['gifter_user_name']
            ) if gifter_id else None,
            raw=MappingProxyType(data)  # type: ignore
        )


class EventSubGift(NamedTuple):
    """
    Represents subscription gift information for an event.

    Attributes
    ----------
    duration_months: int
        Duration of the gifted subscription in months.
    cumulative_total: Optional[int]
        Total number of subscriptions gifted by the user.
    recipient_user: UserIdentity
        User who received the gift subscription.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    community_gift_id: Optional[str]
        ID of the community gift
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    duration_months: int
    cumulative_total: Optional[int]
    recipient_user: UserIdentity
    tier: Literal['1000', '2000', '3000']
    community_gift_id: Optional[str]
    raw: eventsub.SubGift

    @classmethod
    def from_data(cls, data: eventsub.SubGift) -> EventSubGift:
        return cls(
            duration_months=data['duration_months'],
            cumulative_total=data.get('cumulative_total'),
            recipient_user=UserIdentity(
                id=data['recipient_user_id'],
                login=data['recipient_user_login'],
                name=data['recipient_user_name']
            ),
            tier=data['sub_tier'],
            community_gift_id=data.get('community_gift_id'),
            raw=MappingProxyType(data)  # type: ignore
        )


class EventCommunitySubGift(NamedTuple):
    """
    Represents community subscription gift information for an event.

    Attributes
    ----------
    id: str
        Unique identifier for the community gift.
    total: int
        Total number of subscriptions in the community gift.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    cumulative_total: Optional[int]
        Cumulative total of subscriptions gifted by the user.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    total: int
    tier: Literal['1000', '2000', '3000']
    cumulative_total: Optional[int]
    raw: eventsub.CommunitySubGift

    @classmethod
    def from_data(cls, data: eventsub.CommunitySubGift) -> EventCommunitySubGift:
        return cls(
            id=data['id'],
            total=data['total'],
            tier=data['sub_tier'],
            cumulative_total=data.get('cumulative_total'),
            raw=MappingProxyType(data)  # type: ignore
        )


class EventRaid(NamedTuple):
    """
    Represents raid information for an event.

    Attributes
    ----------
    user: UserIdentity
        User who initiated the raid.
    viewer_count: int
        Number of viewers in the raid.
    profile_image_url: str
        URL of the raider's profile image.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    viewer_count: int
    profile_image_url: str
    raw: eventsub.Raid

    @classmethod
    def from_data(cls, data: eventsub.Raid) -> EventRaid:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            viewer_count=data['viewer_count'],
            profile_image_url=data['profile_image_url'],
            raw=MappingProxyType(data)  # type: ignore
        )


class EventAnnouncement(NamedTuple):
    """
    Represents announcement information for an event.

    Attributes
    ----------
    color: str
        Color of the announcement.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    color: str
    raw: eventsub.Announcement

    @classmethod
    def from_data(cls, data: eventsub.Announcement) -> EventAnnouncement:
        return cls(
            color=data['color'],
            raw=MappingProxyType(data)  # type: ignore
        )


class EventBits(NamedTuple):
    """
    Represents bits badge tier information for an event.

    Attributes
    ----------
    tier: int
        Bits badge tier level.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    tier: int
    raw: eventsub.Bits

    @classmethod
    def from_data(cls, data: eventsub.Bits) -> EventBits:
        return cls(
            tier=data['tier'],
            raw=MappingProxyType(data)  # type: ignore
        )


class EventCharityDonation(NamedTuple):
    """
    Represents charity donation information for an event.

    Attributes
    ----------
    charity_name: str
        Name of the charity receiving the donation.
    amount: EventMoneyAmount
        Donation amount information.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    charity_name: str
    amount: EventMoneyAmount
    raw: eventsub.CharityDonation

    @classmethod
    def from_data(cls, data: eventsub.CharityDonation) -> EventCharityDonation:
        return cls(
            charity_name=data['charity_name'],
            amount=EventMoneyAmount.from_data(data['amount']),
            raw=MappingProxyType(data)  # type: ignore
        )


class ChannelChatNotificationEvent(NamedTuple):
    """
    Represents a channel chat notification event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    chatter_user: Optional[UserIdentity]
        User who triggered the notification
    chatter_is_anonymous: bool
        Whether the chatter is anonymous.
    color: str
        Color of the notification.
    badges: Tuple[EventChatBadge, ...]
        Chat badges associated with the user.
    system_message: str
        System-generated message for the notification.
    message_id: str
        Unique identifier for the notification message.
    message: EventMessage
        Message content and metadata.
    notice_type: Literal[...]
        Type of notification event.
    sub: Optional[EventSub]
        Subscription information
    resub: Optional[EventResub]
        Resubscription information
    sub_gift: Optional[EventSubGift]
        Subscription gift information
    community_sub_gift: Optional[EventCommunitySubGift]
        Community subscription gift information
    gift_paid_upgrade: Optional[dict]
        Gift paid upgrade information
    prime_paid_upgrade: Optional[dict]
        Prime paid upgrade information
    pay_it_forward: Optional[dict]
        Pay it forward information
    raid: Optional[EventRaid]
        Raid information
    unraid: Optional[dict]
        Unraid information
    announcement: Optional[EventAnnouncement]
        Announcement information
    bits_badge_tier: Optional[EventBits]
        Bits badge tier information
    charity_donation: Optional[EventCharityDonation]
        Charity donation information
    source_broadcaster_user: Optional[UserIdentity]
        Source broadcaster user for shared chat notifications.
    source_message_id: Optional[str]
        Source message ID for shared chat notifications.
    source_badges: Optional[Tuple[EventChatBadge, ...]]
        Source badges for shared chat notifications.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    chatter_user: Optional[UserIdentity]
    chatter_is_anonymous: bool
    color: str
    badges: Tuple[EventChatBadge, ...]
    system_message: str
    message_id: str
    message: EventMessage
    notice_type: Literal[
        'sub', 'resub', 'sub_gift', 'community_sub_gift', 'gift_paid_upgrade',
        'prime_paid_upgrade', 'raid', 'unraid', 'pay_it_forward', 'announcement',
        'bits_badge_tier', 'charity_donation', 'shared_chat_sub', 'shared_chat_resub',
        'shared_chat_sub_gift', 'shared_chat_community_sub_gift',
        'shared_chat_gift_paid_upgrade', 'shared_chat_prime_paid_upgrade',
        'shared_chat_raid', 'shared_chat_pay_it_forward', 'shared_chat_announcement'
    ]
    sub: Optional[EventSub]
    resub: Optional[EventResub]
    sub_gift: Optional[EventSubGift]
    community_sub_gift: Optional[EventCommunitySubGift]
    gift_paid_upgrade: Optional[dict]
    prime_paid_upgrade: Optional[dict]
    pay_it_forward: Optional[dict]
    raid: Optional[EventRaid]
    unraid: Optional[dict]
    announcement: Optional[EventAnnouncement]
    bits_badge_tier: Optional[EventBits]
    charity_donation: Optional[EventCharityDonation]
    source_broadcaster_user: Optional[UserIdentity]
    source_message_id: Optional[str]
    source_badges: Optional[Tuple[EventChatBadge, ...]]
    raw: eventsub.ChannelChatNotificationEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatNotificationEventV1) -> ChannelChatNotificationEvent:
        chatter_id = data.get('chatter_user_id')
        source_broadcaster_id = data.get('source_broadcaster_user_id')
        badges_data = data.get('badges', [])
        source_badges_data = data.get('source_badges', [])
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            chatter_user=UserIdentity(
                id=data['chatter_user_id'],
                login=data['chatter_user_name'].lower(),
                name=data['chatter_user_name']
            ) if chatter_id else None,
            chatter_is_anonymous=data['chatter_is_anonymous'],
            color=data['color'],
            badges=tuple(EventChatBadge.from_data(badge) for badge in badges_data),
            system_message=data['system_message'],
            message_id=data['message_id'],
            message=EventMessage.from_data(data['message']),
            notice_type=data['notice_type'],
            sub=EventSub.from_data(data['sub']) if data.get('sub') else None,
            resub=EventResub.from_data(data['resub']) if data.get('resub') else None,
            sub_gift=EventSubGift.from_data(data['sub_gift']) if data.get('sub_gift') else None,
            community_sub_gift=EventCommunitySubGift.from_data(data['community_sub_gift'])
            if data.get('community_sub_gift') else None,
            gift_paid_upgrade=data.get('gift_paid_upgrade'),
            prime_paid_upgrade=data.get('prime_paid_upgrade'),
            pay_it_forward=data.get('pay_it_forward'),
            raid=EventRaid.from_data(data['raid']) if data.get('raid') else None,
            unraid=data.get('unraid'),
            announcement=EventAnnouncement.from_data(data['announcement']) if data.get('announcement') else None,
            bits_badge_tier=EventBits.from_data(data['bits_badge_tier']) if data.get('bits_badge_tier') else None,
            charity_donation=EventCharityDonation.from_data(
                data['charity_donation']) if data.get('charity_donation') else None,
            source_broadcaster_user=UserIdentity(
                id=data['source_broadcaster_user_id'],
                login=data['source_broadcaster_user_login'],
                name=data['source_broadcaster_user_name']
            ) if source_broadcaster_id else None,
            source_message_id=data.get('source_message_id'),
            source_badges=tuple(EventChatBadge.from_data(badge)
                                for badge in source_badges_data) if source_badges_data else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelChatNotificationEvent) -> bool:
        if not isinstance(other, ChannelChatNotificationEvent):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"ChannelChatNotificationEvent(message_id={self.message_id!r}, notice_type={self.notice_type!r})"


class ChannelChatSettingsUpdateEvent(NamedTuple):
    """
    Represents an event for updating channel chat settings.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    emote_mode: bool
        Whether emote-only mode is enabled.
    follower_mode: bool
        Whether follower-only mode is enabled.
    follower_mode_duration_minutes: Optional[int]
        Duration in minutes for follower-only mode
    slow_mode: bool
        Whether slow mode is enabled.
    slow_mode_wait_time_seconds: Optional[int]
        Wait time in seconds for slow mode
    subscriber_mode: bool
        Whether subscriber-only mode is enabled.
    unique_chat_mode: bool
        Whether unique chat (r9k) mode is enabled.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    emote_mode: bool
    follower_mode: bool
    follower_mode_duration_minutes: Optional[int]
    slow_mode: bool
    slow_mode_wait_time_seconds: Optional[int]
    subscriber_mode: bool
    unique_chat_mode: bool
    raw: eventsub.ChannelChatSettingsUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatSettingsUpdateEventV1) -> ChannelChatSettingsUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            emote_mode=data['emote_mode'],
            follower_mode=data['follower_mode'],
            follower_mode_duration_minutes=data['follower_mode_duration_minutes'],
            slow_mode=data['slow_mode'],
            slow_mode_wait_time_seconds=data['slow_mode_wait_time_seconds'],
            subscriber_mode=data['subscriber_mode'],
            unique_chat_mode=data['unique_chat_mode'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelChatSettingsUpdateEvent(broadcaster={self.broadcaster_user.login!r})"


class ChannelSubscribeEvent(NamedTuple):
    """
    Represents a channel subscription event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who subscribed.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    is_gift: bool
        Whether the subscription was a gift.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    tier: Literal['1000', '2000', '3000']
    is_gift: bool
    raw: eventsub.ChannelSubscribeEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSubscribeEventV1) -> ChannelSubscribeEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            tier=data['tier'],
            is_gift=data['is_gift'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSubscribeEvent(user={self.user.login!r}, tier={self.tier!r})"


class ChannelCheerEvent(NamedTuple):
    """
    Represents a channel cheer event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: Optional[UserIdentity]
        User who cheered, if not anonymous.
    is_anonymous: bool
        Whether the cheer is anonymous.
    message: str
        Message included with the cheer.
    bits: int
        Number of bits cheered.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: Optional[UserIdentity]
    is_anonymous: bool
    message: str
    bits: int
    raw: eventsub.ChannelCheerEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelCheerEventV1) -> ChannelCheerEvent:
        user_id = data.get('user_id')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ) if user_id else None,
            is_anonymous=data['is_anonymous'],
            message=data['message'],
            bits=data['bits'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelCheerEvent(broadcaster={self.broadcaster_user.login!r}, bits={self.bits})"


class ChannelUpdateEvent(NamedTuple):
    """
    Represents a channel update event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    title: str
        Updated stream title.
    language: str
        Stream language.
    category_id: str
        Category ID of the stream.
    category_name: str
        Category name of the stream.
    content_classification_labels: Tuple[str, ...]
        Content classification labels applied to the stream.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    title: str
    language: str
    category_id: str
    category_name: str
    content_classification_labels: Tuple[str, ...]
    raw: eventsub.ChannelUpdateEventV2

    @classmethod
    def from_data(cls, data: eventsub.ChannelUpdateEventV2) -> ChannelUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            title=data['title'],
            language=data['language'],
            category_id=data['category_id'],
            category_name=data['category_name'],
            content_classification_labels=tuple(data['content_classification_labels']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelUpdateEvent(broadcaster={self.broadcaster_user.login!r}, title={self.title!r})"


class ChannelUnbanEvent(NamedTuple):
    """
    Represents a channel unban event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was unbanned.
    moderator_user: UserIdentity
        Moderator who performed the unban.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    raw: eventsub.ChannelUnbanEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelUnbanEventV1) -> ChannelUnbanEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelUnbanEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"

class ChannelFollowEvent(NamedTuple):
    """
    Represents a channel follow event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who followed the channel.
    followed_at: datetime.datetime
        Timestamp when the follow occurred.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    followed_at: datetime.datetime
    raw: eventsub.ChannelFollowEventV2

    @classmethod
    def from_data(cls, data: eventsub.ChannelFollowEventV2) -> ChannelFollowEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            followed_at=from_iso_string(data['followed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelFollowEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelRaidEvent(NamedTuple):
    """
    Represents a channel raid event.

    Attributes
    ----------
    from_broadcaster_user: UserIdentity
        Broadcaster user who initiated the raid.
    to_broadcaster_user: UserIdentity
        Broadcaster user who received the raid.
    viewers: int
        Number of viewers in the raid.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    from_broadcaster_user: UserIdentity
    to_broadcaster_user: UserIdentity
    viewers: int
    raw: eventsub.ChannelRaidEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelRaidEventV1) -> ChannelRaidEvent:
        return cls(
            from_broadcaster_user=UserIdentity(
                id=data['from_broadcaster_user_id'],
                login=data['from_broadcaster_user_login'],
                name=data['from_broadcaster_user_name']
            ),
            to_broadcaster_user=UserIdentity(
                id=data['to_broadcaster_user_id'],
                login=data['to_broadcaster_user_login'],
                name=data['to_broadcaster_user_name']
            ),
            viewers=data['viewers'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelRaidEvent(from={self.from_broadcaster_user.login!r}, to={self.to_broadcaster_user.login!r})"


class EventModerationFollowers(NamedTuple):
    follow_duration_minutes: int

    @classmethod
    def from_data(cls, data: eventsub.ModerationFollowers) -> EventModerationFollowers:
        return cls(follow_duration_minutes=data['follow_duration_minutes'])


class EventModerationSlow(NamedTuple):
    wait_time_seconds: int

    @classmethod
    def from_data(cls, data: eventsub.ModerationSlow) -> EventModerationSlow:
        return cls(wait_time_seconds=data['wait_time_seconds'])


class EventModerationBan(NamedTuple):
    user: UserIdentity
    reason: Optional[str]

    @classmethod
    def from_data(cls, data: eventsub.ModerationBan) -> EventModerationBan:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            reason=data.get('reason')
        )


class EventModerationTimeout(NamedTuple):
    user: UserIdentity
    reason: Optional[str]
    expires_at: datetime.datetime

    @classmethod
    def from_data(cls, data: eventsub.ModerationTimeout) -> EventModerationTimeout:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            reason=data.get('reason'),
            expires_at=from_iso_string(data['expires_at'])
        )


class EventModerationDelete(NamedTuple):
    user: UserIdentity
    message_id: str
    message_body: str

    @classmethod
    def from_data(cls, data: eventsub.ModerationDelete) -> EventModerationDelete:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            message_id=data['message_id'],
            message_body=data['message_body']
        )


class EventModerationAutomodTerms(NamedTuple):
    action: Literal['add', 'remove']
    list: Literal['blocked', 'permitted']
    terms: Tuple[str, ...]
    from_automod: bool

    @classmethod
    def from_data(cls, data: eventsub.ModerationAutomodTerms) -> EventModerationAutomodTerms:
        return cls(
            action=data['action'],
            list=data['list'],
            terms=tuple(data['terms']),
            from_automod=data['from_automod']
        )


class EventModerationUnbanRequest(NamedTuple):
    user: UserIdentity
    is_approved: bool
    moderator_message: str

    @classmethod
    def from_data(cls, data: eventsub.ModerationUnbanRequest) -> EventModerationUnbanRequest:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            is_approved=data['is_approved'],
            moderator_message=data['moderator_message']
        )


class EventModerationWarn(NamedTuple):
    user: UserIdentity
    reason: Optional[str]
    chat_rules_cited: Optional[Tuple[str, ...]]

    @classmethod
    def from_data(cls, data: eventsub.ModerationWarn) -> EventModerationWarn:
        chat_rules = data.get('chat_rules_cited')
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            reason=data.get('reason'),
            chat_rules_cited=tuple(chat_rules) if chat_rules else None
        )


class ChannelModerateEventV1(NamedTuple):
    """
    Represents a channel moderation event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who performed the action.
    source_broadcaster_user: UserIdentity
        Source broadcaster for shared chat actions.
    action: Literal['ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
                    'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
                    'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
                    'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
                    'mod', 'unmod', 'approve_unban_request', 'deny_unban_request',
                    'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
                    'shared_chat_unban', 'shared_chat_delete']
        The moderation action performed.
    followers: Optional[EventModerationFollowers]
        Follower mode settings
    slow: Optional[EventModerationSlow]
        Slow mode settings
    vip: Optional[UserIdentity]
        User added as VIP
    unvip: Optional[UserIdentity]
        User removed as VIP
    mod: Optional[UserIdentity]
        User added as moderator
    unmod: Optional[UserIdentity]
        User removed as moderator
    ban: Optional[EventModerationBan]
        Ban information
    unban: Optional[UserIdentity]
        Unbanned user information
    timeout: Optional[EventModerationTimeout]
        Timeout information
    untimeout: Optional[UserIdentity]
        Untimed-out user information
    raid: Optional[EventRaid]
        Raid information
    unraid: Optional[UserIdentity]
        Unraid information
    delete: Optional[EventModerationDelete]
        Message deletion information
    automod_terms: Optional[EventModerationAutomodTerms]
        Automod terms update information
    unban_request: Optional[EventModerationUnbanRequest]
        Unban request resolution information
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    source_broadcaster_user: UserIdentity
    action: Literal[
        'ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
        'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
        'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
        'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
        'mod', 'unmod', 'approve_unban_request', 'deny_unban_request',
        'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
        'shared_chat_unban', 'shared_chat_delete'
    ]
    followers: Optional[EventModerationFollowers]
    slow: Optional[EventModerationSlow]
    vip: Optional[UserIdentity]
    unvip: Optional[UserIdentity]
    mod: Optional[UserIdentity]
    unmod: Optional[UserIdentity]
    ban: Optional[EventModerationBan]
    unban: Optional[UserIdentity]
    timeout: Optional[EventModerationTimeout]
    untimeout: Optional[UserIdentity]
    raid: Optional[EventRaid]
    unraid: Optional[UserIdentity]
    delete: Optional[EventModerationDelete]
    automod_terms: Optional[EventModerationAutomodTerms]
    unban_request: Optional[EventModerationUnbanRequest]
    raw: eventsub.ChannelModerateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelModerateEventV1) -> ChannelModerateEventV1:
        followers_data = data.get('followers')
        slow_data = data.get('slow')
        vip_data = data.get('vip')
        unvip_data = data.get('unvip')
        mod_data = data.get('mod')
        unmod_data = data.get('unmod')
        ban_data = data.get('ban')
        unban_data = data.get('unban')
        timeout_data = data.get('timeout')
        untimeout_data = data.get('untimeout')
        raid_data = data.get('raid')
        unraid_data = data.get('unraid')
        delete_data = data.get('delete')
        automod_terms_data = data.get('automod_terms')
        unban_request_data = data.get('unban_request')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            source_broadcaster_user=UserIdentity(
                id=data['source_broadcaster_user_id'],
                login=data['source_broadcaster_user_login'],
                name=data['source_broadcaster_user_name']
            ),
            action=data['action'],
            followers=EventModerationFollowers.from_data(followers_data) if followers_data else None,
            slow=EventModerationSlow.from_data(slow_data) if slow_data else None,
            vip=UserIdentity(
                id=vip_data['user_id'],
                login=vip_data['user_login'],
                name=vip_data['user_name']
            ) if vip_data else None,
            unvip=UserIdentity(
                id=unvip_data['user_id'],
                login=unvip_data['user_login'],
                name=unvip_data['user_name']
            ) if unvip_data else None,
            mod=UserIdentity(
                id=mod_data['user_id'],
                login=mod_data['user_login'],
                name=mod_data['user_name']
            ) if mod_data else None,
            unmod=UserIdentity(
                id=unmod_data['user_id'],
                login=unmod_data['user_login'],
                name=unmod_data['user_name']
            ) if unmod_data else None,
            ban=EventModerationBan.from_data(ban_data) if ban_data else None,
            unban=UserIdentity(
                id=unban_data['user_id'],
                login=unban_data['user_login'],
                name=unban_data['user_name']
            ) if unban_data else None,
            timeout=EventModerationTimeout.from_data(timeout_data) if timeout_data else None,
            untimeout=UserIdentity(
                id=untimeout_data['user_id'],
                login=untimeout_data['user_login'],
                name=untimeout_data['user_name']
            ) if untimeout_data else None,
            raid=EventRaid.from_data(raid_data) if raid_data else None,
            unraid=UserIdentity(
                id=unraid_data['user_id'],
                login=unraid_data['user_login'],
                name=unraid_data['user_name']
            ) if unraid_data else None,
            delete=EventModerationDelete.from_data(delete_data) if delete_data else None,
            automod_terms=EventModerationAutomodTerms.from_data(automod_terms_data) if automod_terms_data else None,
            unban_request=EventModerationUnbanRequest.from_data(unban_request_data) if unban_request_data else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelModerateEventV1(broadcaster={self.broadcaster_user.login!r}, action={self.action!r})"


class ChannelModerateEventV2(NamedTuple):
    """
    Represents a channel moderation event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who performed the action.
    source_broadcaster_user: UserIdentity
        Source broadcaster for shared chat actions.
    action: Literal['ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
                    'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
                    'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
                    'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
                    'mod', 'unmod', 'approve_unban_request', 'deny_unban_request', 'warn',
                    'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
                    'shared_chat_unban', 'shared_chat_delete']
        The moderation action performed.
    followers: Optional[EventModerationFollowers]
        Follower mode settings
    slow: Optional[EventModerationSlow]
        Slow mode settings
    vip: Optional[UserIdentity]
        User added as VIP
    unvip: Optional[UserIdentity]
        User removed as VIP
    mod: Optional[UserIdentity]
        User added as moderator
    unmod: Optional[UserIdentity]
        User removed as moderator
    ban: Optional[EventModerationBan]
        Ban information
    unban: Optional[UserIdentity]
        Unbanned user information
    timeout: Optional[EventModerationTimeout]
        Timeout information
    untimeout: Optional[UserIdentity]
        Untimed-out user information
    raid: Optional[EventRaid]
        Raid information
    unraid: Optional[UserIdentity]
        Unraid information
    delete: Optional[EventModerationDelete]
        Message deletion information
    automod_terms: Optional[EventModerationAutomodTerms]
        Automod terms update information
    unban_request: Optional[EventModerationUnbanRequest]
        Unban request resolution information
    warn: Optional[EventModerationWarn]
        Warning information
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    source_broadcaster_user: UserIdentity
    action: Literal[
        'ban', 'timeout', 'unban', 'untimeout', 'clear', 'emoteonly', 'emoteonlyoff',
        'followers', 'followersoff', 'uniquechat', 'uniquechatoff', 'slow', 'slowoff',
        'subscribers', 'subscribersoff', 'unraid', 'delete', 'unvip', 'vip', 'raid',
        'add_blocked_term', 'add_permitted_term', 'remove_blocked_term', 'remove_permitted_term',
        'mod', 'unmod', 'approve_unban_request', 'deny_unban_request', 'warn',
        'shared_chat_ban', 'shared_chat_timeout', 'shared_chat_untimeout',
        'shared_chat_unban', 'shared_chat_delete'
    ]
    followers: Optional[EventModerationFollowers]
    slow: Optional[EventModerationSlow]
    vip: Optional[UserIdentity]
    unvip: Optional[UserIdentity]
    mod: Optional[UserIdentity]
    unmod: Optional[UserIdentity]
    ban: Optional[EventModerationBan]
    unban: Optional[UserIdentity]
    timeout: Optional[EventModerationTimeout]
    untimeout: Optional[UserIdentity]
    raid: Optional[EventRaid]
    unraid: Optional[UserIdentity]
    delete: Optional[EventModerationDelete]
    automod_terms: Optional[EventModerationAutomodTerms]
    unban_request: Optional[EventModerationUnbanRequest]
    warn: Optional[EventModerationWarn]
    raw: eventsub.ChannelModerateEventV2

    @classmethod
    def from_data(cls, data: eventsub.ChannelModerateEventV2) -> ChannelModerateEventV2:
        followers_data = data.get('followers')
        slow_data = data.get('slow')
        vip_data = data.get('vip')
        unvip_data = data.get('unvip')
        mod_data = data.get('mod')
        unmod_data = data.get('unmod')
        ban_data = data.get('ban')
        unban_data = data.get('unban')
        timeout_data = data.get('timeout')
        untimeout_data = data.get('untimeout')
        raid_data = data.get('raid')
        unraid_data = data.get('unraid')
        delete_data = data.get('delete')
        automod_terms_data = data.get('automod_terms')
        unban_request_data = data.get('unban_request')
        warn_data = data.get('warn')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            source_broadcaster_user=UserIdentity(
                id=data['source_broadcaster_user_id'],
                login=data['source_broadcaster_user_login'],
                name=data['source_broadcaster_user_name']
            ),
            action=data['action'],
            followers=EventModerationFollowers.from_data(followers_data) if followers_data else None,
            slow=EventModerationSlow.from_data(slow_data) if slow_data else None,
            vip=UserIdentity(
                id=vip_data['user_id'],
                login=vip_data['user_login'],
                name=vip_data['user_name']
            ) if vip_data else None,
            unvip=UserIdentity(
                id=unvip_data['user_id'],
                login=unvip_data['user_login'],
                name=unvip_data['user_name']
            ) if unvip_data else None,
            mod=UserIdentity(
                id=mod_data['user_id'],
                login=mod_data['user_login'],
                name=mod_data['user_name']
            ) if mod_data else None,
            unmod=UserIdentity(
                id=unmod_data['user_id'],
                login=unmod_data['user_login'],
                name=unmod_data['user_name']
            ) if unmod_data else None,
            ban=EventModerationBan.from_data(ban_data) if ban_data else None,
            unban=UserIdentity(
                id=unban_data['user_id'],
                login=unban_data['user_login'],
                name=unban_data['user_name']
            ) if unban_data else None,
            timeout=EventModerationTimeout.from_data(timeout_data) if timeout_data else None,
            untimeout=UserIdentity(
                id=untimeout_data['user_id'],
                login=untimeout_data['user_login'],
                name=untimeout_data['user_name']
            ) if untimeout_data else None,
            raid=EventRaid.from_data(raid_data) if raid_data else None,
            unraid=UserIdentity(
                id=unraid_data['user_id'],
                login=unraid_data['user_login'],
                name=unraid_data['user_name']
            ) if unraid_data else None,
            delete=EventModerationDelete.from_data(delete_data) if delete_data else None,
            automod_terms=EventModerationAutomodTerms.from_data(automod_terms_data) if automod_terms_data else None,
            unban_request=EventModerationUnbanRequest.from_data(unban_request_data) if unban_request_data else None,
            warn=EventModerationWarn.from_data(warn_data) if warn_data else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelModerateEventV2(broadcaster={self.broadcaster_user.login!r}, action={self.action!r})"


class StreamOnlineEvent(NamedTuple):
    """
    Represents a stream going online event.

    Attributes
    ----------
    broadcaster: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the stream.
    type: Literal['live', 'playlist', 'watch_party', 'premiere', 'rerun']
        Type of stream.
    started_at: datetime.datetime
        Timestamp when the stream started.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster: UserIdentity
    id: str
    type: Literal['live', 'playlist', 'watch_party', 'premiere', 'rerun']
    started_at: datetime.datetime
    raw: eventsub.StreamOnlineEventV1

    @classmethod
    def from_data(cls, data: eventsub.StreamOnlineEventV1) -> StreamOnlineEvent:
        return cls(
            broadcaster=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            type=data['type'],
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StreamOnlineEvent(broadcaster={self.broadcaster!r})"


class StreamOfflineEvent(NamedTuple):
    """
    Represents a stream going offline event.

    Attributes
    ----------
    broadcaster: UserIdentity
        Broadcaster user information.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster: UserIdentity
    raw: eventsub.StreamOfflineEventV1

    @classmethod
    def from_data(cls, data: eventsub.StreamOfflineEventV1) -> StreamOfflineEvent:
        return cls(
            broadcaster=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"StreamOfflineEvent(broadcaster={self.broadcaster!r})"


class EventTopPredictor(NamedTuple):
    """
    User who used the most Channel Points on an outcome.

    Attributes
    ----------
    user: UserIdentity
        Top predictor information.
    channel_points_used: int
        Number of channel points the user used on this outcome.
    channel_points_won: Optional[int]
        Number of channel points the user won, if any.
    """
    user: UserIdentity
    channel_points_used: int
    channel_points_won: Optional[int]

    @classmethod
    def from_data(cls, data: eventsub.TopPredictor) -> EventTopPredictor:
        return cls(
            user=UserIdentity(data['user_id'], data['user_login'], data['user_name']),
            channel_points_used=data['channel_points_used'],
            channel_points_won=data.get('channel_points_won')
        )


class EventPredictionOutcome(NamedTuple):
    """
    Represents a single outcome for a prediction event.

    Attributes
    ----------
    id: str
        Unique identifier for this outcome.
    title: str
        Display title of the outcome.
    color: str
        Color associated with the outcome (e.g., 'pink', 'blue').
    users: int
        Number of users who predicted this outcome.
    channel_points: int
        Total channel points wagered on this outcome.
    top_predictors: Optional[Tuple[TopPredictor, ...]]
        Top predictors for this outcome, if available.
    """
    id: str
    title: str
    color: Literal['pink', 'blue']
    users: int
    channel_points: int
    top_predictors: Optional[Tuple[EventTopPredictor, ...]]

    @classmethod
    def from_data(cls, data: eventsub.PredictionOutcome) -> EventPredictionOutcome:
        predictors = data.get('top_predictors')
        top_predictors_tuple = None
        if predictors:
            top_predictors_tuple = tuple(EventTopPredictor.from_data(pred) for pred in predictors)

        return cls(
            id=data['id'],
            title=data['title'],
            color=data['color'],
            users=data.get('users', 0),
            channel_points=data.get('channel_points', 0),
            top_predictors=top_predictors_tuple
        )


class ChannelPredictionBeginEvent(NamedTuple):
    """
    Represents the start of a channel prediction event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the prediction.
    title: str
        Title of the prediction.
    outcomes: Tuple[EventPredictionOutcome, ...]
        Possible prediction outcomes.
    started_at: datetime.datetime
        Timestamp when the prediction started.
    locks_at: datetime.datetime
        Timestamp when the prediction locks.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    outcomes: Tuple[EventPredictionOutcome, ...]
    started_at: datetime.datetime
    locks_at: datetime.datetime
    raw: eventsub.ChannelPredictionBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPredictionBeginEventV1) -> ChannelPredictionBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            outcomes=tuple(EventPredictionOutcome.from_data(outcome) for outcome in data['outcomes']),
            started_at=from_iso_string(data['started_at']),
            locks_at=from_iso_string(data['locks_at']),
            raw=MappingProxyType(data) #  type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelPredictionBeginEvent(broadcaster={self.broadcaster_user.login!r}, id={self.id!r})"


class ChannelPredictionProgressEvent(NamedTuple):
    """
    Represents progress updates for a channel prediction event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the prediction.
    title: str
        Title of the prediction.
    outcomes: Tuple[EventPredictionOutcome, ...]
        Possible prediction outcomes with updated vote counts.
    started_at: datetime.datetime
        Timestamp when the prediction started.
    locks_at: datetime.datetime
        Timestamp when the prediction locks.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    outcomes: Tuple[EventPredictionOutcome, ...]
    started_at: datetime.datetime
    locks_at: datetime.datetime
    raw: eventsub.ChannelPredictionProgressEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPredictionProgressEventV1) -> ChannelPredictionProgressEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            outcomes=tuple(EventPredictionOutcome.from_data(outcome) for outcome in data['outcomes']),
            started_at=from_iso_string(data['started_at']),
            locks_at=from_iso_string(data['locks_at']),
            raw=MappingProxyType(data) # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelPredictionProgressEvent(broadcaster={self.broadcaster_user.login!r}, id={self.id!r})"


class ChannelPredictionLockEvent(NamedTuple):
    """
    Represents a channel prediction lock event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the prediction.
    title: str
        Title of the prediction.
    outcomes: Tuple[EventPredictionOutcome, ...]
        Possible prediction outcomes with final vote counts.
    started_at: datetime.datetime
        Timestamp when the prediction started.
    locked_at: datetime.datetime
        Timestamp when the prediction was locked.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    outcomes: Tuple[EventPredictionOutcome, ...]
    started_at: datetime.datetime
    locked_at: datetime.datetime
    raw: eventsub.ChannelPredictionLockEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPredictionLockEventV1) -> ChannelPredictionLockEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            outcomes=tuple(EventPredictionOutcome.from_data(outcome) for outcome in data['outcomes']),
            started_at=from_iso_string(data['started_at']),
            locked_at=from_iso_string(data['locked_at']),
            raw=MappingProxyType(data) # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelPredictionLockEvent(broadcaster={self.broadcaster_user.login!r}, id={self.id!r})"


class ChannelPredictionEndEvent(NamedTuple):
    """
    Represents the end of a channel prediction event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the prediction.
    title: str
        Title of the prediction.
    winning_outcome_id: str
        Identifier of the winning outcome.
    outcomes: Tuple[EventPredictionOutcome, ...]
        Final prediction outcomes.
    status: Literal['resolved', 'canceled']
        Status of the prediction (resolved or canceled).
    started_at: datetime.datetime
        Timestamp when the prediction started.
    ended_at: datetime.datetime
        Timestamp when the prediction ended.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    winning_outcome_id: str
    outcomes: Tuple[EventPredictionOutcome, ...]
    status: Literal['resolved', 'canceled']
    started_at: datetime.datetime
    ended_at: datetime.datetime
    raw: eventsub.ChannelPredictionEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPredictionEndEventV1) -> ChannelPredictionEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            winning_outcome_id=data['winning_outcome_id'],
            outcomes=tuple(EventPredictionOutcome.from_data(outcome) for outcome in data['outcomes']),
            status=data['status'],
            started_at=from_iso_string(data['started_at']),
            ended_at=from_iso_string(data['ended_at']),
            raw=MappingProxyType(data) # type: ignore
        )

    def __repr__(self) -> str:
        return (f"ChannelPredictionEndEvent(broadcaster={self.broadcaster_user.login!r}, id={self.id!r},"
                f" status={self.status!r})")

class ChannelChatUserMessageHoldEvent(NamedTuple):
    """
    Represents a channel chat message hold event, where a message is held for moderation.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who sent the held message.
    message_id: str
        Unique identifier for the held message.
    message: EventMessage
        Content and metadata of the held message.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    message_id: str
    message: EventMessage
    raw: eventsub.ChannelChatUserMessageHoldEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatUserMessageHoldEventV1) -> ChannelChatUserMessageHoldEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(data['message']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelChatUserMessageHoldEvent) -> bool:
        if not isinstance(other, ChannelChatUserMessageHoldEvent):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"ChannelChatUserMessageHoldEvent(message_id={self.message_id!r}, user={self.user.login!r})"


class ChannelChatUserMessageUpdateEvent(NamedTuple):
    """
    Represents an update to a held channel chat message (e.g., approved or denied).

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who sent the message.
    message_id: str
        Unique identifier for the message.
    message: EventMessage
        Content and metadata of the message.
    status: Literal['approved', 'denied', 'expired']
        Status of the message after moderation.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    message_id: str
    message: EventMessage
    status: Literal['approved', 'denied', 'expired']
    raw: eventsub.ChannelChatUserMessageUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelChatUserMessageUpdateEventV1) -> ChannelChatUserMessageUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            message_id=data['message_id'],
            message=EventMessage.from_data(data['message']),
            status=data['status'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelChatUserMessageUpdateEvent) -> bool:
        if not isinstance(other, ChannelChatUserMessageUpdateEvent):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return f"ChannelChatUserMessageUpdateEvent(message_id={self.message_id!r}, status={self.status!r})"


class EventSharedChatParticipant(NamedTuple):
    user: UserIdentity

    @classmethod
    def from_data(cls, data: eventsub.SharedChatParticipant) -> EventSharedChatParticipant:
        return cls(
            user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            )
        )


class ChannelSharedChatBeginEvent(NamedTuple):
    """
    Represents the start of a shared chat session between channels.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information for the local channel.
    session_id: str
        Unique identifier for the shared chat session.
    host_broadcaster_user: UserIdentity
        Host broadcaster user information.
    participants: Tuple[EventSharedChatParticipant, ...]
        List of participants in the shared chat session.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    session_id: str
    host_broadcaster_user: UserIdentity
    participants: Tuple[EventSharedChatParticipant, ...]
    raw: eventsub.ChannelSharedChatBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSharedChatBeginEventV1) -> ChannelSharedChatBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            session_id=data['session_id'],
            host_broadcaster_user=UserIdentity(
                id=data['host_broadcaster_user_id'],
                login=data['host_broadcaster_user_login'],
                name=data['host_broadcaster_user_name']
            ),
            participants=tuple(EventSharedChatParticipant.from_data(participant)
                               for participant in data['participants']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSharedChatBeginEvent(session_id={self.session_id!r})"


class ChannelSharedChatUpdateEvent(NamedTuple):
    """
    Represents an update to a shared chat session.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information for the local channel.
    session_id: str
        Unique identifier for the shared chat session.
    host_broadcaster_user: UserIdentity
        Host broadcaster user information.
    participants: Tuple[EventSharedChatParticipant, ...]
        Updated list of participants in the shared chat session.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    session_id: str
    host_broadcaster_user: UserIdentity
    participants: Tuple[EventSharedChatParticipant, ...]
    raw: eventsub.ChannelSharedChatUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSharedChatUpdateEventV1) -> ChannelSharedChatUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            session_id=data['session_id'],
            host_broadcaster_user=UserIdentity(
                id=data['host_broadcaster_user_id'],
                login=data['host_broadcaster_user_login'],
                name=data['host_broadcaster_user_name']
            ),
            participants=tuple(EventSharedChatParticipant.from_data(participant)
                               for participant in data['participants']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSharedChatUpdateEvent(session_id={self.session_id!r})"


class ChannelSharedChatEndEvent(NamedTuple):
    """
    Represents the end of a shared chat session.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information for the local channel.
    session_id: str
        Unique identifier for the shared chat session.
    host_broadcaster_user: UserIdentity
        Host broadcaster user information.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    session_id: str
    host_broadcaster_user: UserIdentity
    raw: eventsub.ChannelSharedChatEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSharedChatEndEventV1) -> ChannelSharedChatEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            session_id=data['session_id'],
            host_broadcaster_user=UserIdentity(
                id=data['host_broadcaster_user_id'],
                login=data['host_broadcaster_user_login'],
                name=data['host_broadcaster_user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSharedChatEndEvent(session_id={self.session_id!r})"


class ChannelSubscriptionEndEvent(NamedTuple):
    """
    Represents the end of a channel subscription.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User whose subscription ended.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    is_gift: bool
        Whether the subscription was a gift.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    tier: Literal['1000', '2000', '3000']
    is_gift: bool
    raw: eventsub.ChannelSubscriptionEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSubscriptionEndEventV1) -> ChannelSubscriptionEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            tier=data['tier'],
            is_gift=data['is_gift'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSubscriptionEndEvent(user={self.user.login!r}, tier={self.tier!r})"


class ChannelSubscriptionGiftEvent(NamedTuple):
    """
    Represents a channel subscription gift event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who gifted the subscriptions.
    total: int
        Total number of subscriptions gifted.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    cumulative_total: Optional[int]
        Cumulative total of gifted subscriptions by the user
    is_anonymous: bool
        Whether the gift was anonymous.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    total: int
    tier: Literal['1000', '2000', '3000']
    cumulative_total: Optional[int]
    is_anonymous: bool
    raw: eventsub.ChannelSubscriptionGiftEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSubscriptionGiftEventV1) -> ChannelSubscriptionGiftEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            total=data['total'],
            tier=data['tier'],
            cumulative_total=data.get('cumulative_total'),
            is_anonymous=data['is_anonymous'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSubscriptionGiftEvent(user={self.user.login!r}, total={self.total})"


class EventEmoteData(NamedTuple):
    """
    Represents emote data within a message or text.

    Attributes
    ----------
    id: str
        Unique identifier for the emote.
    begin: int
        Starting character position of the emote in the text.
    end: int
        Ending character position of the emote in the text.
    """

    id: str
    begin: int
    end: int

    @classmethod
    def from_data(cls, data: eventsub.EmoteData) -> EventEmoteData:
        return cls(
            id=data['id'],
            begin=data['begin'],
            end=data['end']
        )


class EventSubscriptionMessage(NamedTuple):
    """
    Represents a subscription message with text and emote information.

    Attributes
    ----------
    text: str
        The text content of the subscription message.
    emotes: Tuple[EventEmoteData, ...]
        Tuple of emote data contained within the message text.
    """

    text: str
    emotes: Tuple[EventEmoteData, ...]

    @classmethod
    def from_data(cls, data: eventsub.SubscriptionMessage) -> EventSubscriptionMessage:
        return cls(
            text=data['text'],
            emotes=tuple(EventEmoteData.from_data(emote) for emote in data['emotes'])
        )


class ChannelSubscriptionMessageEvent(NamedTuple):
    """
    Represents a channel subscription message event.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who sent the subscription message.
    tier: Literal['1000', '2000', '3000']
        Subscription tier level.
    message: EventSubscriptionMessage
        Subscription message content and metadata.
    cumulative_months: int
        Total months the user has been subscribed.
    streak_months: Optional[int]
        Current subscription streak
    duration_months: int
        Duration of the subscription in months.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    tier: Literal['1000', '2000', '3000']
    message: EventSubscriptionMessage
    cumulative_months: int
    streak_months: Optional[int]
    duration_months: int
    raw: eventsub.ChannelSubscriptionMessageEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSubscriptionMessageEventV1) -> ChannelSubscriptionMessageEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            tier=data['tier'],
            message=EventSubscriptionMessage.from_data(data['message']),
            cumulative_months=data['cumulative_months'],
            streak_months=data['streak_months'],
            duration_months=data['duration_months'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSubscriptionMessageEvent(user={self.user.login!r}, tier={self.tier!r})"


class ChannelUnbanRequestCreateEvent(NamedTuple):
    """
    Represents the creation of a channel unban request.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who submitted the unban request.
    id: str
        Unique identifier for the unban request.
    text: str
        Text submitted with the unban request.
    created_at: datetime.datetime
        Timestamp when the unban request was created.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    text: str
    created_at: datetime.datetime
    raw: eventsub.ChannelUnbanRequestCreateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelUnbanRequestCreateEventV1) -> ChannelUnbanRequestCreateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            text=data['text'],
            created_at=from_iso_string(data['created_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelUnbanRequestCreateEvent(id={self.id!r}, user={self.user.login!r})"


class ChannelUnbanRequestResolveEvent(NamedTuple):
    """
    Represents the resolution of a channel unban request.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who submitted the unban request.
    moderator_user: UserIdentity
        Moderator who resolved the request.
    id: str
        Unique identifier for the unban request.
    resolution_text: str
        Text provided with the resolution.
    status: Literal['approved', 'denied']
        Resolution status of the unban request.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    id: str
    resolution_text: str
    status: Literal['approved', 'denied']
    raw: eventsub.ChannelUnbanRequestResolveEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelUnbanRequestResolveEventV1) -> ChannelUnbanRequestResolveEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            id=data['id'],
            resolution_text=data['resolution_text'],
            status=data['status'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelUnbanRequestResolveEvent(id={self.id!r}, status={self.status!r})"


class ChannelModeratorAddEvent(NamedTuple):
    """
    Represents the addition of a channel moderator.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was added as a moderator.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    raw: eventsub.ChannelModeratorAddEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelModeratorAddEventV1) -> ChannelModeratorAddEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelModeratorAddEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelModeratorRemoveEvent(NamedTuple):
    """
    Represents the removal of a channel moderator.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was removed as a moderator.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    raw: eventsub.ChannelModeratorRemoveEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelModeratorRemoveEventV1) -> ChannelModeratorRemoveEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelModeratorRemoveEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class EventChannelPointsAutomaticReward(NamedTuple):
    type: str
    cost: int
    unlocked_emote: Optional[EventEmote]

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsAutomaticReward) -> EventChannelPointsAutomaticReward:
        emote_data = data.get('unlocked_emote')
        return cls(
            type=data['type'],
            cost=data['cost'],
            unlocked_emote=EventEmote.from_data(emote_data) if emote_data else None
        )


class EventChannelPointsAutomaticRewardV2(NamedTuple):
    type: str
    channel_points: int
    emote: Optional[EventEmote]

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsAutomaticRewardV2) -> EventChannelPointsAutomaticRewardV2:
        emote_data = data.get('emote')
        return cls(
            type=data['type'],
            channel_points=data['channel_points'],
            emote=EventEmote.from_data(emote_data) if emote_data else None
        )


class ChannelPointsAutomaticRewardRedemptionAddEventV1(NamedTuple):
    """
    Represents the redemption of an automatic channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who redeemed the reward.
    id: str
        Unique identifier for the redemption.
    reward: EventChannelPointsAutomaticReward
        Details of the redeemed automatic reward.
    message: EventSubscriptionMessage
        Message associated with the redemption.
    user_input: str
        User-provided input for the redemption
    redeemed_at: datetime.datetime
        Timestamp when the reward was redeemed.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    reward: EventChannelPointsAutomaticReward
    message: EventSubscriptionMessage
    user_input: str
    redeemed_at: datetime.datetime
    raw: eventsub.ChannelPointsAutomaticRewardRedemptionAddEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsAutomaticRewardRedemptionAddEventV1
                  ) -> ChannelPointsAutomaticRewardRedemptionAddEventV1:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            reward=EventChannelPointsAutomaticReward.from_data(data['reward']),
            message=EventSubscriptionMessage.from_data(data['message']),
            user_input=data['user_input'],
            redeemed_at=from_iso_string(data['redeemed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsAutomaticRewardRedemptionAddEventV1) -> bool:
        if not isinstance(other, ChannelPointsAutomaticRewardRedemptionAddEventV1):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsAutomaticRewardRedemptionAddEventV1(id={self.id!r}, user={self.user.login!r})"


class ChannelPointsAutomaticRewardRedemptionAddEventV2(NamedTuple):
    """
    Represents the redemption of an automatic channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who redeemed the reward.
    id: str
        Unique identifier for the redemption.
    reward: EventChannelPointsAutomaticRewardV2
        Details of the redeemed automatic reward.
    message: EventMessage
        Message associated with the redemption.
    redeemed_at: datetime.datetime
        Timestamp when the reward was redeemed.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    reward: EventChannelPointsAutomaticRewardV2
    message: EventMessage
    redeemed_at: datetime.datetime
    raw: eventsub.ChannelPointsAutomaticRewardRedemptionAddEventV2

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsAutomaticRewardRedemptionAddEventV2
                  ) -> ChannelPointsAutomaticRewardRedemptionAddEventV2:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            reward=EventChannelPointsAutomaticRewardV2.from_data(data['reward']),
            message=EventMessage.from_data(data['message']),
            redeemed_at=from_iso_string(data['redeemed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsAutomaticRewardRedemptionAddEventV2) -> bool:
        if not isinstance(other, ChannelPointsAutomaticRewardRedemptionAddEventV2):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsAutomaticRewardRedemptionAddEventV2(id={self.id!r}, user={self.user.login!r})"

class EventCustomReward(NamedTuple):
    """
    Represents a custom channel points reward.

    Attributes
    ----------
    id: str
        Unique identifier for the custom reward.
    title: str
        The title/name of the custom reward.
    cost: int
        Channel points cost required to redeem this reward.
    prompt: str
        Description or prompt text for the custom reward.
    """

    id: str
    title: str
    cost: int
    prompt: str

    @classmethod
    def from_data(cls, data: eventsub.CustomReward) -> EventCustomReward:
        return cls(
            id=data['id'],
            title=data['title'],
            cost=data['cost'],
            prompt=data['prompt']
        )


class EventGlobalCooldown(NamedTuple):
    """
    Represents global cooldown settings for a reward or feature.

    Attributes
    ----------
    is_enabled: bool
        Whether the global cooldown is enabled.
    seconds: int
        Duration of the global cooldown in seconds.
    """

    is_enabled: bool
    seconds: int

    @classmethod
    def from_data(cls, data: eventsub.GlobalCooldown) -> EventGlobalCooldown:
        return cls(
            is_enabled=data['is_enabled'],
            seconds=data['seconds']
        )


class EventMaxPerStream(NamedTuple):
    """
    Represents maximum per stream limit settings.

    Attributes
    ----------
    is_enabled: bool
        Whether the per-stream limit is enabled.
    value: int
        Maximum number allowed per stream.
    """

    is_enabled: bool
    value: int

    @classmethod
    def from_data(cls, data: eventsub.MaxPerStream) -> EventMaxPerStream:
        return cls(
            is_enabled=data['is_enabled'],
            value=data['value']
        )


class EventMaxPerUserPerStream(NamedTuple):
    """
    Represents maximum per user per stream limit settings.

    Attributes
    ----------
    is_enabled: bool
        Whether the per-user per-stream limit is enabled.
    value: int
        Maximum number allowed per user per stream.
    """

    is_enabled: bool
    value: int

    @classmethod
    def from_data(cls, data: eventsub.MaxPerUserPerStream) -> EventMaxPerUserPerStream:
        return cls(
            is_enabled=data['is_enabled'],
            value=data['value']
        )


class EventImage(NamedTuple):
    """
    Represents image URLs at different resolutions.

    Attributes
    ----------
    url_1x: str
        URL for the 1x resolution image.
    url_2x: str
        URL for the 2x resolution image.
    url_4x: str
        URL for the 4x resolution image.
    """

    url_1x: str
    url_2x: str
    url_4x: str

    @classmethod
    def from_data(cls, data: eventsub.Image) -> EventImage:
        return cls(
            url_1x=data['url_1x'],
            url_2x=data['url_2x'],
            url_4x=data['url_4x']
        )

class ChannelPointsCustomRewardAddEvent(NamedTuple):
    """
    Represents the creation of a custom channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the reward.
    is_enabled: bool
        Whether the reward is enabled.
    is_paused: bool
        Whether the reward is paused.
    is_in_stock: bool
        Whether the reward is in stock.
    title: str
        Title of the reward.
    cost: int
        Cost of the reward in channel points.
    prompt: str
        Prompt or description of the reward.
    is_user_input_required: bool
        Whether user input is required for redemption.
    should_redemptions_skip_request_queue: bool
        Whether redemptions skip the request queue.
    cooldown_expires_at: Optional[datetime.datetime]
        Timestamp when the cooldown expires
    redemptions_redeemed_current_stream: Optional[int]
        Number of redemptions in the current stream
    max_per_stream: EventMaxPerStream
        Maximum redemptions per stream settings.
    max_per_user_per_stream: EventMaxPerUserPerStream
        Maximum redemptions per user per stream settings.
    global_cooldown: EventGlobalCooldown
        Global cooldown settings for the reward.
    background_color: str
        Background color of the reward.
    image: EventImage
        Custom image for the reward.
    default_image: EventImage
        Default image for the reward.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    is_enabled: bool
    is_paused: bool
    is_in_stock: bool
    title: str
    cost: int
    prompt: str
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool
    cooldown_expires_at: Optional[datetime.datetime]
    redemptions_redeemed_current_stream: Optional[int]
    max_per_stream: EventMaxPerStream
    max_per_user_per_stream: EventMaxPerUserPerStream
    global_cooldown: EventGlobalCooldown
    background_color: str
    image: EventImage
    default_image: EventImage
    raw: eventsub.ChannelPointsCustomRewardAddEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsCustomRewardAddEventV1) -> ChannelPointsCustomRewardAddEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            is_enabled=data['is_enabled'],
            is_paused=data['is_paused'],
            is_in_stock=data['is_in_stock'],
            title=data['title'],
            cost=data['cost'],
            prompt=data['prompt'],
            is_user_input_required=data['is_user_input_required'],
            should_redemptions_skip_request_queue=data['should_redemptions_skip_request_queue'],
            cooldown_expires_at=from_iso_string(data['cooldown_expires_at']) if data['cooldown_expires_at'] else None,
            redemptions_redeemed_current_stream=data['redemptions_redeemed_current_stream'],
            max_per_stream=EventMaxPerStream.from_data(data['max_per_stream']),
            max_per_user_per_stream=EventMaxPerUserPerStream.from_data(data['max_per_user_per_stream']),
            global_cooldown=EventGlobalCooldown.from_data(data['global_cooldown']),
            background_color=data['background_color'],
            image=EventImage.from_data(data['image']),
            default_image=EventImage.from_data(data['default_image']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsCustomRewardAddEvent) -> bool:
        if not isinstance(other, ChannelPointsCustomRewardAddEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsCustomRewardAddEvent(id={self.id!r}, title={self.title!r})"


class ChannelPointsCustomRewardUpdateEvent(NamedTuple):
    """
    Represents an update to a custom channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the reward.
    is_enabled: bool
        Whether the reward is enabled.
    is_paused: bool
        Whether the reward is paused.
    is_in_stock: bool
        Whether the reward is in stock.
    title: str
        Title of the reward.
    cost: int
        Cost of the reward in channel points.
    prompt: str
        Prompt or description of the reward.
    is_user_input_required: bool
        Whether user input is required for redemption.
    should_redemptions_skip_request_queue: bool
        Whether redemptions skip the request queue.
    cooldown_expires_at: Optional[datetime.datetime]
        Timestamp when the cooldown expires
    redemptions_redeemed_current_stream: Optional[int]
        Number of redemptions in the current stream
    max_per_stream: EventMaxPerStream
        Maximum redemptions per stream settings.
    max_per_user_per_stream: EventMaxPerUserPerStream
        Maximum redemptions per user per stream settings.
    global_cooldown: EventGlobalCooldown
        Global cooldown settings for the reward.
    background_color: str
        Background color of the reward.
    image: EventImage
        Custom image for the reward.
    default_image: EventImage
        Default image for the reward.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    is_enabled: bool
    is_paused: bool
    is_in_stock: bool
    title: str
    cost: int
    prompt: str
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool
    cooldown_expires_at: Optional[datetime.datetime]
    redemptions_redeemed_current_stream: Optional[int]
    max_per_stream: EventMaxPerStream
    max_per_user_per_stream: EventMaxPerUserPerStream
    global_cooldown: EventGlobalCooldown
    background_color: str
    image: EventImage
    default_image: EventImage
    raw: eventsub.ChannelPointsCustomRewardUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsCustomRewardUpdateEventV1) -> ChannelPointsCustomRewardUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            is_enabled=data['is_enabled'],
            is_paused=data['is_paused'],
            is_in_stock=data['is_in_stock'],
            title=data['title'],
            cost=data['cost'],
            prompt=data['prompt'],
            is_user_input_required=data['is_user_input_required'],
            should_redemptions_skip_request_queue=data['should_redemptions_skip_request_queue'],
            cooldown_expires_at=from_iso_string(data['cooldown_expires_at']) if data['cooldown_expires_at'] else None,
            redemptions_redeemed_current_stream=data['redemptions_redeemed_current_stream'],
            max_per_stream=EventMaxPerStream.from_data(data['max_per_stream']),
            max_per_user_per_stream=EventMaxPerUserPerStream.from_data(data['max_per_user_per_stream']),
            global_cooldown=EventGlobalCooldown.from_data(data['global_cooldown']),
            background_color=data['background_color'],
            image=EventImage.from_data(data['image']),
            default_image=EventImage.from_data(data['default_image']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsCustomRewardUpdateEvent) -> bool:
        if not isinstance(other, ChannelPointsCustomRewardUpdateEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsCustomRewardUpdateEvent(id={self.id!r}, title={self.title!r})"


class ChannelPointsCustomRewardRemoveEvent(NamedTuple):
    """
    Represents the removal of a custom channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the reward.
    is_enabled: bool
        Whether the reward was enabled before removal.
    is_paused: bool
        Whether the reward was paused before removal.
    is_in_stock: bool
        Whether the reward was in stock before removal.
    title: str
        Title of the reward.
    cost: int
        Cost of the reward in channel points.
    prompt: str
        Prompt or description of the reward.
    is_user_input_required: bool
        Whether user input was required for redemption.
    should_redemptions_skip_request_queue: bool
        Whether redemptions skipped the request queue.
    cooldown_expires_at: Optional[datetime.datetime]
        Timestamp when the cooldown would have expired
    redemptions_redeemed_current_stream: Optional[int]
        Number of redemptions in the current stream before removal
    max_per_stream: EventMaxPerStream
        Maximum redemptions per stream settings.
    max_per_user_per_stream: EventMaxPerUserPerStream
        Maximum redemptions per user per stream settings.
    global_cooldown: EventGlobalCooldown
        Global cooldown settings for the reward.
    background_color: str
        Background color of the reward.
    image: EventImage
        Custom image for the reward.
    default_image: EventImage
        Default image for the reward.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    is_enabled: bool
    is_paused: bool
    is_in_stock: bool
    title: str
    cost: int
    prompt: str
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool
    cooldown_expires_at: Optional[datetime.datetime]
    redemptions_redeemed_current_stream: Optional[int]
    max_per_stream: EventMaxPerStream
    max_per_user_per_stream: EventMaxPerUserPerStream
    global_cooldown: EventGlobalCooldown
    background_color: str
    image: EventImage
    default_image: EventImage
    raw: eventsub.ChannelPointsCustomRewardRemoveEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsCustomRewardRemoveEventV1) -> ChannelPointsCustomRewardRemoveEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            is_enabled=data['is_enabled'],
            is_paused=data['is_paused'],
            is_in_stock=data['is_in_stock'],
            title=data['title'],
            cost=data['cost'],
            prompt=data['prompt'],
            is_user_input_required=data['is_user_input_required'],
            should_redemptions_skip_request_queue=data['should_redemptions_skip_request_queue'],
            cooldown_expires_at=from_iso_string(data['cooldown_expires_at']) if data['cooldown_expires_at'] else None,
            redemptions_redeemed_current_stream=data['redemptions_redeemed_current_stream'],
            max_per_stream=EventMaxPerStream.from_data(data['max_per_stream']),
            max_per_user_per_stream=EventMaxPerUserPerStream.from_data(data['max_per_user_per_stream']),
            global_cooldown=EventGlobalCooldown.from_data(data['global_cooldown']),
            background_color=data['background_color'],
            image=EventImage.from_data(data['image']),
            default_image=EventImage.from_data(data['default_image']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsCustomRewardRemoveEvent) -> bool:
        if not isinstance(other, ChannelPointsCustomRewardRemoveEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsCustomRewardRemoveEvent(id={self.id!r}, title={self.title!r})"


class ChannelPointsCustomRewardRedemptionAddEvent(NamedTuple):
    """
    Represents the redemption of a custom channel points reward.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who redeemed the reward.
    id: str
        Unique identifier for the redemption.
    user_input: str
        User-provided input for the redemption
    status: Literal['unfulfilled', 'fulfilled', 'canceled']
        Status of the redemption.
    reward: EventCustomReward
        Details of the redeemed custom reward.
    redeemed_at: datetime.datetime
        Timestamp when the reward was redeemed.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    user_input: str
    status: Literal['unfulfilled', 'fulfilled', 'canceled']
    reward: EventCustomReward
    redeemed_at: datetime.datetime
    raw: eventsub.ChannelPointsCustomRewardRedemptionAddEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsCustomRewardRedemptionAddEventV1
                  ) -> ChannelPointsCustomRewardRedemptionAddEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            user_input=data['user_input'],
            status=data['status'],
            reward=EventCustomReward.from_data(data['reward']),
            redeemed_at=from_iso_string(data['redeemed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsCustomRewardRedemptionAddEvent) -> bool:
        if not isinstance(other, ChannelPointsCustomRewardRedemptionAddEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsCustomRewardRedemptionAddEvent(id={self.id!r}, user={self.user.login!r})"


class ChannelPointsCustomRewardRedemptionUpdateEvent(NamedTuple):
    """
    Represents an update to a custom channel points reward redemption.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who redeemed the reward.
    id: str
        Unique identifier for the redemption.
    user_input: str
        User-provided input for the redemption
    status: Literal['unfulfilled', 'fulfilled', 'canceled']
        Updated status of the redemption.
    reward: EventCustomReward
        Details of the redeemed custom reward.
    redeemed_at: datetime.datetime
        Timestamp when the reward was redeemed.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    user_input: str
    status: Literal['unfulfilled', 'fulfilled', 'canceled']
    reward: EventCustomReward
    redeemed_at: datetime.datetime
    raw: eventsub.ChannelPointsCustomRewardRedemptionUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPointsCustomRewardRedemptionUpdateEventV1
                  ) -> ChannelPointsCustomRewardRedemptionUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            user_input=data['user_input'],
            status=data['status'],
            reward=EventCustomReward.from_data(data['reward']),
            redeemed_at=from_iso_string(data['redeemed_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPointsCustomRewardRedemptionUpdateEvent) -> bool:
        if not isinstance(other, ChannelPointsCustomRewardRedemptionUpdateEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPointsCustomRewardRedemptionUpdateEvent(id={self.id!r}, user={self.user.login!r})"


class EventPollChoice(NamedTuple):
    """
    Represents a choice option in a poll event.

    Attributes
    ----------
    id: str
        Unique identifier for the poll choice.
    title: str
        The text/title of the poll choice.
    bits_votes: Optional[int]
        Number of votes cast using bits
    channel_points_votes: Optional[int]
        Number of votes cast using channel points
    votes: Optional[int]
        Total number of votes for this choice
    """

    id: str
    title: str
    bits_votes: Optional[int]
    channel_points_votes: Optional[int]
    votes: Optional[int]

    @classmethod
    def from_data(cls, data: eventsub.PollChoice) -> EventPollChoice:
        return cls(
            id=data['id'],
            title=data['title'],
            bits_votes=data.get('bits_votes'),
            channel_points_votes=data.get('channel_points_votes'),
            votes=data.get('votes')
        )


class EventPollVotingSettings(NamedTuple):
    """
    Represents voting settings for a poll event.

    Attributes
    ----------
    is_enabled: bool
        Whether voting is enabled for this poll.
    amount_per_vote: int
        The amount required per vote (in bits or channel points).
    """

    is_enabled: bool
    amount_per_vote: int

    @classmethod
    def from_data(cls, data: eventsub.PollVotingSettings) -> EventPollVotingSettings:
        return cls(
            is_enabled=data['is_enabled'],
            amount_per_vote=data['amount_per_vote']
        )


class ChannelPollBeginEvent(NamedTuple):
    """
    Represents the start of a channel poll.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the poll.
    title: str
        Title of the poll.
    choices: Tuple[EventPollChoice, ...]
        Possible poll choices.
    bits_voting: EventPollVotingSettings
        Settings for voting with bits.
    channel_points_voting: EventPollVotingSettings
        Settings for voting with channel points.
    started_at: datetime.datetime
        Timestamp when the poll started.
    ends_at: datetime.datetime
        Timestamp when the poll ends.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    choices: Tuple[EventPollChoice, ...]
    bits_voting: EventPollVotingSettings
    channel_points_voting: EventPollVotingSettings
    started_at: datetime.datetime
    ends_at: datetime.datetime
    raw: eventsub.ChannelPollBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPollBeginEventV1) -> ChannelPollBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            choices=tuple(EventPollChoice.from_data(choice) for choice in data['choices']),
            bits_voting=EventPollVotingSettings.from_data(data['bits_voting']),
            channel_points_voting=EventPollVotingSettings.from_data(data['channel_points_voting']),
            started_at=from_iso_string(data['started_at']),
            ends_at=from_iso_string(data['ends_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPollBeginEvent) -> bool:
        if not isinstance(other, ChannelPollBeginEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPollBeginEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelPollProgressEvent(NamedTuple):
    """
    Represents progress updates for a channel poll.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the poll.
    title: str
        Title of the poll.
    choices: Tuple[EventPollChoice, ...]
        Possible poll choices with updated vote counts.
    bits_voting: EventPollVotingSettings
        Settings for voting with bits.
    channel_points_voting: EventPollVotingSettings
        Settings for voting with channel points.
    started_at: datetime.datetime
        Timestamp when the poll started.
    ends_at: datetime.datetime
        Timestamp when the poll ends.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    choices: Tuple[EventPollChoice, ...]
    bits_voting: EventPollVotingSettings
    channel_points_voting: EventPollVotingSettings
    started_at: datetime.datetime
    ends_at: datetime.datetime
    raw: eventsub.ChannelPollProgressEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPollProgressEventV1) -> ChannelPollProgressEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            choices=tuple(EventPollChoice.from_data(choice) for choice in data['choices']),
            bits_voting=EventPollVotingSettings.from_data(data['bits_voting']),
            channel_points_voting=EventPollVotingSettings.from_data(data['channel_points_voting']),
            started_at=from_iso_string(data['started_at']),
            ends_at=from_iso_string(data['ends_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPollProgressEvent) -> bool:
        if not isinstance(other, ChannelPollProgressEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPollProgressEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelPollEndEvent(NamedTuple):
    """
    Represents the end of a channel poll.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the poll.
    title: str
        Title of the poll.
    choices: Tuple[EventPollChoice, ...]
        Final poll choices with vote counts.
    bits_voting: EventPollVotingSettings
        Settings for voting with bits.
    channel_points_voting: EventPollVotingSettings
        Settings for voting with channel points.
    status: Literal['completed', 'archived', 'terminated']
        Final status of the poll.
    started_at: datetime.datetime
        Timestamp when the poll started.
    ended_at: datetime.datetime
        Timestamp when the poll ended.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    title: str
    choices: Tuple[EventPollChoice, ...]
    bits_voting: EventPollVotingSettings
    channel_points_voting: EventPollVotingSettings
    status: Literal['completed', 'archived', 'terminated']
    started_at: datetime.datetime
    ended_at: datetime.datetime
    raw: eventsub.ChannelPollEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelPollEndEventV1) -> ChannelPollEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            title=data['title'],
            choices=tuple(EventPollChoice.from_data(choice) for choice in data['choices']),
            bits_voting=EventPollVotingSettings.from_data(data['bits_voting']),
            channel_points_voting=EventPollVotingSettings.from_data(data['channel_points_voting']),
            status=data['status'],
            started_at=from_iso_string(data['started_at']),
            ended_at=from_iso_string(data['ended_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelPollEndEvent) -> bool:
        if not isinstance(other, ChannelPollEndEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelPollEndEvent(id={self.id!r}, status={self.status!r})"


class ChannelSuspiciousUserUpdateEvent(NamedTuple):
    """
    Represents an update to a user's suspicious status in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who updated the status.
    user: UserIdentity
        User whose suspicious status was updated.
    low_trust_status: str
        The updated low trust status of the user.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    user: UserIdentity
    low_trust_status: str
    raw: eventsub.ChannelSuspiciousUserUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSuspiciousUserUpdateEventV1) -> ChannelSuspiciousUserUpdateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            low_trust_status=data['low_trust_status'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSuspiciousUserUpdateEvent(user={self.user.login!r}, status={self.low_trust_status})"


class ChannelSuspiciousUserMessageEvent(NamedTuple):
    """
    Represents a message sent by a suspicious user in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        Suspicious user who sent the message.
    low_trust_status: str
        The low trust status of the user.
    shared_ban_channel_ids: Tuple[str, ...]
        IDs of channels that share a ban with this user.
    types: Tuple[str, ...]
        Types of suspicious behavior associated with the user.
    ban_evasion_evaluation: str
        Evaluation of the user's potential ban evasion.
    message: EventMessage
        Content and metadata of the suspicious message.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    low_trust_status: str
    shared_ban_channel_ids: Tuple[str, ...]
    types: Tuple[str, ...]
    ban_evasion_evaluation: str
    message: EventMessage
    raw: eventsub.ChannelSuspiciousUserMessageEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelSuspiciousUserMessageEventV1) -> ChannelSuspiciousUserMessageEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            low_trust_status=data['low_trust_status'],
            shared_ban_channel_ids=tuple(data['shared_ban_channel_ids']),
            types=tuple(data['types']),
            ban_evasion_evaluation=data['ban_evasion_evaluation'],
            message=EventMessage.from_data(data['message']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelSuspiciousUserMessageEvent(user={self.user.login!r}, status={self.low_trust_status!r})"


class ChannelVipAddEvent(NamedTuple):
    """
    Represents the addition of a VIP to a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was added as a VIP.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    raw: eventsub.ChannelVipAddEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelVipAddEventV1) -> ChannelVipAddEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelVipAddEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelVipRemoveEvent(NamedTuple):
    """
    Represents the removal of a VIP from a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who was removed as a VIP.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    raw: eventsub.ChannelVipRemoveEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelVipRemoveEventV1) -> ChannelVipRemoveEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelVipRemoveEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelWarningAcknowledgeEvent(NamedTuple):
    """
    Represents the acknowledgment of a warning in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who acknowledged the warning.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    raw: eventsub.ChannelWarningAcknowledgeEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelWarningAcknowledgeEventV1) -> ChannelWarningAcknowledgeEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelWarningAcknowledgeEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelWarningSendEvent(NamedTuple):
    """
    Represents the sending of a warning to a user in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who received the warning.
    moderator_user: UserIdentity
        Moderator who sent the warning.
    reason: Optional[str]
        Reason for the warning, if provided.
    chat_rules_cited: Optional[Tuple[str, ...]]
        Chat rules cited in the warning
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    moderator_user: UserIdentity
    reason: Optional[str]
    chat_rules_cited: Optional[Tuple[str, ...]]
    raw: eventsub.ChannelWarningSendEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelWarningSendEventV1) -> ChannelWarningSendEvent:
        chat_rules = data.get('chat_rules_cited')
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            reason=data.get('reason'),
            chat_rules_cited=tuple(chat_rules) if chat_rules else None,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelWarningSendEvent(user={self.user.login!r}, broadcaster={self.broadcaster_user.login!r})"


class EventCharityDonationAmount(NamedTuple):
    """
    Represents the amount details for a charity donation.

    Attributes
    ----------
    value: int
        The donation amount value as an integer.
    decimal_places: int
        Number of decimal places for the amount.
    currency: str
        Currency code for the donation amount.
    """

    value: int
    decimal_places: int
    currency: str

    @classmethod
    def from_data(cls, data: eventsub.CharityDonationAmount) -> EventCharityDonationAmount:
        return cls(
            value=data['value'],
            decimal_places=data['decimal_places'],
            currency=data['currency']
        )


class ChannelCharityCampaignDonationEvent(NamedTuple):
    """
    Represents a charity donation event in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who made the donation.
    id: str
        Unique identifier for the donation.
    campaign_id: str
        Identifier for the charity campaign.
    charity_name: str
        Name of the charity.
    charity_description: str
        Description of the charity.
    charity_logo: str
        URL of the charity's logo.
    charity_website: str
        URL of the charity's website.
    amount: EventCharityDonationAmount
        Donation amount details.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    campaign_id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    amount: EventCharityDonationAmount
    raw: eventsub.ChannelCharityDonationEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelCharityDonationEventV1) -> ChannelCharityCampaignDonationEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            campaign_id=data['campaign_id'],
            charity_name=data['charity_name'],
            charity_description=data['charity_description'],
            charity_logo=data['charity_logo'],
            charity_website=data['charity_website'],
            amount=EventCharityDonationAmount.from_data(data['amount']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelCharityCampaignDonationEvent) -> bool:
        if not isinstance(other, ChannelCharityCampaignDonationEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelCharityDonationEvent(id={self.id!r}, user={self.user.login!r})"


class ChannelCharityCampaignStartEvent(NamedTuple):
    """
    Represents the start of a charity campaign in a channel.

    Attributes
    ----------
    id: str
        Unique identifier for the charity campaign.
    broadcaster_user: UserIdentity
        Broadcaster user information.
    charity_name: str
        Name of the charity.
    charity_description: str
        Description of the charity.
    charity_logo: str
        URL of the charity's logo.
    charity_website: str
        URL of the charity's website.
    current_amount: EventCharityDonationAmount
        Current total amount raised.
    target_amount: EventCharityDonationAmount
        Target amount for the campaign.
    started_at: datetime.datetime
        Timestamp when the campaign started.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster_user: UserIdentity
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: EventCharityDonationAmount
    target_amount: EventCharityDonationAmount
    started_at: datetime.datetime
    raw: eventsub.ChannelCharityCampaignStartEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelCharityCampaignStartEventV1) -> ChannelCharityCampaignStartEvent:
        return cls(
            id=data['id'],
            broadcaster_user=UserIdentity(
                id=data['broadcaster_id'],
                login=data['broadcaster_login'],
                name=data['broadcaster_name']
            ),
            charity_name=data['charity_name'],
            charity_description=data['charity_description'],
            charity_logo=data['charity_logo'],
            charity_website=data['charity_website'],
            current_amount=EventCharityDonationAmount.from_data(data['current_amount']),
            target_amount=EventCharityDonationAmount.from_data(data['target_amount']),
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelCharityCampaignStartEvent) -> bool:
        if not isinstance(other, ChannelCharityCampaignStartEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelCharityCampaignStartEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelCharityCampaignProgressEvent(NamedTuple):
    """
    Represents progress updates for a charity campaign in a channel.

    Attributes
    ----------
    id: str
        Unique identifier for the charity campaign.
    broadcaster_user: UserIdentity
        Broadcaster user information.
    charity_name: str
        Name of the charity.
    charity_description: str
        Description of the charity.
    charity_logo: str
        URL of the charity's logo.
    charity_website: str
        URL of the charity's website.
    current_amount: EventCharityDonationAmount
        Current total amount raised.
    target_amount: EventCharityDonationAmount
        Target amount for the campaign.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster_user: UserIdentity
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: EventCharityDonationAmount
    target_amount: EventCharityDonationAmount
    raw: eventsub.ChannelCharityCampaignProgressEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelCharityCampaignProgressEventV1) -> ChannelCharityCampaignProgressEvent:
        return cls(
            id=data['id'],
            broadcaster_user=UserIdentity(
                id=data['broadcaster_id'],
                login=data['broadcaster_login'],
                name=data['broadcaster_name']
            ),
            charity_name=data['charity_name'],
            charity_description=data['charity_description'],
            charity_logo=data['charity_logo'],
            charity_website=data['charity_website'],
            current_amount=EventCharityDonationAmount.from_data(data['current_amount']),
            target_amount=EventCharityDonationAmount.from_data(data['target_amount']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelCharityCampaignProgressEvent) -> bool:
        if not isinstance(other, ChannelCharityCampaignProgressEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelCharityCampaignProgressEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelCharityCampaignStopEvent(NamedTuple):
    """
    Represents the end of a charity campaign in a channel.

    Attributes
    ----------
    id: str
        Unique identifier for the charity campaign.
    broadcaster_user: UserIdentity
        Broadcaster user information.
    charity_name: str
        Name of the charity.
    charity_description: str
        Description of the charity.
    charity_logo: str
        URL of the charity's logo.
    charity_website: str
        URL of the charity's website.
    current_amount: EventCharityDonationAmount
        Final total amount raised.
    target_amount: EventCharityDonationAmount
        Target amount for the campaign.
    stopped_at: datetime.datetime
        Timestamp when the campaign stopped.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    broadcaster_user: UserIdentity
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: EventCharityDonationAmount
    target_amount: EventCharityDonationAmount
    stopped_at: datetime.datetime
    raw: eventsub.ChannelCharityCampaignStopEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelCharityCampaignStopEventV1) -> ChannelCharityCampaignStopEvent:
        return cls(
            id=data['id'],
            broadcaster_user=UserIdentity(
                id=data['broadcaster_id'],
                login=data['broadcaster_login'],
                name=data['broadcaster_name']
            ),
            charity_name=data['charity_name'],
            charity_description=data['charity_description'],
            charity_logo=data['charity_logo'],
            charity_website=data['charity_website'],
            current_amount=EventCharityDonationAmount.from_data(data['current_amount']),
            target_amount=EventCharityDonationAmount.from_data(data['target_amount']),
            stopped_at=from_iso_string(data['stopped_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelCharityCampaignStopEvent) -> bool:
        if not isinstance(other, ChannelCharityCampaignStopEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelCharityCampaignStopEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelShieldModeBeginEvent(NamedTuple):
    """
    Represents the activation of Shield Mode in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who activated Shield Mode.
    started_at: datetime.datetime
        Timestamp when Shield Mode was activated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    started_at: datetime.datetime
    raw: eventsub.ChannelShieldModeBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelShieldModeBeginEventV1) -> ChannelShieldModeBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelShieldModeBeginEvent(broadcaster={self.broadcaster_user.login!r})"


class ChannelShieldModeEndEvent(NamedTuple):
    """
    Represents the deactivation of Shield Mode in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    moderator_user: UserIdentity
        Moderator who deactivated Shield Mode.
    ended_at: datetime.datetime
        Timestamp when Shield Mode was deactivated.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    ended_at: datetime.datetime
    raw: eventsub.ChannelShieldModeEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelShieldModeEndEventV1) -> ChannelShieldModeEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            ended_at=from_iso_string(data['ended_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __repr__(self) -> str:
        return f"ChannelShieldModeEndEvent(broadcaster={self.broadcaster_user.login!r})"


class ChannelShoutoutCreateEvent(NamedTuple):
    """
    Represents the creation of a shoutout from one broadcaster to another.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information of the channel sending the shoutout.
    moderator_user: UserIdentity
        Moderator who initiated the shoutout.
    to_broadcaster_user: UserIdentity
        Broadcaster user information of the channel receiving the shoutout.
    started_at: datetime.datetime
        Timestamp when the shoutout was created.
    viewer_count: int
        Number of viewers at the time of the shoutout.
    cooldown_ends_at: datetime.datetime
        Timestamp when the shoutout cooldown for the broadcaster ends.
    target_cooldown_ends_at: datetime.datetime
        Timestamp when the shoutout cooldown for the target broadcaster ends.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    moderator_user: UserIdentity
    to_broadcaster_user: UserIdentity
    started_at: datetime.datetime
    viewer_count: int
    cooldown_ends_at: datetime.datetime
    target_cooldown_ends_at: datetime.datetime
    raw: eventsub.ChannelShoutoutCreateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelShoutoutCreateEventV1) -> ChannelShoutoutCreateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            moderator_user=UserIdentity(
                id=data['moderator_user_id'],
                login=data['moderator_user_login'],
                name=data['moderator_user_name']
            ),
            to_broadcaster_user=UserIdentity(
                id=data['to_broadcaster_user_id'],
                login=data['to_broadcaster_user_login'],
                name=data['to_broadcaster_user_name']
            ),
            started_at=from_iso_string(data['started_at']),
            viewer_count=data['viewer_count'],
            cooldown_ends_at=from_iso_string(data['cooldown_ends_at']),
            target_cooldown_ends_at=from_iso_string(data['target_cooldown_ends_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __hash__(self) -> int:
        return hash((self.broadcaster_user.id, self.to_broadcaster_user.id, self.started_at))

    def __repr__(self) -> str:
        return f"ChannelShoutoutCreateEvent(to_broadcaster={self.to_broadcaster_user.login!r})"


class ChannelShoutoutReceiveEvent(NamedTuple):
    """
    Represents the receipt of a shoutout from another broadcaster.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information of the channel receiving the shoutout.
    from_broadcaster_user: UserIdentity
        Broadcaster user information of the channel sending the shoutout.
    viewer_count: int
        Number of viewers at the time of the shoutout.
    started_at: datetime.datetime
        Timestamp when the shoutout was received.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    from_broadcaster_user: UserIdentity
    viewer_count: int
    started_at: datetime.datetime
    raw: eventsub.ChannelShoutoutReceiveEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelShoutoutReceiveEventV1) -> ChannelShoutoutReceiveEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            from_broadcaster_user=UserIdentity(
                id=data['from_broadcaster_user_id'],
                login=data['from_broadcaster_user_login'],
                name=data['from_broadcaster_user_name']
            ),
            viewer_count=data['viewer_count'],
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __hash__(self) -> int:
        return hash((self.broadcaster_user.id, self.from_broadcaster_user.id, self.started_at))

    def __repr__(self) -> str:
        return f"ChannelShoutoutReceiveEvent(from_broadcaster={self.from_broadcaster_user.login!r})"


class ChannelGoalBeginEvent(NamedTuple):
    """
    Represents the start of a goal in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the goal.
    type: str
        Type of the goal (e.g., follower, subscription).
    description: str
        Description of the goal.
    current_amount: int
        Current progress toward the goal.
    target_amount: int
        Target amount for the goal.
    started_at: datetime.datetime
        Timestamp when the goal started.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    type: str
    description: str
    current_amount: int
    target_amount: int
    started_at: datetime.datetime
    raw: eventsub.ChannelGoalBeginEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelGoalBeginEventV1) -> ChannelGoalBeginEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            type=data['type'],
            description=data['description'],
            current_amount=data['current_amount'],
            target_amount=data['target_amount'],
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelGoalBeginEvent) -> bool:
        if not isinstance(other, ChannelGoalBeginEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelGoalBeginEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelGoalProgressEvent(NamedTuple):
    """
    Represents progress updates for a goal in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the goal.
    type: str
        Type of the goal (e.g., follower, subscription).
    description: str
        Description of the goal.
    current_amount: int
        Current progress toward the goal.
    target_amount: int
        Target amount for the goal.
    started_at: datetime.datetime
        Timestamp when the goal started.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    type: str
    description: str
    current_amount: int
    target_amount: int
    started_at: datetime.datetime
    raw: eventsub.ChannelGoalProgressEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelGoalProgressEventV1) -> ChannelGoalProgressEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            type=data['type'],
            description=data['description'],
            current_amount=data['current_amount'],
            target_amount=data['target_amount'],
            started_at=from_iso_string(data['started_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelGoalProgressEvent) -> bool:
        if not isinstance(other, ChannelGoalProgressEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelGoalProgressEvent(id={self.id!r}, broadcaster={self.broadcaster_user.login!r})"


class ChannelGoalEndEvent(NamedTuple):
    """
    Represents the end of a goal in a channel.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    id: str
        Unique identifier for the goal.
    type: str
        Type of the goal (e.g., follower, subscription).
    description: str
        Description of the goal.
    current_amount: int
        Final progress toward the goal.
    target_amount: int
        Target amount for the goal.
    started_at: datetime.datetime
        Timestamp when the goal started.
    is_achieved: bool
        Whether the goal was achieved.
    ended_at: datetime.datetime
        Timestamp when the goal ended.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    id: str
    type: str
    description: str
    current_amount: int
    target_amount: int
    started_at: datetime.datetime
    is_achieved: bool
    ended_at: datetime.datetime
    raw: eventsub.ChannelGoalEndEventV1

    @classmethod
    def from_data(cls, data: eventsub.ChannelGoalEndEventV1) -> ChannelGoalEndEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            id=data['id'],
            type=data['type'],
            description=data['description'],
            current_amount=data['current_amount'],
            target_amount=data['target_amount'],
            started_at=from_iso_string(data['started_at']),
            is_achieved=data['is_achieved'],
            ended_at=from_iso_string(data['ended_at']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ChannelGoalEndEvent) -> bool:
        if not isinstance(other, ChannelGoalEndEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ChannelGoalEndEvent(id={self.id!r}, is_achieved={self.is_achieved})"


class EventDropEntitlementGrantData(NamedTuple):
    """
    Represents the data for a drop entitlement grant event.

    Attributes
    ----------
    organization_id: str
        Identifier for the organization.
    category_id: str
        Identifier for the category.
    category_name: str
        Name of the category.
    campaign_id: str
        Identifier for the campaign.
    user: UserIdentity
        User who received the entitlement.
    entitlement_id: str
        Unique identifier for the entitlement.
    benefit_id: str
        Identifier for the benefit.
    created_at: datetime.datetime
        Timestamp when the entitlement was created.
    """

    organization_id: str
    category_id: str
    category_name: str
    campaign_id: str
    user: UserIdentity
    entitlement_id: str
    benefit_id: str
    created_at: datetime.datetime

    @classmethod
    def from_data(cls, data: eventsub.DropEntitlementGrantData) -> EventDropEntitlementGrantData:
        return cls(
            organization_id=data['organization_id'],
            category_id=data['category_id'],
            category_name=data['category_name'],
            campaign_id=data['campaign_id'],
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            entitlement_id=data['entitlement_id'],
            benefit_id=data['benefit_id'],
            created_at=from_iso_string(data['created_at']),
            raw=MappingProxyType(data)  # type: ignore
        )


class DropEntitlementGrantEvent(NamedTuple):
    """
    Represents a drop entitlement grant event.

    Attributes
    ----------
    id: str
        Unique identifier for the entitlement grant.
    data: EventDropEntitlementGrantData
        Detailed data about the entitlement grant.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    id: str
    data: EventDropEntitlementGrantData
    raw: eventsub.DropEntitlementGrantEventV1

    @classmethod
    def from_data(cls, data: eventsub.DropEntitlementGrantEventV1) -> DropEntitlementGrantEvent:
        return cls(
            id=data['id'],
            data=EventDropEntitlementGrantData.from_data(data['data']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: DropEntitlementGrantEvent) -> bool:
        if not isinstance(other, DropEntitlementGrantEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"DropEntitlementGrantEvent(id={self.id!r}, user={self.data.user.login!r})"


class EventExtensionProduct(NamedTuple):
    """
    Represents the product data for an extension bits transaction.

    Attributes
    ----------
    name: str
        Name of the product.
    sku: str
        Stock-keeping unit identifier for the product.
    bits: int
        Number of bits required for the product.
    in_development: bool
        Whether the product is in development.
    """

    name: str
    sku: str
    bits: int
    in_development: bool

    @classmethod
    def from_data(cls, data: eventsub.ExtensionProduct) -> EventExtensionProduct:
        return cls(
            name=data['name'],
            sku=data['sku'],
            bits=data['bits'],
            in_development=data['in_development']
        )


class ExtensionBitsTransactionCreateEvent(NamedTuple):
    """
    Represents the creation of an extension bits transaction.

    Attributes
    ----------
    broadcaster_user: UserIdentity
        Broadcaster user information.
    user: UserIdentity
        User who initiated the transaction.
    id: str
        Unique identifier for the transaction.
    extension_client_id: str
        Client ID of the extension.
    product: EventExtensionProduct
        Details of the product purchased.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    broadcaster_user: UserIdentity
    user: UserIdentity
    id: str
    extension_client_id: str
    product: EventExtensionProduct
    raw: eventsub.ExtensionBitsTransactionCreateEventV1

    @classmethod
    def from_data(cls, data: eventsub.ExtensionBitsTransactionCreateEventV1) -> ExtensionBitsTransactionCreateEvent:
        return cls(
            broadcaster_user=UserIdentity(
                id=data['broadcaster_user_id'],
                login=data['broadcaster_user_login'],
                name=data['broadcaster_user_name']
            ),
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            id=data['id'],
            extension_client_id=data['extension_client_id'],
            product=EventExtensionProduct.from_data(data['product']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ExtensionBitsTransactionCreateEvent) -> bool:
        if not isinstance(other, ExtensionBitsTransactionCreateEvent):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"ExtensionBitsTransactionCreateEvent(id={self.id!r}, user={self.user.login!r})"


class UserAuthorizationGrantEvent(NamedTuple):
    """
    Represents a user granting authorization to a client.

    Attributes
    ----------
    client_id: str
        Identifier of the client receiving authorization.
    user: UserIdentity
        User who granted the authorization.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    client_id: str
    user: UserIdentity
    raw: eventsub.UserAuthorizationGrantEventV1

    @classmethod
    def from_data(cls, data: eventsub.UserAuthorizationGrantEventV1) -> UserAuthorizationGrantEvent:
        return cls(
            client_id=data['client_id'],
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: UserAuthorizationGrantEvent) -> bool:
        if not isinstance(other, UserAuthorizationGrantEvent):
            return False
        return self.client_id == other.client_id and self.user.id == other.user.id

    def __hash__(self) -> int:
        return hash((self.client_id, self.user.id))

    def __repr__(self) -> str:
        return f"UserAuthorizationGrantEvent(user={self.user.login!r})"


class UserAuthorizationRevokeEvent(NamedTuple):
    """
    Represents a user revoking authorization from a client.

    Attributes
    ----------
    client_id: str
        Identifier of the client from which authorization was revoked.
    user_id: str
        Identifier of the user who revoked authorization.
    user_login: Optional[str]
        Login name of the user
    user_name: Optional[str]
        Display name of the user
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    client_id: str
    user_id: str
    user_login: Optional[str]
    user_name: Optional[str]
    raw: eventsub.UserAuthorizationRevokeEventV1

    @classmethod
    def from_data(cls, data: eventsub.UserAuthorizationRevokeEventV1) -> UserAuthorizationRevokeEvent:
        return cls(
            client_id=data['client_id'],
            user_id=data['user_id'],
            user_login=data['user_login'],
            user_name=data['user_name'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: UserAuthorizationRevokeEvent) -> bool:
        if not isinstance(other, UserAuthorizationRevokeEvent):
            return False
        return self.client_id == other.client_id and self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash((self.client_id, self.user_id))

    def __repr__(self) -> str:
        return f"UserAuthorizationRevokeEvent(user_id={self.user_id!r})"


class UserUpdateEvent(NamedTuple):
    """
    Represents an update to a user's profile information.

    Attributes
    ----------
    user: UserIdentity
        User whose profile was updated.
    email: str
        Updated email address of the user.
    email_verified: bool
        Whether the user's email is verified.
    description: str
        Updated description of the user.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    user: UserIdentity
    email: str
    email_verified: bool
    description: str
    raw: eventsub.UserUpdateEventV1

    @classmethod
    def from_data(cls, data: eventsub.UserUpdateEventV1) -> UserUpdateEvent:
        return cls(
            user=UserIdentity(
                id=data['user_id'],
                login=data['user_login'],
                name=data['user_name']
            ),
            email=data['email'],
            email_verified=data['email_verified'],
            description=data['description'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: UserUpdateEvent) -> bool:
        if not isinstance(other, UserUpdateEvent):
            return False
        return self.user.id == other.user.id

    def __hash__(self) -> int:
        return hash(self.user.id)

    def __repr__(self) -> str:
        return f"UserUpdateEvent(user={self.user.login!r})"


class EventWhisperData(NamedTuple):
    """
    Represents the data for a whisper message.

    Attributes
    ----------
    text: str
        Content of the whisper message.
    """

    text: str

    @classmethod
    def from_data(cls, data: eventsub.WhisperData) -> EventWhisperData:
        return cls(
            text=data['text'],
        )


class UserWhisperMessageEvent(NamedTuple):
    """
    Represents a whisper message sent from one user to another.

    Attributes
    ----------
    from_user: UserIdentity
        User who sent the whisper.
    to_user: UserIdentity
        User who received the whisper.
    whisper_id: str
        Unique identifier for the whisper message.
    whisper: EventWhisperData
        Content of the whisper message.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    from_user: UserIdentity
    to_user: UserIdentity
    whisper_id: str
    whisper: EventWhisperData
    raw: eventsub.UserWhisperMessageEventV1

    @classmethod
    def from_data(cls, data: eventsub.UserWhisperMessageEventV1) -> UserWhisperMessageEvent:
        return cls(
            from_user=UserIdentity(
                id=data['from_user_id'],
                login=data['from_user_login'],
                name=data['from_user_name']
            ),
            to_user=UserIdentity(
                id=data['to_user_id'],
                login=data['to_user_login'],
                name=data['to_user_name']
            ),
            whisper_id=data['whisper_id'],
            whisper=EventWhisperData.from_data(data['whisper']),
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: UserWhisperMessageEvent) -> bool:
        if not isinstance(other, UserWhisperMessageEvent):
            return False
        return self.whisper_id == other.whisper_id

    def __hash__(self) -> int:
        return hash(self.whisper_id)

    def __repr__(self) -> str:
        return f"UserWhisperMessageEvent(whisper_id={self.whisper_id!r}, from_user={self.from_user.login!r})"
