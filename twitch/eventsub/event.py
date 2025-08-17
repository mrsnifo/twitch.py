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

from typing import NamedTuple, TypeVar, Optional, Literal, Dict, Any, override, TYPE_CHECKING

if TYPE_CHECKING:
    from ..state import ClientConnectionState, ClientUserConnectionState
    from twitch.eventsub.gateway import Metadata
    from ..models import Subscription

__all__ = ('Event', 'UserEvents', 'AppEvents')

T = TypeVar('T')


class Event[T](NamedTuple):
    """
    EventSub event.

    Attributes
    ----------
    event: T
        The Eventsub event
    subscription: Subscription
        The subscription that triggered this event
    metadata: Metadata
        Metadata about the EventSub message
    """
    event: T
    subscription: Subscription
    metadata: Metadata

    @property
    def id(self) -> str:
        """
        Direct access to message ID.

        ???+ note

            No built-in duplicate message checking is provided. Check the messages on your
            own if you want accuracy.

        Provides a unique identifier for each event message. Messages are delivered
        at least once, and may be duplicated if delivery confirmation is uncertain.
        Duplicate messages will share the same ID, allowing for deduplication.

        Returns
        -------
        str
            The unique message ID from the metadata.
        """
        return self.metadata.message_id

    def __repr__(self) -> str:
        return f"Event(id={self.id!r}, event={self.event})"

    def __eq__(self, other: Event) -> bool:
        if not isinstance(other, Event):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class _BaseEvents:
    """Base class for handling event subscriptions."""

    __slots__ = ('_state', '_id')

    def __init__(self, user_id: str, *, state: ClientConnectionState):
        self._state: ClientConnectionState = state
        self._id: str = user_id

    async def _create_subscription(self,
                             subscription_type: str,
                             subscription_version: str,
                             subscription_condition: Dict[str, Any]) -> Subscription:
        pass

    async def automod_message_hold(
            self,
            broadcaster_user_id: str,
            moderator_user_id: str,
            version: Literal['1', '2'] = '2',
    ) -> Subscription:
        """
        Subscribe to automod message hold event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                     |
        |-------------|--------------------------|------------------------------------------------|
        | User Access | moderator:manage:automod | Token holder must be moderator/broadcaster     |
        | App Access  | moderator:manage:automod | User authorized app with scope, must be mod/bc |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: str
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1', '2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_automod_message_hold_v1(message: Event[AutomodHoldEventV1]):
                ...

        Version 2::

            @client.event
            async def on_automod_message_hold_v2(message: Event[AutomodHoldEventV2]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id,
        }
        return await self._create_subscription(
            subscription_type='automod.message.hold',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def automod_message_update(
            self,
            broadcaster_user_id: str,
            moderator_user_id: str,
            version: Literal['1', '2'] = '2',
    ) -> Subscription:
        """
        Subscribe to automod message update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | moderator:manage:automod | Token holder must be moderator/broadcaster                    |
        | App Access  | moderator:manage:automod | User authorized app with scope, must be moderator/broadcaster |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: str
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1', '2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_automod_message_update_v1(message: Event[AutomodUpdateEventV1]):
                ...

        Version 2::

            @client.event
            async def on_automod_message_update_v2(message: Event[AutomodUpdateEventV2]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id,
        }

        return await self._create_subscription(
            subscription_type='automod.message.update',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def automod_settings_update(
            self,
            broadcaster_user_id: str,
            moderator_user_id: str,
            version: Literal['1'] = '1',
    ) -> Subscription:
        """
        Subscribe to automod settings update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                 | Authorization Requirements                       |
        |-------------|---------------------------------|--------------------------------------------------|
        | User Access | moderator:read:automod_settings | Token holder must be moderator/broadcaster       |
        | App Access  | moderator:read:automod_settings | User authorized app with scope, must be mod/bc   |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: str
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_automod_settings_update_v1(message: Event[AutomodSettingsUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id,
        }
        return await self._create_subscription(
            subscription_type='automod.settings.update',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def automod_terms_update(
            self,
            broadcaster_user_id: str,
            moderator_user_id: str,
            version: Literal['1'] = '1',
    ) -> Subscription:
        """
        Subscribe to automod terms update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | moderator:manage:automod | Token holder must be moderator/broadcaster                    |
        | App Access  | moderator:manage:automod | User authorized app with scope, must be moderator/broadcaster |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: str
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_automod_terms_update_v1(message: Event[AutomodTermsUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'moderator_user_id': moderator_user_id,
        }
        return await self._create_subscription(
            subscription_type='automod.terms.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_update(
            self,
            broadcaster_user_id: str,
            version: Literal['2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 2::

            @client.event
            async def on_channel_update_v2(message: Event[ChannelUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='channel.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_clear(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat clear event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_clear_v1(message: Event[ChannelChatClearEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.clear',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_clear_user_messages(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat clear user messages event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_clear_user_messages_v1(message: Event[ChannelChatClearUserMessagesEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.clear_user_messages',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_message(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel chat message event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                            |
        |-------------|-----------------|-------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster            |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status    |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_message_v1(message: Event[ChannelChatMessageEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.message',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_message_delete(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel chat message delete event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_message_delete_v1(message: Event[ChannelChatMessageDeleteEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.message_delete',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_notification(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat notification event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_notification_v1(message: Event[ChannelChatNotificationEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.notification',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_settings_update(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat settings update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_settings_update_v1(message: Event[ChannelChatSettingsUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat_settings.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_user_message_hold(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat user message hold event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_user_message_hold_v1(message: Event[ChannelChatUserMessageHoldEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.user_message_hold',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_chat_user_message_update(
            self,
            broadcaster_user_id: str,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel chat user message update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | user:read:chat  | Token holder must be moderator/broadcaster                    |
        | App Access  | user:bot        | App must have user:bot + channel:bot or mod status            |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        user_id: str
            The user ID for the user that can read chat. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_chat_user_message_update_v1(message: Event[ChannelChatUserMessageUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id,
            'user_id': user_id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.user_message_update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shared_chat_begin(
            self,
            broadcaster_user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shared chat begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_shared_chat_begin_v1(message: Event[ChannelSharedChatBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shared_chat_update(
            self,
            broadcaster_user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shared chat update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_shared_chat_update_v1(message: Event[ChannelSharedChatUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shared_chat_end(
            self,
            broadcaster_user_id: str,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel shared chat end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_shared_chat_end_v1(message: Event[ChannelSharedChatEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_raid(
            self,
            from_broadcaster_user_id: Optional[str] = None,
            to_broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel raid event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        from_broadcaster_user_id: Optional[str]
            The broadcaster user ID that created the raid. Optional.
        to_broadcaster_user_id: Optional[str]
            The broadcaster user ID that received the raid. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_raid_v1(message: Event[ChannelRaidEvent]):
                ...
        """
        condition = {}
        if from_broadcaster_user_id:
            condition['from_broadcaster_user_id'] = from_broadcaster_user_id
        if to_broadcaster_user_id:
            condition['to_broadcaster_user_id'] = to_broadcaster_user_id
        return await self._create_subscription(
            subscription_type='channel.raid',
            subscription_version=version,
            subscription_condition=condition
        )

    async def stream_online(
            self,
            broadcaster_user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to stream online event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_stream_online_v1(message: Event[StreamOnlineEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='stream.online',
            subscription_version=version,
            subscription_condition=condition
        )

    async def stream_offline(
            self,
            broadcaster_user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to stream offline event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        broadcaster_user_id: str
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_stream_offline_v1(message: Event[StreamOfflineEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id
        }
        return await self._create_subscription(
            subscription_type='stream.offline',
            subscription_version=version,
            subscription_condition=condition
        )

    async def user_update(
            self,
            user_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to user update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | None                       |
        | App Access  | None            | None                       |

        Parameters
        ----------
        user_id: str
            The user ID to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_user_update_v1(message: Event[UserUpdateEvent]):
                ...
        """
        condition = {
            'user_id': user_id,
        }
        return await self._create_subscription(
            subscription_type='user.update',
            subscription_version=version,
            subscription_condition=condition
        )


class AppEvents(_BaseEvents):
    """Event handler for app-based event subscriptions using conduits."""

    __slots__ = ('conduit_id', '_transport')

    def __init__(self, user_id: str, conduit_id: str, state: ClientConnectionState):
        self.conduit_id: str = conduit_id
        super().__init__(user_id, state=state)
        self._transport = self._get_transport()

    def _get_transport(self) -> Dict[str, Any]:
        return {
            'method': 'conduit',
            'conduit_id': self.conduit_id
        }

    async def _create_subscription(self,
                                   subscription_type: str,
                                   subscription_version: str,
                                   subscription_condition: Dict[str, Any]) -> Subscription:
        return await self._state.create_subscription(
            self._id,
            subscription_type=subscription_type,
            subscription_version=subscription_version,
            subscription_condition=subscription_condition,
            transport=self._transport
        )

    async def conduit_shard_disabled(
            self,
            conduit_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to conduit shard disabled event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements           |
        |-------------|-----------------|--------------------------------------|
        | App Access  | None            | Client must own conduit if specified |

        Parameters
        ----------
        conduit_id: Optional[str]
            The conduit ID. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_conduit_shard_disabled_v1_raw(message: Event[Dict[str, Any]):
                ...
        """
        condition = {}
        if conduit_id:
            condition['conduit_id'] = conduit_id
        return await self._create_subscription(
            subscription_type='conduit.shard.disabled',
            subscription_version=version,
            subscription_condition=condition
        )

    async def drop_entitlement_grant(
            self,
            organization_id: str,
            category_id: Optional[str] = None,
            campaign_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to drop entitlement grant event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | Client owned by org        |

        Parameters
        ----------
        organization_id: str
            The organization ID.
        category_id: Optional[str]
            The category ID. Optional.
        campaign_id: Optional[str]
            The campaign ID. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_drop_entitlement_grant_v1(message: Event[DropEntitlementGrantEvent]):
                ...
        """
        condition = {
            'organization_id': organization_id
        }
        if category_id:
            condition['category_id'] = category_id
        if campaign_id:
            condition['campaign_id'] = campaign_id
        return await self._create_subscription(
            subscription_type='drop.entitlement.grant',
            subscription_version=version,
            subscription_condition=condition
        )

    async def user_authorization_grant(
            self,
            client_id: Optional[str] = None,
            version: Literal['1'] = '1',
    ) -> Subscription:
        """
        Subscribe to user authorization grant event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        client_id: Optional[str]
            The client ID.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_user_authorization_grant_v1(message: Event[UserAuthorizationGrantEvent]):
                ...
        """
        condition = {
            'client_id': client_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='user.authorization.grant',
            subscription_version=version,
            subscription_condition=condition
        )

    async def user_authorization_revoke(
            self,
            client_id: Optional[str] = None,
            version: Literal['1'] = '1',
    ) -> Subscription:
        """
        Subscribe to user authorization revoke event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        client_id: Optional[str]
            The client ID.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_user_authorization_revoke_v1(message: Event[UserAuthorizationRevokeEvent]):
                ...
        """
        condition = {
            'client_id': client_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='user.authorization.revoke',
            subscription_version=version,
            subscription_condition=condition
        )


class UserEvents(_BaseEvents):
    """Event handler for user-based event subscriptions."""

    if TYPE_CHECKING:
        _state: ClientUserConnectionState

    def __init__(self, user_id: str, state: ClientUserConnectionState):
        super().__init__(user_id, state=state)

    async def _create_subscription(self,
                             subscription_type: str,
                             subscription_version: str,
                             subscription_condition: Dict[str, Any]) -> Subscription:
        return await self._state.create_subscription(
            self._id,
            subscription_type=subscription_type,
            subscription_version=subscription_version,
            subscription_condition=subscription_condition
        )

    @override
    async def automod_message_hold(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1', '2'] = '2',
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='automod.message.hold',
            subscription_version=version,
            subscription_condition=condition,
        )

    @override
    async def automod_message_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1', '2'] = '2',
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id,
        }

        return await self._create_subscription(
            subscription_type='automod.message.update',
            subscription_version=version,
            subscription_condition=condition,
        )

    @override
    async def automod_settings_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1',
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='automod.settings.update',
            subscription_version=version,
            subscription_condition=condition,
        )

    @override
    async def automod_terms_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1',
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='automod.terms.update',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['2'] = '2'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.update',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_clear(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.clear',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_clear_user_messages(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.clear_user_messages',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_message(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.message',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_message_delete(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.message_delete',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_notification(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.notification',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_settings_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat_settings.update',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_user_message_hold(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.user_message_hold',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_chat_user_message_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.chat.user_message_update',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_shared_chat_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_shared_chat_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.update',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_shared_chat_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shared_chat.end',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def channel_raid(
            self,
            from_broadcaster_user_id: Optional[str] = None,
            to_broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {}
        if from_broadcaster_user_id:
            condition['from_broadcaster_user_id'] = from_broadcaster_user_id
        if to_broadcaster_user_id:
            condition['to_broadcaster_user_id'] = to_broadcaster_user_id or self._id
        return await self._create_subscription(
            subscription_type='channel.raid',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def stream_online(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='stream.online',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def stream_offline(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='stream.offline',
            subscription_version=version,
            subscription_condition=condition
        )

    @override
    async def user_update(
            self,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        condition = {
            'user_id': user_id or self._id,
        }
        return await self._create_subscription(
            subscription_type='user.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_bits_use(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel bits use event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements       |
        |-------------|-----------------|----------------------------------|
        | User Access | bits:read       | Token holder must be broadcaster |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_bits_use_v1(message: Event[ChannelBitsUseEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.bits.use',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_follow(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel follow event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | moderator:read:followers | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 2::

            @client.event
            async def on_channel_follow_v2(message: Event[ChannelFollowEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.follow',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_ad_break_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel ad break begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements                                    |
        |-------------|------------------|---------------------------------------------------------------|
        | User Access | channel:read:ads | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_ad_break_begin_v1(message: Event[ChannelAdBreakBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.ad_break.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_subscribe(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel subscribe event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements                             |
        |-------------|-------------------------------|--------------------------------------------------------|
        | User Access | channel:read:subscriptions    | Token holder must be broadcaster                       |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_subscribe_v1(message: Event[ChannelSubscribeEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.subscribe',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_subscription_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel subscription end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements                             |
        |-------------|-------------------------------|--------------------------------------------------------|
        | User Access | channel:read:subscriptions    | Token holder must be broadcaster                       |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_subscription_end_v1(message: Event[ChannelSubscriptionEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.subscription.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_subscription_gift(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel subscription gift event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements                             |
        |-------------|-------------------------------|--------------------------------------------------------|
        | User Access | channel:read:subscriptions    | Token holder must be broadcaster                       |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_subscription_gift_v1(message: Event[ChannelSubscriptionGiftEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.subscription.gift',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_subscription_message(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel subscription message event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements                            |
        |-------------|-------------------------------|-------------------------------------------------------|
        | User Access | channel:read:subscriptions    | Token holder must be broadcaster                      |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_subscription_message_v1(message: Event[ChannelSubscriptionMessageEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.subscription.message',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_cheer(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel cheer event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | bits:read       | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_cheer_v1(message: Event[ChannelCheerEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.cheer',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_ban(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel ban event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements                                    |
        |-------------|------------------|---------------------------------------------------------------|
        | User Access | channel:moderate | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_ban_v1(message: Event[ChannelBanEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.ban',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_unban(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel unban event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements                                    |
        |-------------|------------------|---------------------------------------------------------------|
        | User Access | channel:moderate | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_unban_v1(message: Event[ChannelUnbanEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.unban',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_unban_request_create(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel unban request create event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                 | Authorization Requirements                     |
        |-------------|---------------------------------|------------------------------------------------|
        | User Access | moderator:read:unban_requests   | Token holder must be mod/bc                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_unban_request_create_v1(message: Event[ChannelUnbanRequestCreateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.unban_request.create',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_unban_request_resolve(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel unban request resolve event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                 | Authorization Requirements                      |
        |-------------|---------------------------------|-------------------------------------------------|
        | User Access | moderator:read:unban_requests   | Token holder must be mod/bc                     |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_unban_request_resolve_v1(message: Event[ChannelUnbanRequestResolveEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.unban_request.resolve',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_moderate(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1', '2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel moderate event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                                    |
        |-------------|-----------------|---------------------------------------------------------------|
        | User Access | channel:moderate | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token. Required for version 2.
        version: Literal['1', '2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_moderate_v1(message: Event[ChannelModerateEventV1]):
                ...

        Version 2::

            @client.event
            async def on_channel_moderate_v2(message: Event[ChannelModerateEventV2]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
        }
        if version == '2':
            condition['moderator_user_id'] = moderator_user_id or self._id
        return await self._create_subscription(
            subscription_type='channel.moderate',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_moderator_add(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel moderator add event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements                                    |
        |-------------|------------------|---------------------------------------------------------------|
        | User Access | moderation:read  | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_moderator_add_v1(message: Event[ChannelModeratorAddEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.moderator.add',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_moderator_remove(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel moderator remove event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements                                    |
        |-------------|------------------|---------------------------------------------------------------|
        | User Access | moderation:read  | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_moderator_remove_v1(message: Event[ChannelModeratorRemoveEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.moderator.remove',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_automatic_reward_redemption_add(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1', '2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel points automatic reward redemption add event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements            |
        |-------------|-----------------------------|---------------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster      |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1', '2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_points_auto_reward_v1(
                message: Event[ChannelPointsAutomaticRewardRedemptionAddEventV1]):
                ...

        Version 2::

            @client.event
            async def on_channel_points_auto_reward_v2(
                message: Event[ChannelPointsAutomaticRewardRedemptionAddEventV2]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.channel_points_automatic_reward_redemption.add',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_custom_reward_add(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel points custom reward add event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements         |
        |-------------|-----------------------------|------------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster   |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_reward_add_v1(message: Event[ChannelPointsCustomRewardAddEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.channel_points_custom_reward.add',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_custom_reward_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            reward_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel points custom reward update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements            |
        |-------------|-----------------------------|---------------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster      |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        reward_id: Optional[str]
            The reward ID to monitor specific rewards. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_reward_update_v1(message: Event[ChannelPointsCustomRewardUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
        }
        if reward_id:
            condition['reward_id'] = reward_id
        return await self._create_subscription(
            subscription_type='channel.channel_points_custom_reward.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_custom_reward_remove(
            self,
            broadcaster_user_id: Optional[str] = None,
            reward_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel points custom reward remove event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements         |
        |-------------|-----------------------------|------------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster   |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        reward_id: Optional[str]
            The reward ID to monitor specific rewards. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_reward_remove_v1(message: Event[ChannelPointsCustomRewardRemoveEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
        }
        if reward_id:
            condition['reward_id'] = reward_id
        return await self._create_subscription(
            subscription_type='channel.channel_points_custom_reward.remove',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_custom_reward_redemption_add(
            self,
            broadcaster_user_id: Optional[str] = None,
            reward_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel points custom reward redemption add event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements         |
        |-------------|-----------------------------|------------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster   |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        reward_id: Optional[str]
            The reward ID to monitor specific rewards. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_reward_redeem_add_v1(
                message: Event[ChannelPointsCustomRewardRedemptionAddEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
        }
        if reward_id:
            condition['reward_id'] = reward_id
        return await self._create_subscription(
            subscription_type='channel.channel_points_custom_reward_redemption.add',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_points_custom_reward_redemption_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            reward_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel points custom reward redemption update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements        |
        |-------------|-----------------------------|-----------------------------------|
        | User Access | channel:read:redemptions    | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        reward_id: Optional[str]
            The reward ID to monitor specific rewards. Optional.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_reward_redeem_update_v1(
                message: Event[ChannelPointsCustomRewardRedemptionUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
        }
        if reward_id:
            condition['reward_id'] = reward_id
        return await self._create_subscription(
            subscription_type='channel.channel_points_custom_reward_redemption.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_poll_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1',
    ) -> Subscription:
        """
        Subscribe to channel poll begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements         |
        |-------------|-----------------------|------------------------------------|
        | User Access | channel:read:polls    | Token holder must be broadcaster   |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_poll_begin_v1(message: Event[ChannelPollBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.poll.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_poll_progress(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel poll progress event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements        |
        |-------------|-----------------------|-----------------------------------|
        | User Access | channel:read:polls    | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_poll_progress_v1(message: Event[ChannelPollProgressEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.poll.progress',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_poll_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel poll end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements        |
        |-------------|-----------------------|-----------------------------------|
        | User Access | channel:read:polls    | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_poll_end_v1(message: Event[ChannelPollEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.poll.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_prediction_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel prediction begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements        |
        |-------------|---------------------------|-----------------------------------|
        | User Access | channel:read:predictions  | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_prediction_begin_v1(message: Event[ChannelPredictionBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.prediction.begin',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def channel_prediction_progress(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel prediction progress event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements        |
        |-------------|---------------------------|-----------------------------------|
        | User Access | channel:read:predictions  | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_prediction_progress_v1(message: Event[ChannelPredictionProgressEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.prediction.progress',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def channel_prediction_lock(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel prediction lock event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements        |
        |-------------|---------------------------|-----------------------------------|
        | User Access | channel:read:predictions  | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_prediction_lock_v1(message: Event[ChannelPredictionLockEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.prediction.lock',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def channel_prediction_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel prediction end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements        |
        |-------------|---------------------------|-----------------------------------|
        | User Access | channel:read:predictions  | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_prediction_end_v1(message: Event[ChannelPredictionEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.prediction.end',
            subscription_version=version,
            subscription_condition=condition,
        )

    async def channel_suspicious_user_message(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel suspicious user message event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                    | Authorization Requirements                        |
        |-------------|------------------------------------|---------------------------------------------------|
        | User Access | moderator:read:suspicious_users    | Token holder must be moderator/broadcaster        |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_suspicious_user_message_v1(message: Event[ChannelSuspiciousUserMessageEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.suspicious_user.message',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_suspicious_user_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel suspicious user update event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                    | Authorization Requirements                       |
        |-------------|------------------------------------|--------------------------------------------------|
        | User Access | moderator:read:suspicious_users    | Token holder must be moderator/broadcaster       |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_suspicious_user_update_v1(message: Event[ChannelSuspiciousUserUpdateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.suspicious_user.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_vip_add(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel vip add event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes        | Authorization Requirements        |
        |-------------|------------------------|-----------------------------------|
        | User Access | moderator:read:vips    | Token holder must be broadcaster  |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_vip_add_v1(message: Event[ChannelVipAddEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.vip.add',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_vip_remove(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel vip remove event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes        | Authorization Requirements                                    |
        |-------------|------------------------|---------------------------------------------------------------|
        | User Access | moderator:read:vips    | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_vip_remove_v1(message: Event[ChannelVipRemoveEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.vip.remove',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_warning_acknowledge(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel warning acknowledge event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements                                    |
        |-------------|----------------------------|---------------------------------------------------------------|
        | User Access | moderator:read:warnings    | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_warning_acknowledge_v1(message: Event[ChannelWarningAcknowledgeEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.warning.acknowledge',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_warning_send(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel warning send event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements                                    |
        |-------------|----------------------------|---------------------------------------------------------------|
        | User Access | moderator:manage:warnings  | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_warning_send_v1(message: Event[ChannelWarningSendEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.warning.send',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_charity_campaign_donate(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel charity campaign donate event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | channel:read:charity     | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_charity_donate_v1(message: Event[ChannelCharityCampaignDonationEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.charity_campaign.donate',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_charity_campaign_start(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel charity campaign start event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | channel:read:charity     | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_charity_start_v1(message: Event[ChannelCharityCampaignStartEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.charity_campaign.start',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_charity_campaign_progress(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel charity campaign progress event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | channel:read:charity     | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_charity_progress_v1(message: Event[ChannelCharityCampaignProgressEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.charity_campaign.progress',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_charity_campaign_stop(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel charity campaign stop event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | channel:read:charity     | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_charity_stop_v1(message: Event[ChannelCharityCampaignStopEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.charity_campaign.stop',
            subscription_version=version,
            subscription_condition=condition
        )

    async def extension_bits_transaction_create(
            self,
            extension_client_id: str,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to extension bits transaction create event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | None            | Token client ID must match extension |

        Parameters
        ----------
        extension_client_id: str
            The extension client ID.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_extension_bits_transaction_create_v1(message: Event[ExtensionBitsTransactionCreateEvent]):
                ...
        """
        condition = {
            'extension_client_id': extension_client_id,
        }
        return await self._create_subscription(
            subscription_type='extension.bits_transaction.create',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_goal_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel goal begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements                                    |
        |-------------|-----------------------|---------------------------------------------------------------|
        | User Access | channel:read:goals    | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_goal_begin_v1(message: Event[ChannelGoalBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.goal.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_goal_progress(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'

    ) -> Subscription:
        """
        Subscribe to channel goal progress event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements                                    |
        |-------------|-----------------------|---------------------------------------------------------------|
        | User Access | channel:read:goals    | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_goal_progress_v1(message: Event[ChannelGoalProgressEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.goal.progress',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_goal_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel goal end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes       | Authorization Requirements                                    |
        |-------------|-----------------------|---------------------------------------------------------------|
        | User Access | channel:read:goals    | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_goal_end_v1(message: Event[ChannelGoalEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.goal.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_hype_train_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel hype train begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements                                    |
        |-------------|--------------------------|---------------------------------------------------------------|
        | User Access | channel:read:hype_train  | Token holder must be broadcaster                              |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_hype_train_begin_v2_raw(message: Event[Dict[str, Any]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.hype_train.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_hype_train_progress(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel hype train progress event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements              |
        |-------------|--------------------------|-----------------------------------------|
        | User Access | channel:read:hype_train  | Token holder must be broadcaster        |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 2::

            @client.event
            async def on_channel_hype_train_progress_v2_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.hype_train.progress',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_hype_train_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            version: Literal['2'] = '2'
    ) -> Subscription:
        """
        Subscribe to channel hype train end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements             |
        |-------------|--------------------------|----------------------------------------|
        | User Access | channel:read:hype_train  | Token holder must be broadcaster       |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        version: Literal['2']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 2::

            @client.event
            async def on_channel_hype_train_end_v2_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.hype_train.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shield_mode_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shield mode begin event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                  | Authorization Requirements                      |
        |-------------|----------------------------------|-------------------------------------------------|
        | User Access | moderator:read:shield_mode       | Token holder must be moderator/broadcaster      |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_shield_mode_begin_v1(message: Event[ChannelShieldModeBeginEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shield_mode.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shield_mode_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shield mode end event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                  | Authorization Requirements                 |
        |-------------|----------------------------------|--------------------------------------------|
        | User Access | moderator:read:shield_mode       | Token holder must be moderator/broadcaster |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_shield_mode_end_v1(message: Event[ChannelShieldModeEndEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shield_mode.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shoutout_create(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shoutout create event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements                                    |
        |-------------|---------------------------|---------------------------------------------------------------|
        | User Access | moderator:read:shoutouts  | Token holder must be moderator/broadcaster                    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_shoutout_create_v1(message: Event[ChannelShoutoutCreateEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shoutout.create',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_shoutout_receive(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to channel shoutout receive event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements                    |
        |-------------|---------------------------|-----------------------------------------------|
        | User Access | moderator:read:shoutouts  | Token holder must be moderator/broadcaster    |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Version 1::

            @client.event
            async def on_channel_shoutout_receive_v1(message: Event[ChannelShoutoutReceiveEvent]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.shoutout.receive',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_guest_star_session_begin(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['beta'] = 'beta'
    ) -> Subscription:
        """
        Subscribe to channel guest star session begin event (beta).

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements                  |
        |-------------|-----------------------------|---------------------------------------------|
        | User Access | channel:read:guest_star     | Token holder must be moderator/broadcaster  |
        |             | channel:manage:guest_star   |                                             |
        |             | moderator:read:guest_star   |                                             |
        |             | moderator:manage:guest_star |                                             |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['beta']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Beta::

            @client.event
            async def on_channel_guest_star_session_begin_beta_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.guest_star_session.begin',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_guest_star_session_end(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['beta'] = 'beta'
    ) -> Subscription:
        """
        Subscribe to channel guest star session end event (beta).

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements                  |
        |-------------|-----------------------------|---------------------------------------------|
        | User Access | channel:read:guest_star     | Token holder must be moderator/broadcaster  |
        |             | channel:manage:guest_star   |                                             |
        |             | moderator:read:guest_star   |                                             |
        |             | moderator:manage:guest_star |                                             |


        channel:manage:guest_star or moderator:read:guest_star or moderator:manage:guest_star

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['beta']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Beta::

            @client.event
            async def on_channel_guest_star_session_end_beta_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.guest_star_session.end',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_guest_star_guest_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['beta'] = 'beta'
    ) -> Subscription:
        """
        Subscribe to channel guest star guest update event (beta).

        Token and Authorization Requirements::

        | Token Type  | Required Scopes              | Authorization Requirements                   |
        |-------------|------------------------------|----------------------------------------------|
        | User Access | channel:read:guest_star      | Token holder must be moderator/broadcaster   |
        |             | channel:manage:guest_star    |                                              |
        |             | moderator:read:guest_star    |                                              |
        |             | moderator:manage:guest_star  |                                              |


        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['beta']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Beta::

            @client.event
            async def on_channel_guest_star_guest_update_beta_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.guest_star_guest.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def channel_guest_star_settings_update(
            self,
            broadcaster_user_id: Optional[str] = None,
            moderator_user_id: Optional[str] = None,
            version: Literal['beta'] = 'beta'
    ) -> Subscription:
        """
        Subscribe to channel guest star settings update event (beta).

        Token and Authorization Requirements::

        | Token Type  | Required Scopes             | Authorization Requirements                  |
        |-------------|-----------------------------|---------------------------------------------|
        | User Access | channel:read:guest_star     | Token holder must be moderator/broadcaster  |
        |             | channel:manage:guest_star   |                                             |
        |             | moderator:read:guest_star   |                                             |
        |             | moderator:manage:guest_star |                                             |

        Parameters
        ----------
        broadcaster_user_id: Optional[str]
            The broadcaster user ID for the channel to monitor.
        moderator_user_id: Optional[str]
            The moderator user ID. Must match the user ID in the access token.
        version: Literal['beta']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Beta::

            @client.event
            async def on_channel_guest_star_settings_update_beta_raw(message: Event[Dict[str, Any]]):
                ...
        """
        condition = {
            'broadcaster_user_id': broadcaster_user_id or self._id,
            'moderator_user_id': moderator_user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='channel.guest_star_settings.update',
            subscription_version=version,
            subscription_condition=condition
        )

    async def user_whisper_message(
            self,
            user_id: Optional[str] = None,
            version: Literal['1'] = '1'
    ) -> Subscription:
        """
        Subscribe to user whisper message event.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes    | Authorization Requirements |
        |-------------|--------------------|----------------------------|
        | User Access | user:read:whispers | None                       |

        Parameters
        ----------
        user_id: Optional[str]
            The user ID to monitor.
        version: Literal['1']
            The version number that identifies the definition of the subscription's data.

        Returns
        -------
        Subscription
            Created or existing subscription (based on ignore_conflict).

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token.
        BadRequest
            If the request parameters are invalid or websocket transport has different user subscriptions.
        Unauthorized
            If the token is invalid, expired, or lacks required scopes.
        Forbidden
            If subscription missing proper authorization.
        RateLimit
            The request exceeds the number of subscriptions that you may create.
        Conflict
            If a subscription with the same type and condition already exists.

        Examples
        --------
        Beta::

            @client.event
            async def on_user_whisper_message_1(message: Event[UserWhisperMessageEvent]):
                ...
        """
        condition = {
            'user_id': user_id or self._id
        }
        return await self._create_subscription(
            subscription_type='user.whisper.message',
            subscription_version=version,
            subscription_condition=condition
        )