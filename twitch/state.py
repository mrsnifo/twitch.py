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

from .errors import HTTPException, BadRequest, Unauthorized, Forbidden, Conflict
from typing import TYPE_CHECKING, Callable, Any, Dict, Optional, Tuple
from .eventsub.event import Event, AppEvents, UserEvents
from types import MappingProxyType
from .models import Subscription
from .api import AppAPI, UserAPI
from . import utils
import weakref
import inspect
import asyncio
import logging

from twitch.eventsub.models import (
    # Automod
    AutomodHoldEventV1, AutomodHoldEventV2, AutomodUpdateEventV1, AutomodUpdateEventV2,
    AutomodSettingsUpdateEvent, AutomodTermsUpdateEvent,

    # Bits, Channel, Chat
    ChannelBitsUseEvent, ChannelUpdateEvent, ChannelFollowEvent, ChannelAdBreakBeginEvent,
    ChannelChatClearEvent, ChannelChatClearUserMessagesEvent, ChannelChatMessageEvent,
    ChannelChatMessageDeleteEvent, ChannelChatNotificationEvent, ChannelChatSettingsUpdateEvent,
    ChannelChatUserMessageHoldEvent, ChannelChatUserMessageUpdateEvent,

    # Shared Chat, Subscriptions, Cheers, Raids
    ChannelSharedChatBeginEvent, ChannelSharedChatUpdateEvent, ChannelSharedChatEndEvent,
    ChannelSubscribeEvent, ChannelSubscriptionEndEvent, ChannelSubscriptionGiftEvent,
    ChannelSubscriptionMessageEvent, ChannelCheerEvent, ChannelRaidEvent,

    # Moderation
    ChannelBanEvent, ChannelUnbanEvent, ChannelUnbanRequestCreateEvent,
    ChannelUnbanRequestResolveEvent, ChannelModerateEventV1, ChannelModerateEventV2,
    ChannelModeratorAddEvent, ChannelModeratorRemoveEvent,

    # Channel Points
    ChannelPointsAutomaticRewardRedemptionAddEventV1,
    ChannelPointsAutomaticRewardRedemptionAddEventV2,
    ChannelPointsCustomRewardAddEvent, ChannelPointsCustomRewardUpdateEvent,
    ChannelPointsCustomRewardRemoveEvent, ChannelPointsCustomRewardRedemptionAddEvent,
    ChannelPointsCustomRewardRedemptionUpdateEvent,

    # Polls, Predictions
    ChannelPollBeginEvent, ChannelPollProgressEvent, ChannelPollEndEvent,
    ChannelPredictionBeginEvent, ChannelPredictionProgressEvent,
    ChannelPredictionLockEvent, ChannelPredictionEndEvent,

    # Suspicious Users, VIPs, Warnings
    ChannelSuspiciousUserMessageEvent, ChannelSuspiciousUserUpdateEvent,
    ChannelVipAddEvent, ChannelVipRemoveEvent,
    ChannelWarningAcknowledgeEvent, ChannelWarningSendEvent,

    # Charity, Drops, Goals
    ChannelCharityCampaignDonationEvent, ChannelCharityCampaignStartEvent,
    ChannelCharityCampaignProgressEvent, ChannelCharityCampaignStopEvent,
    DropEntitlementGrantEvent, ExtensionBitsTransactionCreateEvent,
    ChannelGoalBeginEvent, ChannelGoalProgressEvent, ChannelGoalEndEvent,

    # Shield Mode, Shoutouts, Stream, User
    ChannelShieldModeBeginEvent, ChannelShieldModeEndEvent,
    ChannelShoutoutCreateEvent, ChannelShoutoutReceiveEvent,
    StreamOnlineEvent, StreamOfflineEvent,
    UserAuthorizationGrantEvent, UserAuthorizationRevokeEvent,
    UserUpdateEvent, UserWhisperMessageEvent,
)

if TYPE_CHECKING:
    from twitch.eventsub.gateway import Metadata, EventSubWebSocket
    from .http import HTTPClient

__all__ = ('ConnectionState', 'ClientConnectionState', 'ClientUserConnectionState')

_logger = logging.getLogger(__name__)


class ConnectionState:
    def __init__(self, http: HTTPClient, **options) -> None:
        self.http: HTTPClient = http
        self.application: Optional[AppAPI] = None
        self._users: weakref.WeakValueDictionary[str, UserAPI] = weakref.WeakValueDictionary()

    def clear(self) -> None:
        self.application: Optional[AppAPI] = None
        self._users: weakref.WeakValueDictionary[str, UserAPI] = weakref.WeakValueDictionary()

    def store_user(self, user_id: str) -> UserAPI:
        try:
            return self._users[user_id]
        except KeyError:
            user = UserAPI(user_id, state=self)
            self._users[user_id] = user
            return user

    def get_user(self, user_id: str) -> Optional[UserAPI]:
        return self._users.get(user_id)

def event(
        name: str,
        **version_mappings: Any
    ) -> Callable[[Callable[..., None]], Callable[[Any, Dict[str, Any], Subscription, Metadata], None]]:
    def decorator(_: Callable[..., None]) -> Callable[[Any, Dict[str, Any], Subscription, Metadata], None]:
        def wrapper(
            self,
            data: Dict[str, Any],
            subscription: Subscription,
            metadata: Metadata
        ) -> None:
            version = subscription.version
            model = version_mappings.get(f'v{version}')
            if not model:
                _logger.debug("No model found for '%s' (version %s)", name, version)
                self.dispatch(f"{name}_v{version}_raw", Event(data, subscription, metadata))
                return
            self.dispatch(f"{name}_v{version}", Event(model.from_data(data), subscription, metadata))
        return wrapper
    return decorator


class ClientConnectionState(ConnectionState):
    def __init__(self, http: HTTPClient, dispatch: Callable[..., Any], **options: Any) -> None:
        super().__init__(http=http)
        self.ignore_conflict = options.get('ignore_conflict', True)
        self.http: HTTPClient = http
        self.dispatch: Callable[..., Any] = dispatch
        self.events: Optional[AppEvents | UserEvents] = None
        self.parsers: Dict[str, Callable[[Any], None]]
        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith('parse_'):
                parsers[attr[6:].lower()] = func

    async def create_subscription(self,
                                  user_id,
                                  /, *,
                                  subscription_type,
                                  subscription_version,
                                  subscription_condition: Dict[str, Any],
                                  transport: Dict[str, Any]
                                  ) -> Subscription:
        try:
            subscription_data = await self.http.create_eventsub_subscription(
                user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
                transport=transport
            )
            return Subscription.from_data(subscription_data['data'][0])
        except Conflict:

            if not self.ignore_conflict:
                raise

            subscription = await self._get_user_subscription(
                user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
                transport=transport
            )

            if subscription is not None:
                return subscription

            # rare-case where subscription deleted after receiving Conflict.
            return await self.create_subscription(
                user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
                transport=transport
            )

    async def _get_user_subscription(self,
                                     user_id: str,
                                     /, *,
                                     subscription_type: str,
                                     subscription_version: str,
                                     subscription_condition: Dict[str, Any],
                                     transport: Dict[str, Any]
                                     ) -> Optional[Subscription]:
        paginated_request = self.http.get_eventsub_subscriptions(
            user_id,
            subscription_user_id=next(iter(subscription_condition.values())),
            fetch_limit=None,
            subscription_id=None,
            status=None,
            subscriptions_type=None
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        async for subscription in paginated_request:
            if (
                subscription.condition == subscription_condition and
                subscription.type == subscription_type and
                subscription.version == subscription_version and
                subscription.transport == transport
            ):
                return subscription
        return None



    def clear(self):
        super().clear()
        self.events: Optional[AppEvents | UserEvents] = None

    @property
    def is_empty(self) -> bool:
        return False

    async def revocation(self, subscription: Subscription, metadata: Metadata):
        self.dispatch('revocation', subscription, metadata)

    @event('automod_message_hold', v1=AutomodHoldEventV1, v2=AutomodHoldEventV2)
    def parse_automod_message_hold(self,
                                   data: Dict[str, Any],
                                   subscription: Subscription,
                                   metadata: Metadata
                                   ) -> None: pass

    @event('automod_message_update', v1=AutomodUpdateEventV1, v2=AutomodUpdateEventV2)
    def parse_automod_message_update(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('automod_settings_update', v1=AutomodSettingsUpdateEvent)
    def parse_automod_settings_update(self,
                                      data: Dict[str, Any],
                                      subscription: Subscription,
                                      metadata: Metadata
                                      ) -> None: pass

    @event('automod_terms_update', v1=AutomodTermsUpdateEvent)
    def parse_automod_terms_update(self,
                                   data: Dict[str, Any],
                                   subscription: Subscription,
                                   metadata: Metadata
                                   ) -> None: pass

    @event('bits', v1=ChannelBitsUseEvent)
    def parse_channel_bits_use(self,
                               data: Dict[str, Any],
                               subscription: Subscription,
                               metadata: Metadata
                               ) -> None: pass

    @event('channel_update', v2=ChannelUpdateEvent)
    def parse_channel_update(self,
                             data: Dict[str, Any],
                             subscription: Subscription,
                             metadata: Metadata
                             ) -> None: pass

    @event('channel_follow', v2=ChannelFollowEvent)
    def parse_channel_follow(self,
                             data: Dict[str, Any],
                             subscription: Subscription,
                             metadata: Metadata
                             ) -> None: pass

    @event('channel_ad_break', v1=ChannelAdBreakBeginEvent)
    def parse_channel_ad_break_begin(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('chat_clear', v1=ChannelChatClearEvent)
    def parse_channel_chat_clear(self,
                                 data: Dict[str, Any],
                                 subscription: Subscription,
                                 metadata: Metadata
                                 ) -> None: pass

    @event('chat_clear_user', v1=ChannelChatClearUserMessagesEvent)
    def parse_channel_chat_clear_user_messages(self,
                                              data: Dict[str, Any],
                                              subscription: Subscription,
                                              metadata: Metadata
                                              ) -> None: pass

    @event('chat_message', v1=ChannelChatMessageEvent)
    def parse_channel_chat_message(self,
                                   data: Dict[str, Any],
                                   subscription: Subscription,
                                   metadata: Metadata
                                   ) -> None: pass

    @event('chat_message_delete', v1=ChannelChatMessageDeleteEvent)
    def parse_channel_chat_message_delete(self,
                                          data: Dict[str, Any],
                                          subscription: Subscription,
                                          metadata: Metadata
                                          ) -> None: pass

    @event('chat_notification', v1=ChannelChatNotificationEvent)
    def parse_channel_chat_notification(self,
                                        data: Dict[str, Any],
                                        subscription: Subscription,
                                        metadata: Metadata
                                        ) -> None: pass

    @event('chat_settings', v1=ChannelChatSettingsUpdateEvent)
    def parse_channel_chat_settings_update(self,
                                           data: Dict[str, Any],
                                           subscription: Subscription,
                                           metadata: Metadata
                                           ) -> None: pass

    @event('chat_user_message_hold', v1=ChannelChatUserMessageHoldEvent)
    def parse_channel_chat_user_message_hold(self,
                                             data: Dict[str, Any],
                                             subscription: Subscription,
                                             metadata: Metadata
                                             ) -> None: pass

    @event('chat_user_message_update', v1=ChannelChatUserMessageUpdateEvent)
    def parse_channel_chat_user_message_update(self,
                                               data: Dict[str, Any],
                                               subscription: Subscription,
                                               metadata: Metadata
                                               ) -> None: pass

    @event('shared_chat_begin', v1=ChannelSharedChatBeginEvent)
    def parse_channel_shared_chat_begin(self,
                                        data: Dict[str, Any],
                                        subscription: Subscription,
                                        metadata: Metadata
                                        ) -> None: pass

    @event('shared_chat_update', v1=ChannelSharedChatUpdateEvent)
    def parse_channel_shared_chat_update(self,
                                         data: Dict[str, Any],
                                         subscription: Subscription,
                                         metadata: Metadata
                                         ) -> None: pass

    @event('shared_chat_end', v1=ChannelSharedChatEndEvent)
    def parse_channel_shared_chat_end(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('channel_subscribe', v1=ChannelSubscribeEvent)
    def parse_channel_subscribe(self,
                                data: Dict[str, Any],
                                subscription: Subscription,
                                metadata: Metadata
                                ) -> None: pass

    @event('channel_subscription_end', v1=ChannelSubscriptionEndEvent)
    def parse_channel_subscription_end(self,
                                       data: Dict[str, Any],
                                       subscription: Subscription,
                                       metadata: Metadata
                                       ) -> None: pass

    @event('channel_subscription_gif', v1=ChannelSubscriptionGiftEvent)
    def parse_channel_subscription_gift(self,
                                        data: Dict[str, Any],
                                        subscription: Subscription,
                                        metadata: Metadata
                                        ) -> None: pass

    @event('channel_subscription_message', v1=ChannelSubscriptionMessageEvent)
    def parse_channel_subscription_message(self,
                                           data: Dict[str, Any],
                                           subscription: Subscription,
                                           metadata: Metadata
                                           ) -> None: pass

    @event('channel_cheer', v1=ChannelCheerEvent)
    def parse_channel_cheer(self,
                           data: Dict[str, Any],
                           subscription: Subscription,
                           metadata: Metadata
                          ) -> None: pass

    @event('channel_raid', v1=ChannelRaidEvent)
    def parse_channel_raid(self,
                          data: Dict[str, Any],
                          subscription: Subscription,
                          metadata: Metadata
                          ) -> None: pass

    @event('channel_ban', v1=ChannelBanEvent)
    def parse_channel_ban(self,
                          data: Dict[str, Any],
                          subscription: Subscription,
                          metadata: Metadata
                          ) -> None: pass

    @event('channel_unban', v1=ChannelUnbanEvent)
    def parse_channel_unban(self,
                            data: Dict[str, Any],
                            subscription: Subscription,
                            metadata: Metadata
                            ) -> None: pass

    @event('channel_unban_request_create', v1=ChannelUnbanRequestCreateEvent)
    def parse_channel_unban_request_create(self,
                                           data: Dict[str, Any],
                                           subscription: Subscription,
                                           metadata: Metadata
                                           ) -> None: pass

    @event('channel_unban_request_resolve', v1=ChannelUnbanRequestResolveEvent)
    def parse_channel_unban_request_resolve(self,
                                            data: Dict[str, Any],
                                            subscription: Subscription,
                                            metadata: Metadata
                                            ) -> None: pass

    @event('channel_moderate', v1=ChannelModerateEventV1, v2=ChannelModerateEventV2)
    def parse_channel_moderate(self,
                               data: Dict[str, Any],
                               subscription: Subscription,
                               metadata: Metadata
                               ) -> None: pass

    @event('channel_moderator_add', v1=ChannelModeratorAddEvent)
    def parse_channel_moderator_add(self,
                                    data: Dict[str, Any],
                                    subscription: Subscription,
                                    metadata: Metadata
                                    ) -> None: pass

    @event('channel_moderator_remove', v1=ChannelModeratorRemoveEvent)
    def parse_channel_moderator_remove(self,
                                       data: Dict[str, Any],
                                       subscription: Subscription,
                                       metadata: Metadata
                                       ) -> None: pass

    @event('channel_points_auto_reward',
               v1=ChannelPointsAutomaticRewardRedemptionAddEventV1,
               v2=ChannelPointsAutomaticRewardRedemptionAddEventV2)
    def parse_channel_channel_points_automatic_reward_redemption_add(self,
                                                                     data: Dict[str, Any],
                                                                     subscription: Subscription,
                                                                     metadata: Metadata
                                                                     ) -> None: pass

    @event('channel_reward_add', v1=ChannelPointsCustomRewardAddEvent)
    def parse_channel_channel_points_custom_reward_add(self,
                                                       data: Dict[str, Any],
                                                       subscription: Subscription,
                                                       metadata: Metadata
                                                       ) -> None: pass

    @event('channel_reward_update', v1=ChannelPointsCustomRewardUpdateEvent)
    def parse_channel_channel_points_custom_reward_update(self,
                                                          data: Dict[str, Any],
                                                          subscription: Subscription,
                                                          metadata: Metadata
                                                          ) -> None: pass

    @event('channel_reward_remove', v1=ChannelPointsCustomRewardRemoveEvent)
    def parse_channel_channel_points_custom_reward_remove(self,
                                                          data: Dict[str, Any],
                                                          subscription: Subscription,
                                                          metadata: Metadata
                                                          ) -> None: pass

    @event('channel_reward_redeem_add', v1=ChannelPointsCustomRewardRedemptionAddEvent)
    def parse_channel_channel_points_custom_reward_redemption_add(self,
                                                                  data: Dict[str, Any],
                                                                  subscription: Subscription,
                                                                  metadata: Metadata
                                                                  ) -> None: pass

    @event('channel_reward_redeem_update', v1=ChannelPointsCustomRewardRedemptionUpdateEvent)
    def parse_channel_channel_points_custom_reward_redemption_update(self,
                                                                     data: Dict[str, Any],
                                                                     subscription: Subscription,
                                                                     metadata: Metadata
                                                                     ) -> None: pass

    @event('channel_poll_begin', v1=ChannelPollBeginEvent)
    def parse_channel_poll_begin(self,
                                 data: Dict[str, Any],
                                 subscription: Subscription,
                                 metadata: Metadata
                                 ) -> None: pass

    @event('channel_poll_progress', v1=ChannelPollProgressEvent)
    def parse_channel_poll_progress(self,
                                    data: Dict[str, Any],
                                    subscription: Subscription,
                                    metadata: Metadata
                                    ) -> None: pass

    @event('channel_poll_end', v1=ChannelPollEndEvent)
    def parse_channel_poll_end(self,
                               data: Dict[str, Any],
                               subscription: Subscription,
                               metadata: Metadata
                               ) -> None: pass

    @event('channel_prediction_begin', v1=ChannelPredictionBeginEvent)
    def parse_channel_prediction_begin(self,
                                       data: Dict[str, Any],
                                       subscription: Subscription,
                                       metadata: Metadata
                                       ) -> None: pass

    @event('channel_prediction_progress', v1=ChannelPredictionProgressEvent)
    def parse_channel_prediction_progress(self,
                                          data: Dict[str, Any],
                                          subscription: Subscription,
                                          metadata: Metadata
                                          ) -> None: pass

    @event('channel_prediction_lock', v1=ChannelPredictionLockEvent)
    def parse_channel_prediction_lock(self,
                                      data: Dict[str, Any],
                                      subscription: Subscription,
                                      metadata: Metadata
                                      ) -> None: pass

    @event('channel_prediction_end', v1=ChannelPredictionEndEvent)
    def parse_channel_prediction_end(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('channel_suspicious_user_message', v1=ChannelSuspiciousUserMessageEvent)
    def parse_channel_suspicious_user_message(self,
                                              data: Dict[str, Any],
                                              subscription: Subscription,
                                              metadata: Metadata
                                              ) -> None: pass

    @event('channel_suspicious_user_update', v1=ChannelSuspiciousUserUpdateEvent)
    def parse_channel_suspicious_user_update(self,
                                             data: Dict[str, Any],
                                             subscription: Subscription,
                                             metadata: Metadata
                                             ) -> None: pass

    @event('channel_vip_add', v1=ChannelVipAddEvent)
    def parse_channel_vip_add(self,
                              data: Dict[str, Any],
                              subscription: Subscription,
                              metadata: Metadata
                              ) -> None: pass

    @event('vip_remove', v1=ChannelVipRemoveEvent)
    def parse_channel_vip_remove(self,
                                 data: Dict[str, Any],
                                 subscription: Subscription,
                                 metadata: Metadata
                                 ) -> None: pass

    @event('channel_warning_acknowledge', v1=ChannelWarningAcknowledgeEvent)
    def parse_channel_warning_acknowledge(self,
                                          data: Dict[str, Any],
                                          subscription: Subscription,
                                          metadata: Metadata
                                          ) -> None: pass

    @event('channel_warning_send', v1=ChannelWarningSendEvent)
    def parse_channel_warning_send(self,
                                   data: Dict[str, Any],
                                   subscription: Subscription,
                                   metadata: Metadata
                                   ) -> None: pass

    @event('channel_charity_donate', v1=ChannelCharityCampaignDonationEvent)
    def parse_channel_charity_campaign_donate(self,
                                              data: Dict[str, Any],
                                              subscription: Subscription,
                                              metadata: Metadata
                                              ) -> None: pass

    @event('channel_charity_start', v1=ChannelCharityCampaignStartEvent)
    def parse_channel_charity_campaign_start(self,
                                             data: Dict[str, Any],
                                             subscription: Subscription,
                                             metadata: Metadata
                                             ) -> None: pass

    @event('channel_charity_progress', v1=ChannelCharityCampaignProgressEvent)
    def parse_channel_charity_campaign_progress(self,
                                                data: Dict[str, Any],
                                                subscription: Subscription,
                                                metadata: Metadata
                                                ) -> None: pass

    @event('channel_charity_stop', v1=ChannelCharityCampaignStopEvent)
    def parse_channel_charity_campaign_stop(self,
                                            data: Dict[str, Any],
                                            subscription: Subscription,
                                            metadata: Metadata
                                            ) -> None: pass

    @event('drop_entitlement_grant', v1=DropEntitlementGrantEvent)
    def parse_drop_entitlement_grant(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('extension_bits_transaction_create', v1=ExtensionBitsTransactionCreateEvent)
    def parse_extension_bits_transaction_create(self,
                                                data: Dict[str, Any],
                                                subscription: Subscription,
                                                metadata: Metadata
                                                ) -> None: pass

    @event('channel_goal_begin', v1=ChannelGoalBeginEvent)
    def parse_channel_goal_begin(self,
                                 data: Dict[str, Any],
                                 subscription: Subscription,
                                 metadata: Metadata
                                 ) -> None: pass

    @event('channel_goal_progress', v1=ChannelGoalProgressEvent)
    def parse_channel_goal_progress(self,
                                    data: Dict[str, Any],
                                    subscription: Subscription,
                                    metadata: Metadata
                                    ) -> None: pass

    @event('channel_goal_end', v1=ChannelGoalEndEvent)
    def parse_channel_goal_end(self,
                               data: Dict[str, Any],
                               subscription: Subscription,
                               metadata: Metadata
                               ) -> None: pass

    @event('channel_shield_mode_begin', v1=ChannelShieldModeBeginEvent)
    def parse_channel_shield_mode_begin(self,
                                        data: Dict[str, Any],
                                        subscription: Subscription,
                                        metadata: Metadata
                                        ) -> None: pass

    @event('channel_shield_mode_end', v1=ChannelShieldModeEndEvent)
    def parse_channel_shield_mode_end(self,
                                      data: Dict[str, Any],
                                      subscription: Subscription,
                                      metadata: Metadata
                                      ) -> None: pass

    @event('channel_shoutout_create', v1=ChannelShoutoutCreateEvent)
    def parse_channel_shoutout_create(self,
                                      data: Dict[str, Any],
                                      subscription: Subscription,
                                      metadata: Metadata
                                      ) -> None: pass

    @event('channel_shoutout_receive', v1=ChannelShoutoutReceiveEvent)
    def parse_channel_shoutout_receive(self,
                                      data: Dict[str, Any],
                                      subscription: Subscription,
                                      metadata: Metadata
                                      ) -> None: pass

    @event('stream_online', v1=StreamOnlineEvent)
    def parse_stream_online(self,
                            data: Dict[str, Any],
                            subscription: Subscription,
                            metadata: Metadata
                            ) -> None: pass

    @event('stream_offline', v1=StreamOfflineEvent)
    def parse_stream_offline(self,
                             data: Dict[str, Any],
                             subscription: Subscription,
                             metadata: Metadata
                             ) -> None: pass

    @event('user_authorization_grant', v1=UserAuthorizationGrantEvent)
    def parse_user_authorization_grant(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('user_authorization_revoke', v1=UserAuthorizationRevokeEvent)
    def parse_user_authorization_revoke(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None: pass

    @event('user_update', v1=UserUpdateEvent)
    def parse_user_update(self,
                          data: Dict[str, Any],
                          subscription: Subscription,
                          metadata: Metadata
                          ) -> None: pass

    @event('user_whisper_message', v1=UserWhisperMessageEvent)
    def parse_user_whisper_message(self,
                                   data: Dict[str, Any],
                                   subscription: Subscription,
                                   metadata: Metadata
                                   ) -> None: pass

    @event('channel_guest_star_session_begin')
    def parse_channel_guest_star_session_begin(self,
                                               data: Dict[str, Any],
                                               subscription: Subscription,
                                               metadata: Metadata
                                               ) -> None:
        pass

    @event('channel_guest_star_session_end')
    def parse_channel_guest_star_session_end(self,
                                             data: Dict[str, Any],
                                             subscription: Subscription,
                                             metadata: Metadata
                                              ) -> None:
        pass

    @event('channel_guest_star_guest_update')
    def parse_channel_guest_star_guest_update(self,
                                              data: Dict[str, Any],
                                              subscription: Subscription,
                                              metadata: Metadata
                                              ) -> None:
        pass

    @event('channel_guest_star_settings_update')
    def parse_channel_guest_star_settings_update(self,
                                                 data: Dict[str, Any],
                                                 subscription: Subscription,
                                                 metadata: Metadata
                                                 ) -> None:
        pass

    @event('channel_guest_star_settings_update')
    def parse_channel_guest_star_settings_update(self,
                                                 data: Dict[str, Any],
                                                 subscription: Subscription,
                                                 metadata: Metadata
                                                 ) -> None:
        pass

    @event('channel_hype_train_begin')
    def parse_channel_hype_train_begin(self,
                                       data: Dict[str, Any],
                                       subscription: Subscription,
                                       metadata: Metadata
                                       ) -> None:
        pass

    @event('channel_hype_train_progress')
    def parse_channel_hype_train_progress(self,
                                          data: Dict[str, Any],
                                          subscription: Subscription,
                                          metadata: Metadata
                                          ) -> None:
        pass

    @event('channel_hype_train_end')
    def parse_channel_hype_train_end(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None:
        pass

    @event('conduit_shard_disabled')
    def parse_channel_hype_train_end(self,
                                     data: Dict[str, Any],
                                     subscription: Subscription,
                                     metadata: Metadata
                                     ) -> None:
        pass


class WebSocketSessionMismatchError(Exception):
    """Exception raised when WebSocket session ID mismatch occurs."""
    pass


class ClientUserConnectionState(ClientConnectionState):
    if TYPE_CHECKING:
        _get_websocket: Callable[..., Optional[EventSubWebSocket]]

    def __init__(self,
                 http: HTTPClient,
                 dispatch: Callable[..., Any],
                 handlers: Dict[str, Callable[..., None]],
                 **options
                ) -> None:
        super().__init__(http=http, dispatch=dispatch, **options)
        self.handlers: Dict[str, Callable[..., Any]] = handlers
        self._subscriptions: Dict[str, Dict[str, Subscription]] = {}
        self._subscription_costs: Dict[str, Tuple[int, int, int]] = {}
        self._subscription_lock = asyncio.Lock()
        self._resubscribe_task: Optional[asyncio.Task] = None
        self._session_welcome: asyncio.Event = asyncio.Event()

    @property
    def subscriptions(self) -> MappingProxyType[str, Tuple[Subscription, ...]]:
        """Returns a read-only mapping of user subscriptions."""
        result = {}
        for user_id, subs_dict in self._subscriptions.items():
            result[user_id] = tuple(subs_dict.values())
        return MappingProxyType(result)

    @property
    def subscription_costs(self) -> MappingProxyType[str, Tuple[int, int, int]]:
        """Returns a read-only mapping of subscription costs."""
        return MappingProxyType(self._subscription_costs)

    @property
    def is_empty(self) -> bool:
        """Check if any subscriptions exist."""
        return not any(self._subscriptions.values())

    def clear(self) -> None:
        """Reset all subscription state to initial values."""
        super().clear()
        self._subscriptions: Dict[str, Dict[str, Subscription]] = {}
        self._subscription_costs: Dict[str, Tuple[int, int, int]] = {}
        self._subscription_lock = asyncio.Lock()
        self._resubscribe_task: Optional[asyncio.Task] = None
        self._session_welcome: asyncio.Event = asyncio.Event()


    def establish_session(self, session_id: str) -> None:
        """Mark WebSocket session as established."""
        _logger.debug('Connected to WebSocket. Session ID: %s', session_id)
        self._session_welcome.set()

    def get_session_id(self) -> Optional[str]:
        """Get current WebSocket session ID if available."""
        ws = self._get_websocket()
        if ws is None or not ws.open or not ws.session_id:
            return None
        return ws.session_id

    async def wait(self, initial: bool = True) -> None:
        """Wait for subscription processing to complete."""
        if initial: self._subscription_costs.clear()
        if not self.is_empty:
            self.handlers['websocket_ready']()
        if self._resubscribe_task and not self._resubscribe_task.done():
            _logger.debug("Resubscription in progress, waiting for completion")
            await self._resubscribe_task

    async def drain_subscriptions(self) -> Dict[str, Dict[str, Subscription]]:
        """Remove and return all current subscriptions. """
        async with self._subscription_lock:
            events = self._subscriptions.copy()
            self._subscriptions = {}
        return events

    async def wait_for_session(self) -> str:
        """Wait for WebSocket session to be established."""
        while (session_id := self.get_session_id()) is None:
            self.handlers['websocket_ready']()
            _logger.debug("No session found, websocket enabled")
            self._session_welcome.clear()
            await self._session_welcome.wait()
        return session_id

    async def revocation(self, subscription: Subscription, metadata: Metadata):
        await super().revocation(subscription, metadata)
        await self.remove_subscription(subscription_id=subscription.id, cost=subscription.cost)

    async def remove_subscription(self, *, subscription_id: str, cost: Optional[int]) -> None:
        """Handle subscription revocation/deletion and update costs."""
        user_id = next((uid for uid, subs in self._subscriptions.items() if subscription_id in subs), None)
        if user_id:
            _logger.debug('Subscription removed: %s', subscription_id)

            async with self._subscription_lock:
                subscription = self._subscriptions.setdefault(user_id, {}).pop(subscription_id, None)

                if not self._subscriptions[user_id]:
                    del self._subscriptions[user_id]
                    if user_id in self._subscription_costs:
                        del self._subscription_costs[user_id]
                    return

                if user_id not in self._subscription_costs:
                    _logger.warning('Subscription costs for user %s not found, ignoring cost update',
                                    user_id)
                    return

                total, total_cost, max_cost = self._subscription_costs[user_id]
                if cost is None:
                    cost = subscription.cost if subscription else 0
                    _logger.warning('Subscription %s not found for cost calculation, using fallback cost: %s',
                                    subscription_id, cost)
                await self._update_cost(user_id, max(0, total - 1), max(0, total_cost - cost), max_cost)

    async def create_subscription(
            self,
            user_id,
            subscription_type,
            subscription_version,
            subscription_condition: Dict[str, Any],
            transport: Dict[str, Any] = None
    ) -> Subscription:
        backoff = utils.ExponentialBackoff(base_delay=1, max_delay=60)
        try:
            session_id = await asyncio.wait_for(self.wait_for_session(), timeout=30.0)
            subscription = await self._create_subscription(
                session_id,
                user_id=user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition
            )
            return subscription
        except (asyncio.TimeoutError, WebSocketSessionMismatchError):
            delay = backoff.get_delay()
            _logger.warning("Timeout waiting for session, retrying in %ss", delay)
            await asyncio.sleep(delay)
            return await self.create_subscription(
                user_id, subscription_type, subscription_version, subscription_condition
            )

    async def resubscribe_events(self, session_id: str, events: Dict[str, Dict[str, Subscription]]) -> None:
        """Resubscribe to existing events after session change."""
        if not events:
            return

        subscriptions = [(uid, sid, data) for uid, subs in events.items() for sid, data in subs.items()]
        processed = set()

        for user_id, sub_id, sub in subscriptions:
            try:
                await self._create_subscription(
                    session_id,
                    user_id=user_id,
                    subscription_type=sub.type,
                    subscription_version=sub.version,
                    subscription_condition=sub.condition.copy()
                )
                processed.add((user_id, sub_id))
            except WebSocketSessionMismatchError:
                break
            except (BadRequest, Unauthorized, Forbidden, Conflict) as exc:
                _logger.exception("Failed to resubscribe user ID %s %s event: %s - subscription removed",
                                  user_id, sub.type, exc)
                processed.add((user_id, sub_id))
            except (OSError, HTTPException):
                break

            if self.get_session_id() != session_id:
                break

        async with self._subscription_lock:
            for uid, subs in events.items():
                for sid, data in subs.items():
                    if (uid, sid) not in processed:
                        self._subscriptions.setdefault(uid, {})[sid] = data

    async def _update_cost(self, user_id: str, total: int, total_cost: int, max_total_cost: int) -> None:
        """Update subscription cost tracking for user."""
        self._subscription_costs[user_id] = (total, total_cost, max_total_cost)
        _logger.debug("Updated subscription costs for user ID %s with total=%s, cost=%s, max_cost=%s",
                      user_id, total, total_cost, max_total_cost)

    async def _get_user_subscription(self,
                                     user_id: str,
                                     /, *,
                                     subscription_type: str,
                                     subscription_version: str,
                                     subscription_condition: Dict[str, Any],
                                     transport: Dict[str, Any]
                                     ) -> Optional[Subscription]:
        subscriptions = self._subscriptions.get(user_id, {})
        for subscription in subscriptions.values():
            if (subscription.type == subscription_type and
                    subscription.version == subscription_version and
                    subscription.condition == subscription_condition):
                return subscription

        # Incase subscription not in the Local storage.
        subscription = await super()._get_user_subscription(
            user_id,
            subscription_type=subscription_type,
            subscription_version=subscription_version,
            subscription_condition=subscription_condition,
            transport=transport
        )
        self._subscriptions.setdefault(user_id, {})[subscription.id] = subscription
        return subscription

    async def _create_subscription(self,
                                   session_id: str,
                                   *,
                                   user_id: str,
                                   subscription_type: str,
                                   subscription_version: str,
                                   subscription_condition: Dict[str, Any]) -> Subscription:
        """Create a single subscription via API."""
        transport = {'method': 'websocket', 'session_id': session_id}
        try:
            data = await self.http.create_eventsub_subscription(
                user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
                transport=transport
            )
            async with self._subscription_lock:
                await self._update_cost(user_id, data['total'], data['total_cost'], data['max_total_cost'])
                subscription = Subscription.from_data(data['data'][0])
                self._subscriptions.setdefault(user_id, {})[subscription.id] = subscription
            return subscription
        except BadRequest as exc:
            if self.get_session_id() != session_id:
                raise WebSocketSessionMismatchError from exc
            raise
        except Conflict:

            if not self.ignore_conflict:
                raise

            subscription = await self._get_user_subscription(
                user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
                transport=transport
            )

            if subscription is not None:
                return subscription

            # rare-case where subscription deleted after receiving Conflict.
            return await self._create_subscription(
                session_id,
                user_id=user_id,
                subscription_type=subscription_type,
                subscription_version=subscription_version,
                subscription_condition=subscription_condition,
            )
