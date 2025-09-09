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

from typing import TYPE_CHECKING, Tuple, Set, override, Optional, Literal, overload, Dict, Any, List
from .utils import to_rfc3339_string, normalize_timezone
from datetime import datetime


from .models import (
    SharedChatSession, SendMessageStatus, UserChatColor, ChatSettings, Chatter, ChatBadgeSet,
    Cheermote, ChannelEmote, GlobalEmote, EmoteSet,
    ChannelInfo, UserInfo, ChannelFollower, FollowedChannel, ChannelEditor, ChannelVIP, ChannelTeam, TeamUsers,
    Video, Clip, StreamInfo, StreamMarker, ContentClassificationLabel, ChannelStreamSchedule,
    AutoModSettings, BannedUser, UnbanRequest, BlockedTerm, Moderator, ShieldModeStatus, WarnReason, Raid,
    Poll, Prediction, CreatorGoal, HypeTrainEvent, HypeTrainStatus,
    StarCommercial, Subscription, UserSubscription, BitsLeaderboardEntry, CharityCampaign, CharityDonation,
    AdSchedule, AdSnooze, AutoModStatusMessage,
    UserExtension, ActiveUserExtension, UserActiveExtensionUpdate, ExtensionTransaction, ExtensionBitsProduct,
    ExtensionLiveChannel, ExtensionConfiguration,
    AnalyticsReport,
    Category, Game, SearchChannel,
    ConduitShard, ConduitShardUpdate, Conduit, StreamKey,
    DropsEntitlement, DropsEntitlementUpdate, UserIdentity
)

if TYPE_CHECKING:
    from .state import ConnectionState, ClientUserConnectionState
    from .http import PaginatedRequest

__all__ = ('AppAPI', 'UserAPI')

class BaseAPI:

    __slots__ = ('_state', 'id')

    def __init__(self, user_id: str, *, state: ConnectionState) -> None:
        self._state: ConnectionState = state
        self.id = user_id

    async def get_cheermotes(self, user_id: Optional[str] = None) -> Tuple[Cheermote, ...]:
        """
        Gets a Tuple of Cheermotes that users can use to cheer Bits in any Bits-enabled channel's chat room.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: Optional[str]
            The ID of the broadcaster whose custom Cheermotes should be retrieved.
            If None, the response will include only global Cheermotes.

        Returns
        -------
        Tuple[Cheermote, ...]
            A tuple of Cheermote objects representing the available Cheermotes

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_cheermotes(self.id, broadcaster_id=user_id)
        return tuple(Cheermote.from_data(cheermote) for cheermote in data['data'])

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

    async def get_channel_emotes(self, user_id: str) -> Tuple[ChannelEmote, ...]:
        """
        Gets a tuple of channel-specific emotes for the specified broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the broadcaster whose channel emotes should be retrieved.

        Returns
        -------
        Tuple[ChannelEmote, ...]
            A tuple of ChannelEmote objects representing the channel's custom emotes

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_channel_emotes(self.id, broadcaster_id=user_id)
        return tuple(ChannelEmote.from_data(emote, data['template']) for emote in data['data'])

    async def get_global_emotes(self) -> Tuple[GlobalEmote, ...]:
        """
        Gets a tuple of global emotes available across all Twitch channels.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Returns
        -------
        Tuple[GlobalEmote, ...]
            A tuple of GlobalEmote objects representing Twitch's global emotes

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_global_emotes(self.id)
        return tuple(GlobalEmote.from_data(emote, data['template']) for emote in data['data'])

    async def get_emote_sets(self, emote_set_ids: Set[str]) -> Tuple[EmoteSet, ...]:
        """
        Gets emote sets by their IDs.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        emote_set_ids: Set[str]
            A set of emote set IDs to retrieve. Must contain at least one ID.
            Maximum of 25 IDs allowed.

        Returns
        -------
        Tuple[EmoteSet, ...]
            A tuple of EmoteSet objects representing the requested emote sets

        Raises
        ------
        ValueError
            If emote_set_ids length is not between 1 and 25.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any emote set ID is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        if not (1 <= len(emote_set_ids) <= 25):
            raise ValueError(f"emote_set_ids length must be between 1 and 25")

        data = await self._state.http.get_emote_sets(self.id, emote_set_ids=emote_set_ids)
        return tuple(EmoteSet.from_data(emote, data['template']) for emote in data['data'])

    async def get_channel_chat_badges(self, user_id: str) -> Tuple[ChatBadgeSet, ...]:
        """
        Gets a tuple of chat badge sets for the specified broadcaster's channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the broadcaster whose channel chat badges should be retrieved.

        Returns
        -------
        Tuple[ChatBadgeSet, ...]
            A tuple of ChatBadgeSet objects representing the channel's custom chat badges

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_channel_chat_badges(self.id, broadcaster_id=user_id)
        return tuple(ChatBadgeSet.from_data(badge) for badge in data['data'])

    async def get_global_chat_badges(self) -> Tuple[ChatBadgeSet, ...]:
        """
        Gets a tuple of global chat badge sets available across all Twitch channels.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Returns
        -------
        Tuple[ChatBadgeSet, ...]
            A tuple of ChatBadgeSet objects representing Twitch's global chat badges

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_global_chat_badges(self.id)
        return tuple(ChatBadgeSet.from_data(badge) for badge in data['data'])

    async def get_chat_settings(self, user_id: str) -> ChatSettings:
        """
        Gets the broadcaster's chat settings.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the broadcaster whose chat settings should be retrieved.

        Returns
        -------
        ChatSettings
            A ChatSettings object representing the broadcaster's chat settings

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_chat_settings(self.id, broadcaster_id=user_id)
        return ChatSettings.from_data(data['data'][0])

    async def get_shared_chat_session(self, user_id: str) -> Optional[SharedChatSession]:
        """
        Retrieves the active shared chat session for a channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The User ID of the channel broadcaster.

        Returns
        -------
        Optional[SharedChatSession]
            A SharedChatSession object representing the active shared chat session,
            or None if no session exists.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is invalid.
        Unauthorized
            If the token is invalid or expired.

        Note
        ----
        Channels can be streaming together but shared chat can be enabled or disabled.
        """
        data = await self._state.http.get_shared_chat_session(self.id, broadcaster_id=user_id)
        return SharedChatSession.from_data(data['data'][0]) if data['data'] else None

    async def get_user_chat_color(self, user_ids: Set[str]) -> Tuple[UserChatColor, ...]:
        """
        Gets the color used for the user's name in chat.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_ids: Set[str]
            The IDs of the users whose username colors you want to get.
            Maximum of 100 user IDs. IDs that weren't found are ignored.

        Returns
        -------
        Tuple[UserChatColor, ...]
            A tuple of UserChatColor objects containing user information and their chat colors.

        Raises
        ------
        ValueError
            If user_ids length is not between 1 and 100.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any user ID is not valid.
        Unauthorized
            If the token is invalid or expired.
        """
        if not (1 <= len(user_ids) <= 100):
            raise ValueError(f"user_ids length must be between 1 and 100")

        data = await self._state.http.get_user_chat_color(self.id, user_ids=user_ids)
        return tuple(UserChatColor.from_data(user_color) for user_color in data['data'] or [])

    async def get_channel_information(self, user_ids: Set[str]) -> Tuple[ChannelInfo, ...]:
        """
        Gets information about one or more channels.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_ids: Set[str]
            The IDs of the broadcasters whose channels you want to get.
            Maximum of 100 broadcaster IDs. Duplicate IDs and IDs that weren't found are ignored.

        Returns
        -------
        Tuple[ChannelInfo, ...]
            A tuple of ChannelInfo objects containing information about the specified channels.
            The tuple is empty if the specified channels weren't found.

        Raises
        ------
        ValueError
            If user_ids length is not between 1 and 100.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any broadcaster ID is not valid.
        Unauthorized
            If the Authorization header is required or the OAuth token is not valid,
            or the ID in the Client-Id header must match the Client ID in the OAuth token.
        """
        if not (1 <= len(user_ids) <= 100):
            raise ValueError(f"broadcaster_ids length must be between 1 and 100")

        data = await self._state.http.get_channel_information(self.id, broadcaster_ids=user_ids)
        return tuple(ChannelInfo.from_data(channel_info) for channel_info in data['data'] or [])

    async def get_channel_teams(self, user_id: str) -> Optional[Tuple[ChannelTeam, ...]]:
        """
        Gets the list of Twitch teams that the broadcaster is a member of.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the broadcaster whose teams you want to get.

        Returns
        -------
        Tuple[ChannelTeam, ...]
            A tuple of ChannelTeam objects containing the teams that the broadcaster
            is a member of.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id parameter is missing or invalid.
        Unauthorized
            If the Authorization header is required, the access token is not valid,
            or the ID in the Client-Id header does not match the client ID in the access token.
        NotFound
            If the broadcaster was not found.
        """
        data = await self._state.http.get_channel_teams(self.id, broadcaster_id=user_id)
        return tuple(ChannelTeam.from_data(team) for team in data['data']) if data['data'] else None

    async def get_team_by_id(self, team_id: str) -> Optional[TeamUsers]:
        """
        Gets information about the specified Twitch team by ID.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        team_id: str
            The ID of the team to get.

        Returns
        -------
        Optional[TeamUsers]
            A TeamUsers object containing the team information and list of team members.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        Unauthorized
            If the Authorization header is required, the access token is not valid,
            or the ID in the Client-Id header does not match the client ID in the access token.
        NotFound
            If the specified team was not found.
        """
        data = await self._state.http.get_teams(self.id, team_id=team_id, team_name=None)
        return TeamUsers.from_data(data['data'][0]) if data['data'] else None

    async def get_team_by_name(self, team_name: str) -> Optional[TeamUsers]:
        """
        Gets information about the specified Twitch team by name.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        team_name: str
            The name of the team to get.

        Returns
        -------
        Optional[TeamUsers]
            A TeamUsers object containing the team information and list of team members.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        Unauthorized
            If the Authorization header is required, the access token is not valid,
            or the ID in the Client-Id header does not match the client ID in the access token.
        NotFound
            If the specified team was not found.
        """
        data = await self._state.http.get_teams(self.id, team_id=None, team_name=team_name)
        return TeamUsers.from_data(data['data'][0]) if data['data'] else None

    @overload
    async def get_users(self, *, user_ids: Set[str]) -> Tuple[UserInfo, ...]:
        ...

    @overload
    async def get_users(self, *, user_logins: Set[str]) -> Tuple[UserInfo, ...]:
        ...

    @overload
    async def get_users(self, *, user_ids: Set[str], user_logins: Set[str]) -> Tuple[UserInfo, ...]:
        ...

    async def get_users(
            self,
            *,
            user_ids: Set[str] = frozenset(),
            user_logins: Set[str] = frozenset()
    ) -> Tuple[UserInfo, ...]:
        """
        Gets information about one or more users.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_ids: Set[str]
            The IDs of the users to get. Maximum of 100 user IDs total when combined
            with login_names.
        user_logins: Set[str]
            The login names of the users to get. Maximum of 100 login names total
            when combined with user_ids.

        Returns
        -------
        Tuple[UserInfo, ...]
            A tuple of User objects containing user information.

        Raises
        ------
        ValueError
            If no user_ids or user_logins are provided, or if the total number exceeds 100.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any user ID or login name is not valid.
        Unauthorized
            If the token is invalid or expired.
        """
        total_count = len(user_ids) + len(user_logins)
        if not (1 <= total_count <= 100):
            raise ValueError(f"Total number of user_ids and user_logins must be between 1 and 100, got {total_count}")

        data = await self._state.http.get_users(self.id, user_ids=user_ids, user_logins=user_logins)
        return tuple(UserInfo.from_data(user) for user in data['data'] or [])

    def get_top_games(self, limit: Optional[int] = 100) -> PaginatedRequest[..., Game]:
        """
        Gets information about all top games/categories on Twitch, sorted by viewer count.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        limit: Optional[int]
            The maximum total number of games to fetch.

        Returns
        -------
        PaginatedRequest[..., Game]
            A paginated collection of Game objects containing game information,
            sorted by viewer count with the most popular games first.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the limit parameter is not valid (outside 1-100 range when specified).
        Unauthorized
            If the Authorization header is required, the access token is not valid,
            or the ID in the Client-Id header does not match the client ID in the access token.
        """
        paginated_request = self._state.http.get_top_games(self.id, fetch_limit=limit)
        paginated_request._data_transform = lambda data: tuple(Game.from_data(item) for item in data['data'])
        return paginated_request

    @overload
    async def get_games(self, *, game_ids: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, game_names: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, igdb_ids: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, game_ids: Set[str], game_names: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, game_ids: Set[str], igdb_ids: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, game_names: Set[str], igdb_ids: Set[str]) -> Tuple[Game, ...]:
        ...

    @overload
    async def get_games(self, *, game_ids: Set[str], game_names: Set[str], igdb_ids: Set[str]) -> Tuple[Game, ...]:
        ...

    async def get_games(
            self,
            *,
            game_ids: Set[str] = frozenset(),
            game_names: Set[str] = frozenset(),
            igdb_ids: Set[str] = frozenset()
    ) -> Tuple[Game, ...]:
        """
        Gets information about specified categories or games.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        game_ids: Set[str]
            The IDs of the categories or games to get. You may specify a maximum
            of 100 IDs. The endpoint ignores duplicate and invalid IDs or IDs
            that weren't found.
        game_names: Set[str]
            The names of the categories or games to get. The name must exactly
            match the category's or game's title. You may specify a maximum of
            100 names. The endpoint ignores duplicate names and names that
            weren't found.
        igdb_ids: Set[str]
            The IGDB IDs of the games to get. You may specify a maximum of 100
            IDs. The endpoint ignores duplicate and invalid IDs or IDs that
            weren't found.

        Returns
        -------
        Tuple[Game, ...]
            A tuple of Game objects containing information about the specified
            categories and games.

        Raises
        ------
        ValueError
            If no parameters are provided or if the combined number of IDs and
            names exceeds 100.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any game ID, name, or IGDB ID is invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        if not (1 <= (len(game_ids) + len(game_names) + len(igdb_ids)) <= 100):
            raise ValueError("Total number of game_ids, game_names, and igdb_ids must be between 1 and 100")

        data = await self._state.http.get_games(
            self.id,
            game_names=game_names,
            game_ids=game_ids,
            igdb_ids=igdb_ids
        )
        return tuple(Game.from_data(game) for game in data['data'] or [])

    def search_categories(self, query: str, limit: Optional[int] = 100) -> PaginatedRequest[..., Category]:
        """
        Gets the games or categories that match the specified query.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        query: str
            The query to search for categories.
        limit: Optional[int]
            The maximum total number of categories to fetch.

        Returns
        -------
        PaginatedRequest[..., Category]
            A paginated collection of Category objects that match the query.

        Raises
        ------
        ValueError
            If the query is empty.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the query parameter is missing.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        if not query:
            raise ValueError("query cannot be empty")

        paginated_request = self._state.http.search_categories(self.id, query=query, fetch_limit=limit)
        paginated_request._data_transform = lambda data: tuple(Category.from_data(item) for item in data['data'])
        return paginated_request

    def search_channels(
            self,
            query: str,
            live_only: bool = False,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., SearchChannel]:
        """
        Gets the channels that match the specified query and have streamed content within the past 6 months.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        query: str
            The query to search for channels.
        live_only: bool
            A Boolean value that determines whether the response includes only channels
            that are currently streaming live.
        limit: Optional[int]
            The maximum total number of channels to fetch.

        Returns
        -------
        PaginatedRequest[..., SearchChannel]
            A paginated collection of SearchChannel objects that match the query.

        Raises
        ------
        ValueError
            If the query is empty.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the query parameter is missing.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        if not query:
            raise ValueError("query cannot be empty")

        paginated_request = self._state.http.search_channels(self.id, query=query, live_only=live_only, fetch_limit=limit)
        paginated_request._data_transform = lambda data: tuple(SearchChannel.from_data(item) for item in data['data'])
        return paginated_request

    def get_clips_by_id(
            self,
            clip_ids: Set[str],
            is_featured: Optional[bool] = None
    ) -> PaginatedRequest[..., Clip]:
        """
        Gets video clips by their IDs.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        clip_ids: Set[str]
            IDs that identify the clips to get. You may specify a maximum of 100 IDs.
            The API ignores duplicate IDs and IDs that aren't found.
        is_featured: Optional[bool]
            A Boolean value that determines whether the response includes featured clips.

        Returns
        -------
        PaginatedRequest[..., Clip]
            A paginated collection of Clip objects in the same order as the input IDs.

        Raises
        ------
        ValueError
            If ids contains fewer than 1 or more than 100 items.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any clip ID is invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        if not (1 <= len(clip_ids) <= 100):
            raise ValueError(f"ids must contain between 1 and 100 items")

        paginated_request = self._state.http.get_clips(
            self.id,
            clip_ids=clip_ids,
            is_featured=is_featured,
            fetch_limit=len(clip_ids),
            started_at=None,
            broadcaster_id=None,
            game_id=None,
            ended_at=None
        )
        paginated_request._data_transform = lambda data: tuple(Clip.from_data(item) for item in data['data'])
        return paginated_request

    def get_clips_by_user_id(
            self,
            user_id: str,
            started_at: Optional[datetime] = None,
            ended_at: Optional[datetime] = None,
            is_featured: Optional[bool] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Clip]:
        """
        Gets video clips that were captured from a broadcaster's streams.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            An ID that identifies the broadcaster whose video clips you want to get.
        started_at: Optional[datetime]
            The start date used to filter clips. The API returns only clips within
            the start and end date window. Naive datetime objects are treated as UTC.
        ended_at: Optional[datetime]
            The end date used to filter clips. If not specified, the time window
            is the start date plus one week. Naive datetime objects are treated as UTC.
        is_featured: Optional[bool]
            A Boolean value that determines whether the response includes featured clips.
            If True, returns only clips that are featured. If False, returns only clips
            that aren't featured. All clips are returned if this parameter is not present.
        limit: Optional[int]
            The maximum number of clips to fetch.

        Returns
        -------
        PaginatedRequest[..., Clip]
            A paginated collection of Clip objects in descending order by view count.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id or date parameters are invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        started_at_str = to_rfc3339_string(normalize_timezone(started_at)) if started_at else None
        ended_at_str = to_rfc3339_string(normalize_timezone(ended_at)) if ended_at else None

        paginated_request = self._state.http.get_clips(
            self.id,
            broadcaster_id=user_id,
            started_at=started_at_str,
            ended_at=ended_at_str,
            is_featured=is_featured,
            fetch_limit=limit,
            game_id=None,
            clip_ids=set()
        )
        paginated_request._data_transform = lambda data: tuple(Clip.from_data(item) for item in data['data'])
        return paginated_request

    def get_clips_by_category_id(
            self,
            category_id: str,
            started_at: Optional[datetime] = None,
            ended_at: Optional[datetime] = None,
            is_featured: Optional[bool] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Clip]:
        """
        Gets video clips that were captured from streams playing a specific game.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        category_id: str
            An ID that identifies the game/category whose clips you want to get.
        started_at: Optional[datetime]
            The start date used to filter clips. The API returns only clips within
            the start and end date window. Naive datetime objects are treated as UTC.
        ended_at: Optional[datetime]
            The end date used to filter clips. If not specified, the time window
            is the start date plus one week. Naive datetime objects are treated as UTC.
        is_featured: Optional[bool]
            A Boolean value that determines whether the response includes featured clips.
            If True, returns only clips that are featured. If False, returns only clips
            that aren't featured. All clips are returned if this parameter is not present.
        limit: Optional[int]
            The maximum number of clips to fetch.

        Returns
        -------
        PaginatedRequest[..., Clip]
            A paginated collection of Clip objects in descending order by view count.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the category_id or date parameters are invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        NotFound
            If the category_id was not found.
        """
        started_at_str = to_rfc3339_string(normalize_timezone(started_at)) if started_at else None
        ended_at_str = to_rfc3339_string(normalize_timezone(ended_at)) if ended_at else None

        paginated_request = self._state.http.get_clips(
            self.id,
            game_id=category_id,
            started_at=started_at_str,
            ended_at=ended_at_str,
            is_featured=is_featured,
            fetch_limit=limit,
            clip_ids=set(),
            broadcaster_id=None
        )
        paginated_request._data_transform = lambda data: tuple(Clip.from_data(item) for item in data['data'])
        return paginated_request

    def get_videos_by_id(self, video_ids: Set[str]) -> PaginatedRequest[..., Video]:
        """
        Gets information about one or more published videos by their IDs.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        video_ids: Set[str]
            IDs that identify the videos to get. You may specify a maximum of 100 IDs.

        Returns
        -------
        PaginatedRequest[..., Video]
            A paginated collection of Video objects.

        Raises
        ------
        ValueError
            If video_ids contains fewer than 1 or more than 100 items.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any video ID is invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        if not (1 <= len(video_ids) <= 100):
            raise ValueError(f"video_ids must contain between 1 and 100 items")

        paginated_request = self._state.http.get_videos(
            self.id,
            video_ids=video_ids,
            fetch_limit=len(video_ids),
            game_id=None,
            video_type=None,
            sort=None,
            period=None,
            video_user_id=None,
            language=None
        )
        paginated_request._data_transform = lambda data: tuple(Video.from_data(item) for item in data['data'])
        return paginated_request

    def get_videos_by_user_id(
            self,
            user_id: str,
            language: Optional[str] = None,
            period: Literal['all', 'day', 'month', 'week'] = 'all',
            sort: Literal['time', 'trending', 'views'] = 'time',
            video_type: Literal['all', 'archive', 'highlight', 'upload'] = 'all',
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Video]:
        """
        Gets published videos from a specific user.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the user whose list of videos you want to get.
        language: Optional[str]
            A filter used to filter the list of videos by the language that the video
            owner broadcasts in. Use ISO 639-1 two-letter code (e.g., 'en' for English).
            Use 'other' if the language is not supported.
        period: Literal['all', 'day', 'month', 'week']
            A filter used to filter videos by when they were published.
        sort: Literal['time', 'trending', 'views']
            The order to sort the returned videos.
        video_type: Literal['all', 'archive', 'highlight', 'upload']
            A filter used to filter videos by type.
        limit: Optional[int]
           The maximum number of videos to fetch.

        Returns
        -------
        PaginatedRequest[..., Video]
            A paginated collection of Video objects.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id or other filter parameters are invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        """
        paginated_request = self._state.http.get_videos(
            self.id,
            video_user_id=user_id,
            language=language,
            period=period,
            sort=sort,
            video_type=video_type,
            fetch_limit=limit,
            game_id=None,
            video_ids=set()
        )
        paginated_request._data_transform = lambda data: tuple(Video.from_data(item) for item in data['data'])
        return paginated_request

    def get_videos_by_category_id(
            self,
            category_id: str,
            language: Optional[str] = None,
            period: Literal['all', 'day', 'month', 'week'] = 'all',
            sort: Literal['time', 'trending', 'views'] = 'time',
            video_type: Literal['all', 'archive', 'highlight', 'upload'] = 'all',
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Video]:
        """
        Gets published videos from a specific game/category.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        category_id: str
            A category or game ID. The response contains a maximum of 500 videos
            that show this content.
        language: Optional[str]
            A filter used to filter the list of videos by the language that the video
            owner broadcasts in. Use ISO 639-1 two-letter code (e.g., 'en' for English).
            Use 'other' if the language is not supported.
        period: Literal['all', 'day', 'month', 'week']
            A filter used to filter videos by when they were published.
        sort: Literal['time', 'trending', 'views']
            The order to sort the returned videos.
        video_type: Literal['all', 'archive', 'highlight', 'upload']
            A filter used to filter videos by type.
        limit: Optional[int]
            The maximum number of videos to fetch. Max 500

        Returns
        -------
        PaginatedRequest[..., Video]
            A paginated collection of Video objects.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the category_id or other filter parameters are invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        NotFound
            If the category_id was not found.
        """
        paginated_request = self._state.http.get_videos(
            self.id,
            game_id=category_id,
            language=language,
            period=period,
            sort=sort,
            video_type=video_type,
            fetch_limit=min(limit or 500, 500) if limit else 500,
            video_ids=set(),
            video_user_id=None
        )
        paginated_request._data_transform = lambda data: tuple(Video.from_data(item) for item in data['data'])
        return paginated_request

    @overload
    def get_streams(
            self,
            *,
            user_ids: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            user_logins: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            game_ids: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            user_ids: Set[str],
            user_logins: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            user_ids: Set[str],
            game_ids: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            user_logins: Set[str],
            game_ids: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    @overload
    def get_streams(
            self,
            *,
            user_ids: Set[str],
            user_logins: Set[str],
            game_ids: Set[str],
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        ...

    def get_streams(
            self,
            *,
            user_ids: Set[str] = frozenset(),
            user_logins: Set[str] = frozenset(),
            game_ids: Set[str] = frozenset(),
            stream_type: Literal['all', 'live'] = 'all',
            languages: Set[str] = frozenset()
    ) -> PaginatedRequest[..., StreamInfo]:
        """
        Gets all live streams.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_ids: Set[str]
            User IDs used to filter the list of streams.
            Maximum of 100 IDs.
        user_logins: Set[str]
            User login names used to filter the list of streams.
            Maximum of 100 login names.
        game_ids: Set[str]
            Game (category) IDs used to filter the list of streams.
            Maximum of 100 IDs.
        stream_type: Literal['all', 'live']
            The type of stream to filter the list of streams by. Possible values are: 'all', 'live'.
            Default is 'all'.
        languages: Set[str]
            Language codes used to filter the list of streams.
            Use ISO 639-1 two-letter code (e.g., 'en' for English). Use 'other' if the language is not supported.
            Maximum of 100 language codes.

        Returns
        -------
        PaginatedRequest[..., StreamInfo]
            A paginated collection of Stream objects.

        Raises
        ------
        ValueError
            If any parameter set exceeds 100 items, or if no filter parameters are provided.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If any user ID, login name, game ID, or language code is not valid, or if the type parameter is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        for param_name, param_set in [
            ('user_ids', user_ids),
            ('user_logins', user_logins),
            ('game_ids', game_ids),
            ('languages', languages)
        ]:
            if len(param_set) > 100:
                raise ValueError(f"{param_name} must not exceed 100 items")

        if len(user_ids) + len(user_logins) + len(game_ids) == 0:
            raise ValueError("At least one of user_ids, user_logins, or game_ids must be provided")

        paginated_request = self._state.http.get_streams(
            self.id,
            user_ids=user_ids,
            user_logins=user_logins,
            game_ids=game_ids,
            stream_type=stream_type,
            languages=languages,
            fetch_limit=None
        )
        paginated_request._data_transform = lambda data: tuple(StreamInfo.from_data(item) for item in data['data'])
        return paginated_request

    async def get_content_classification_labels(
            self,
            locale: Literal['bg-BG', 'cs-CZ', 'da-DK', 'de-DE', 'el-GR', 'en-GB', 'en-US',
            'es-ES', 'es-MX', 'fi-FI', 'fr-FR', 'hu-HU', 'it-IT', 'ja-JP',
            'ko-KR', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU',
            'sk-SK', 'sv-SE', 'th-TH', 'tr-TR', 'vi-VN', 'zh-CN', 'zh-TW'] = 'en-US'
    ) -> Tuple[ContentClassificationLabel, ...]:
        """
        Gets information about Twitch content classification labels.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        locale: str
            Locale for the Content Classification Labels.
            Possible values:
            'bg-BG', 'cs-CZ', 'da-DK', 'de-DE', 'el-GR', 'en-GB',
            'en-US', 'es-ES', 'es-MX', 'fi-FI', 'fr-FR', 'hu-HU', 'it-IT', 'ja-JP',
            'ko-KR', 'nl-NL', 'no-NO', 'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU',
            'sk-SK', 'sv-SE', 'th-TH', 'tr-TR', 'vi-VN', 'zh-CN', 'zh-TW'

        Returns
        -------
        Tuple[ContentClassificationLabel, ...]
            A tuple of ContentClassificationLabel objects containing information about
            the available content classification labels.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the locale is invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_content_classification_labels(self.id, locale=locale)
        return tuple(ContentClassificationLabel.from_data(label) for label in data['data'])

    def get_channel_stream_schedule(
            self,
            user_id: str,
            segment_ids: Set[str] = frozenset(),
            start_time: Optional[datetime] = None,
            limit: Optional[int] = 25
    ) -> PaginatedRequest[..., ChannelStreamSchedule]:
        """
        Gets the broadcaster's streaming schedule.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        user_id: str
            The ID of the broadcaster that owns the streaming schedule you want to get.
        segment_ids: Set[str]
            The IDs of the scheduled segments to return. Maximum of 100 IDs.
        start_time: Optional[datetime.datetime]
            The UTC date and time that identifies when in the broadcaster's schedule to start returning segments.
            If not specified, returns segments starting after the current UTC date and time.
            Naive datetime objects are treated as UTC.
        limit: Optional[int]
            The maximum number of segments to fetch.

        Returns
        -------
        PaginatedRequest[..., ChannelStreamSchedule]
            A paginated collection containing the broadcaster's streaming schedule.

        Raises
        ------
        ValueError
            If segment_ids contains more than 100 IDs.
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If the user_id or other parameters are invalid.
        Unauthorized
            If the Authorization header is missing, the access token is invalid,
            or the Client-Id header doesn't match the client ID in the token.
        NotFound
            If the broadcaster has not created a streaming schedule.
        """
        if len(segment_ids) > 100:
            raise ValueError("segment_ids must not exceed 100 items")

        start_time_str = to_rfc3339_string(normalize_timezone(start_time)) if start_time else None

        paginated_request = self._state.http.get_channel_stream_schedule(
            self.id,
            broadcaster_id=user_id,
            segment_ids=segment_ids,
            start_time=start_time_str,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: ChannelStreamSchedule.from_data(data)
        return paginated_request

    async def update_drops_entitlements(
            self,
            fulfillment_status: Literal["CLAIMED", "FULFILLED"],
            entitlement_ids: Set[str]
    ) -> Tuple[DropsEntitlementUpdate, ...]:
        """
        Updates the Drop entitlement's fulfillment status.

        The following table identifies which entitlements are updated based on the type of access token used:

        - App: Updates all entitlements with benefits owned by the organization in the access token.

        - User: Updates all entitlements owned by the user in the access token and where the benefits
          are owned by the organization in the access token.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements      |
        |-------------|-----------------|---------------------------------|
        | App Access  | None            | Client ID owned by organization |
        | User Access | drops:edit      | User member of organization     |

        Parameters
        ----------
        fulfillment_status: Literal["CLAIMED", "FULFILLED"]
            The fulfillment status to set the entitlements to. Possible values are:
        entitlement_ids:Set[str]
            A set of IDs that identify the entitlements to update.

        Returns
        -------
        Tuple[DropsEntitlementUpdate, ...]
            A tuple of DropsEntitlementUpdate objects indicating which entitlements were successfully
            updated and those that weren't.

        Raises
        ------
        ValueError
            If entitlement_ids length exceeds 100.
        TokenError
            If missing a valid app access token or user access token.
            If the Client ID associated with the access token is not owned by a user who is a member
            of the organization that holds ownership of the game.
        BadRequest
            If the value in the fulfillment_status field is not valid.
            If the client in the access token is not associated with a known organization.
            If the owner of the client in the access token is not a member of the organization.
        Unauthorized
            If the access token is not valid.
            If the ID in the Client-Id header must match the Client ID in the access token.
        """
        if not (1 <= len(entitlement_ids) <= 100):
            raise ValueError(f"entitlement_ids length must be between 1 and 100")

        data = await self._state.http.update_drops_entitlements(
            self.id,
            entitlement_ids=entitlement_ids,
            fulfillment_status=fulfillment_status
        )
        return tuple(DropsEntitlementUpdate.from_data(update_data) for update_data in data['data'] or [])

    async def create_eventsub_subscription(
            self,
            subscription_type: str,
            subscription_version: str,
            transport: Dict[str, Any],
            condition: Dict[str, Any]
    ) -> Tuple[Subscription, Tuple[int, int, int]]:
        """
        Creates an EventSub subscription to receive notifications when events occur.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | Varies by type  | For webhook/conduit        |
        | User Access | Varies by type  | For websocket              |

        Parameters
        ----------
        subscription_type: str
            The type of subscription to create. For a list of subscription types,
            see Subscription Types in the Twitch API documentation.
        subscription_version: str
            The version number that identifies the definition of the subscription's data.
        transport: Dict[str, Any]
            The transport details used to send the notifications.
            Must contain 'method' (either 'webhook' or 'websocket') and additional fields based on the method:
            - For webhook: 'callback' (URL) and optionally 'secret'
            - For websocket: 'session_id'
        condition: Dict[str, Any]
            The subscription's parameter values. Contents are determined by the subscription type.

        Returns
        -------
        Tuple[Subscription, Tuple[int, int, int]]
            A tuple containing:
            - The created Subscription object
            - A tuple of (total_subscriptions, total_cost, max_total_cost)

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid or the subscription type/version is not supported.
        Unauthorized
            If the token is invalid or expired.
        Conflict
            If a subscription with the same type and condition already exists.
        Forbidden
            If the scope is insufficient for the subscription type.
        """
        data = await self._state.http.create_eventsub_subscription(
            self.id,
            subscription_type=subscription_type,
            subscription_version=subscription_version,
            subscription_condition=condition,
            transport=transport,
        )
        return Subscription.from_data(data['data'][0]), (data['total'], data['total_cost'], data['max_total_cost'])

    def get_eventsub_subscriptions(self, limit: Optional[int] = 100) -> PaginatedRequest[..., Subscription]:
        """
        Gets a list of all EventSub subscriptions that the client in the access token created.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        limit: Optional[int]
            The maximum total number of EventSub subscriptions to fetch.

        Returns
        -------
        PaginatedRequest[..., Subscription]
            A paginated collection of Subscription objects.

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            fetch_limit=limit,
            subscription_id=None,
            subscriptions_type=None,
            subscription_user_id=None,
            status=None,
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        return paginated_request

    def get_eventsub_subscriptions_by_status(
            self,
            status: Literal[
                'enabled',
                'webhook_callback_verification_pending',
                'webhook_callback_verification_failed',
                'notification_failures_exceeded',
                'authorization_revoked',
                'moderator_removed',
                'user_removed',
                'chat_user_banned',
                'version_removed',
                'beta_maintenance',
                'websocket_disconnected',
                'websocket_failed_ping_pong',
                'websocket_received_inbound_traffic',
                'websocket_state_unused',
                'websocket_internal_error',
                'websocket_network_timeout',
                'websocket_network_error',
                'websocket_failed_to_reconnect'
            ],
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Subscription]:
        """
        Gets a list of EventSub subscriptions filtered by status.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        status: str
            Filter subscriptions by its status. Possible values are:
            'enabled', 'webhook_callback_verification_pending', 'webhook_callback_verification_failed',
            'notification_failures_exceeded', 'authorization_revoked', 'moderator_removed', 'user_removed',
            'chat_user_banned', 'version_removed', 'beta_maintenance', 'websocket_disconnected',
            'websocket_failed_ping_pong', 'websocket_received_inbound_traffic', 'websocket_state_unused',
            'websocket_internal_error', 'websocket_network_timeout', 'websocket_network_error',
            'websocket_failed_to_reconnect'
        limit: Optional[int]
            The maximum total number of EventSub subscriptions to fetch.

        Returns
        -------
        PaginatedRequest[..., Subscription]
            A paginated collection of Subscription objects.

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            status=status,
            fetch_limit=limit,
            subscription_id=None,
            subscriptions_type=None,
            subscription_user_id=None
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        return paginated_request

    def get_eventsub_subscriptions_by_type(
            self,
            subscriptions_type: str,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Subscription]:
        """
        Gets a list of EventSub subscriptions filtered by subscription type.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        subscriptions_type: str
            Filter subscriptions by subscription type. For a list of subscription types, see Subscription Types.
        limit: Optional[int]
            The maximum total number of EventSub subscriptions to fetch.

        Returns
        -------
        PaginatedRequest[..., Subscription]
            A paginated collection of Subscription objects.

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            subscriptions_type=subscriptions_type,
            fetch_limit=limit,
            subscription_id=None,
            subscription_user_id=None,
            status=None
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        return paginated_request

    def get_eventsub_subscriptions_by_user_id(
            self,
            user_id: str,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Subscription]:
        """
        Gets a list of EventSub subscriptions filtered by user ID.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        user_id: str
            Filter subscriptions by user ID. The response contains subscriptions where this ID matches
            a user ID that you specified in the Condition object when you created the subscription.
        limit: Optional[int]
            The maximum total number of EventSub subscriptions to fetch.

        Returns
        -------
        PaginatedRequest[..., Subscription]
            A paginated collection of Subscription objects.

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            subscription_user_id=user_id,
            fetch_limit=limit,
            subscription_id=None,
            status=None,
            subscriptions_type=None
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        return paginated_request

    async def get_eventsub_subscription_by_id(self, subscription_id: str) -> Optional[Subscription]:
        """
        Gets a specific EventSub subscription by its ID.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        subscription_id: str
            Returns an array with the subscription matching the ID (as long as it is owned by the client
            making the request), or an empty array if there is no matching subscription.

        Returns
        -------
        Optional[Subscription]
            The EventSub subscription if found, None if not found or not owned by the client.

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the subscription was not found.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            subscription_id=subscription_id,
            fetch_limit=1,
            subscriptions_type=None,
            subscription_user_id=None,
            status=None
        )
        paginated_request._data_transform = lambda data: tuple(Subscription.from_data(item) for item in data['data'])
        subscriptions = await paginated_request.next()
        return subscriptions[0] if subscriptions else None

    async def get_eventsub_subscriptions_summary(self) -> Tuple[int, int, int]:
        """
        Gets summary information about your EventSub subscriptions including totals and costs.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Returns
        -------
        Tuple[int, int, int]
            A tuple containing (total, total_cost, max_total_cost):
            - total: The total number of subscriptions that you've created
            - total_cost: The sum of all of your subscription costs
            - max_total_cost: The maximum total cost that you're allowed to incur for all subscriptions

        Raises
        ------
        TokenError
            If using webhooks/conduits without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the request parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_eventsub_subscriptions(
            self.id,
            subscription_id=None,
            fetch_limit=1,
            subscriptions_type=None,
            subscription_user_id=None,
            status=None
        )
        data = await paginated_request.next()
        return data[0]['total'], data[0]['total_cost'], data[0]['max_total_cost']

    async def delete_eventsub_subscription(self, subscription_id: str) -> None:
        """
        Deletes an EventSub subscription.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | For webhook/conduit        |
        | User Access | None            | For websocket              |

        Parameters
        ----------
        subscription_id: str
            The ID of the subscription to delete.

        Raises
        ------
        TokenError
            If using webhooks without an app access token, or if using WebSockets without a user access token.
        BadRequest
            If the subscription_id parameter is missing or invalid.
        Unauthorized
            If the Authorization header is missing, the access token is not valid,
            or the Client-Id header doesn't match the client ID in the access token.
        NotFound
            If the subscription was not found.
        """
        await self._state.http.delete_eventsub_subscription(self.id, subscription_id=subscription_id)

    def get_extension_live_channels(self, extension_id: str, limit: Optional[int] = 100) -> PaginatedRequest[..., ExtensionLiveChannel]:
        """
        Gets a list of broadcasters that are streaming live and have installed or activated the specified extension.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        extension_id: str
            The ID of the extension whose installed or activated channels you want to get.
        limit: Optional[int]
            The maximum number of items to return.

        Returns
        -------
        PaginatedRequest[..., ExtensionLiveChannel]
            A paginated collection of ExtensionLiveChannel objects.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If extension_id is missing or invalid.
        Unauthorized
            If the token is invalid or expired.
        """
        paginated_request = self._state.http.get_extension_live_channels(
            self.id,
            extension_id=extension_id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(ExtensionLiveChannel.from_data(item) for item in data['data'])
        return paginated_request

    async def get_extension_channel_configuration(self, broadcaster_id: str, extension_id: str) -> ExtensionConfiguration:
        """
        Gets the configuration of the extension on the specified channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |
        | User Access | None            | None                       |

        Parameters
        ----------
        broadcaster_id: str
            The ID of the broadcaster (channel) whose extension configuration you want to get.
        extension_id: str
            The ID of the extension whose configuration you want to get.

        Returns
        -------
        ExtensionConfiguration
            The extension configuration on the channel.

        Raises
        ------
        TokenError
            If missing a valid app access token or user access token.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the configuration was not found.
        """
        data = await self._state.http.get_extension_channel_configuration(
            self.id,
            broadcaster_id=broadcaster_id,
            extension_id=extension_id
        )
        return ExtensionConfiguration.from_data(data['data'][0])


class AppAPI(BaseAPI):
    def __init__(self, app_user_id: str, *, state: ConnectionState) -> None:
        super().__init__(app_user_id, state=state)

    async def send_chat_message(
            self,
            broadcaster_id: str,
            sender_id: str,
            message: str,
            reply_message_id: Optional[str] = None,
            for_source_only: Optional[bool] = None
    ) -> SendMessageStatus:
        """
        Sends a message to the broadcaster's chat room using an app access token.

        ???+ tip

            This method is safer than sending messages directly as it only works in
            channels that have explicitly authorized your app.

        Token and Authorization Requirements::

        | Token Type | Required Scopes         | Authorization Requirements                       |
        |------------|-------------------------|--------------------------------------------------|
        | App Access | user:write:chat         | Token holder can send to chat                    |
        |            | user:bot                | Required from chatting user                      |
        |            | channel:bot             | Required from broadcaster or moderator status    |

        Parameters
        ----------
        broadcaster_id: str
            The ID of the broadcaster whose chat room the message will be sent to.
        sender_id: str
            The ID of the user sending the message. This ID must match the user ID
            in the user access token.
        message: str
            The message to send. Max 500 characters. Can include emoticons using
            their case-sensitive names without colons (e.g., bleedPurple).
        reply_message_id: Optional[str]
            The ID of the message to reply to.
        for_source_only: Optional[bool]
            Whether the message is sent only to the source channel. Note: This parameter
            can only be set when using an App Access Token. Default behavior changes
            to True on May 19, 2025.

        Returns
        -------
        SendMessageStatus
            The status of the sent-message.

        Raises
        ------
        ValueError
            If message length > 500.
        TokenError
            If missing app token with required scopes.
        BadRequest
            If invalid parameters or message content.
        Unauthorized
            If the token is invalid or expired.
        Forbidden
            If not permitted to send messages to this chat room.
        """
        if len(message) > 500:
            raise ValueError("message must be <= 500 characters")

        data = await self._state.http.send_chat_message(
            self.id,
            broadcaster_id=broadcaster_id,
            sender_id=sender_id,
            message=message,
            reply_parent_message_id=reply_message_id,
            for_source_only=for_source_only
        )
        return SendMessageStatus.from_data(data['data'][0])

    def get_drops_entitlements(
            self,
            entitlement_ids: Set[str] = frozenset(),
            user_id: Optional[str] = None,
            game_id: Optional[str] = None,
            fulfillment_status: Optional[Literal['CLAIMED', 'FULFILLED']] = None,
            limit: Optional[int] = 1000
    ) -> PaginatedRequest[..., DropsEntitlement]:
        """
        Gets an organization's list of entitlements that have been granted to a game, a user, or both.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements   |
        |-------------|-----------------|------------------------------|
        | App Access  | None            | Client owned by organization |

        Note
        ----
        Entitlements are returned unsorted. Use fulfillment_status and game_id to filter results.
        To retrieve entitlements for a specific game, use the game_id parameter to filter results.

        Parameters
        ----------
        entitlement_ids: Set[str]
            IDs that identify the entitlements to get.
            Maximum of 100 IDs.
        user_id: Optional[str]
            An ID that identifies a user that was granted entitlements.
        game_id: Optional[str]
            An ID that identifies a game that offered entitlements.
        fulfillment_status: Optional[Literal['CLAIMED', 'FULFILLED']]
            The entitlement's fulfillment status. Used to filter the list to only those with the specified status.
            Possible values are: 'CLAIMED', 'FULFILLED'.
        limit: Optional[int]
            The maximum total number of drops entitlements to fetch.

        Returns
        -------
        PaginatedRequest[..., DropsEntitlement]
            A paginated collection of DropsEntitlement objects.

        Raises
        ------
        ValueError
            If ids length exceeds 100.
        TokenError
            If missing a valid app access token.
        BadRequest
            If the fulfillment_status value is not valid, or client is not associated with a known organization,
            or owner of client is not a member of organization.
        Unauthorized
            If Client-Id header doesn't match the Client ID in the access token, or Authorization header is missing,
            or access token is not valid.
        Forbidden
            If organization doesn't own the game specified in game_id, or organization doesn't own the entitlements
            specified in ids.
        """
        if len(entitlement_ids) > 100:
            raise ValueError("entitlement_ids must not exceed 100 items")

        paginated_request = self._state.http.get_drops_entitlements(
            self.id,
            entitlement_ids=entitlement_ids,
            target_user_id=user_id,
            game_id=game_id,
            fulfillment_status=fulfillment_status,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            DropsEntitlement.from_data(item) for item in data['data']
        )
        return paginated_request

    async def get_conduits(self) -> Tuple[Conduit, ...]:
        """
        Gets information about the conduits for EventSub.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Returns
        -------
        Tuple[Conduit, ...]
            A tuple of Conduit objects.

        Raises
        ------
        TokenError
            If missing a valid app access token.
        Unauthorized
            If the token is invalid or expired.
        """
        data = await self._state.http.get_conduits(self.id)
        return tuple(Conduit.from_data(conduit) for conduit in data['data'])

    async def create_conduit(self, shard_count: int) -> Conduit:
        """
        Creates a conduit for EventSub.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        shard_count: int
            The number of shards to create. Max 20000.

        Returns
        -------
        Conduit
            The created Conduit.

        Raises
        ------
        ValueError
            If shard_count > 20000.
        TokenError
            If missing a valid app access token.
        BadRequest
            If shard_count is invalid.
        Unauthorized
            If the token is invalid or expired.
        RateLimited
            reached the maximum conduits allowed.
        """
        if shard_count > 20000:
            raise ValueError("shard_count must be <= 20000")
        data = await self._state.http.create_conduit(self.id, shard_count=shard_count)
        return Conduit.from_data(data['data'][0])

    async def update_conduit(self, conduit_id: str, shard_count: int) -> Conduit:
        """
        Updates a conduit's shard count.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        conduit_id: str
            The ID of the conduit to update.
        shard_count: int
            The new number of shards. Max 20000.

        Returns
        -------
        Conduit
            The updated Conduit.

        Raises
        ------
        ValueError
            If shard_count > 20000.
        TokenError
            If missing a valid app access token.
        BadRequest
            If conduit_id or shard_count is invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the conduit was not found.
        """
        if shard_count > 20000:
            raise ValueError("shard_count must be <= 20000")
        data = await self._state.http.update_conduit(self.id, conduit_id=conduit_id, shard_count=shard_count)
        return Conduit.from_data(data['data'][0])

    async def delete_conduit(self, conduit_id: str) -> None:
        """
        Deletes a conduit.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        conduit_id: str
            The ID of the conduit to delete.

        Raises
        ------
        TokenError
            If missing a valid app access token.
        BadRequest
            If conduit_id is invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the conduit was not found.
        """
        await self._state.http.delete_conduit(self.id, conduit_id=conduit_id)

    def get_conduit_shards(
            self,
            conduit_id: str,
            status: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., ConduitShard]:
        """
        Gets the shards for a conduit.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        conduit_id: str
            The ID of the conduit.
        status: Optional[str]
            Filter by shard status.
        limit: Optional[int]
            The maximum number of shards to return.

        Returns
        -------
        PaginatedRequest[..., ConduitShard]
            A paginated collection of ConduitShard objects.

        Raises
        ------
        TokenError
            If missing a valid app access token.
        BadRequest
            If conduit_id or status is invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the conduit was not found.
        """
        paginated_request = self._state.http.get_conduit_shards(
            self.id,
            conduit_id=conduit_id,
            status=status,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(ConduitShard.from_data(item) for item in data['data'])
        return paginated_request

    async def update_conduit_shards(self, conduit_id: str, shards: Tuple[Dict[str, Any]]) -> ConduitShardUpdate:
        """
        Updates the shards for a conduit.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | App Access  | None            | None                       |

        Parameters
        ----------
        conduit_id: str
            The ID of the conduit.
        shards: Tuple[Dict[str, Any]]
            The list of shard updates.

        Returns
        -------
        ConduitShardUpdate
            The update status.

        Raises
        ------
        TokenError
            If missing a valid app access token.
        BadRequest
            If conduit_id or shards are invalid.
        Unauthorized
            If the token is invalid or expired.
        NotFound
            If the conduit was not found.
        """
        data = await self._state.http.update_conduit_shards(
            self.id,
            conduit_id=conduit_id,
            shards=shards
        )
        return ConduitShardUpdate.from_data(data)

    def get_extension_transactions(
            self,
            extension_id: str,
            transaction_ids: Set[str] = frozenset(),
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., ExtensionTransaction]:
        """
        Gets transactions for the specified extension.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements            |
        |-------------|-----------------|---------------------------------------|
        | App Access  | None            | Client ID matches extension client ID |

        Parameters
        ----------
        extension_id: str
            The ID of the extension.
        transaction_ids: Set[str]
            Transaction IDs to look up. Max 100.
        limit: Optional[int]
            The maximum number of items to return.

        Returns
        -------
        PaginatedRequest[..., ExtensionTransaction]
            A paginated collection of ExtensionTransaction objects.

        Raises
        ------
        ValueError
            If transaction_ids > 100.
        TokenError
            If missing token.
        BadRequest
            If extension_id or transaction_ids are invalid.
        Unauthorized
            If token invalid or client ID mismatch.
        """
        if len(transaction_ids) > 100:
            raise ValueError("transaction_ids must not exceed 100 items")

        paginated_request = self._state.http.get_extension_transactions(
            self.id,
            extension_id=extension_id,
            transaction_ids=transaction_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            ExtensionTransaction.from_data(item) for item in data['data'])
        return paginated_request

    async def get_extension_bits_products(
            self,
            extension_id: str,
            should_include_all: bool = False
    ) -> Tuple[ExtensionBitsProduct, ...]:
        """
        Gets the Bits products for the specified extension.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements            |
        |-------------|-----------------|---------------------------------------|
        | App Access  | None            | Client ID matches extension client ID |

        Parameters
        ----------
        extension_id: str
            The ID of the extension.
        should_include_all: bool
            Whether to include expired products.

        Returns
        -------
        Tuple[ExtensionBitsProduct, ...]
            A tuple of ExtensionBitsProduct objects.

        Raises
        ------
        TokenError
            If missing token.
        BadRequest
            The ID in the Client-Id header must belong to an extension.
        Unauthorized
            If token invalid or client ID mismatch.
        """
        data = await self._state.http.get_extension_bits_products(
            self.id,
            extension_id=extension_id,
            should_include_all=should_include_all
        )
        return tuple(ExtensionBitsProduct.from_data(item) for item in data['data'])

    async def update_extension_bits_product(
            self,
            extension_id: str,
            sku: str,
            cost: Dict[str, Any],
            name: str,
            in_development: bool = False,
            display_name: Optional[str] = None,
            expiration: Optional[str] = None,
            is_broadcast: bool = False
    ) -> ExtensionBitsProduct:
        """
        Updates or creates a Bits product for the extension.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements            |
        |-------------|-----------------|---------------------------------------|
        | App Access  | None            | Client ID matches extension client ID |

        Parameters
        ----------
        extension_id: str
            The ID of the extension.
        sku: str
            The SKU of the product.
        cost: Dict[str, Any]
            The cost of the product.
        name: str
            The name of the product.
        in_development: bool
            Whether the product is in development.
        display_name: Optional[str]
            The display name.
        expiration: Optional[str]
            The expiration date.
        is_broadcast: bool
            Whether the product is broadcast.

        Returns
        -------
        ExtensionBitsProduct
            The updated or created product.

        Raises
        ------
        TokenError
            If missing token.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid or client ID mismatch.
        """
        data = await self._state.http.update_extension_bits_product(
            self.id,
            extension_id=extension_id,
            sku=sku,
            cost=cost,
            name=name,
            in_development=in_development,
            display_name=display_name,
            expiration=expiration,
            is_broadcast=is_broadcast
        )
        return ExtensionBitsProduct.from_data(data['data'][0])


class UserAPI(BaseAPI):

    if TYPE_CHECKING:
        _state: ClientUserConnectionState

    __slots__ = ('__weakref__',)

    def __init__(self, user_id: str, *, state: ClientUserConnectionState) -> None:
        super().__init__(user_id, state=state)
        self.id: str = user_id

    async def delete_eventsub_subscription(self, subscription_id: str) -> None:
        await super().delete_eventsub_subscription(subscription_id)
        await self._state.remove_subscription(subscription_id=subscription_id, cost=None)

    @override
    async def get_channel_emotes(self, user_id: Optional[str] = None) -> Tuple[ChannelEmote, ...]:
        return await super().get_channel_emotes(user_id or self.id)

    @override
    async def get_channel_chat_badges(self, user_id: Optional[str] = None) -> Tuple[ChatBadgeSet, ...]:
        return await super().get_channel_chat_badges(user_id or self.id)

    @override
    async def get_chat_settings(self, user_id: Optional[str] = None) -> ChatSettings:
        return await super().get_chat_settings(user_id or self.id)

    @override
    async def get_shared_chat_session(self, user_id: Optional[str] = None) -> Optional[SharedChatSession]:
        return await super().get_shared_chat_session(user_id or self.id)

    @override
    async def get_user_chat_color(self, user_ids: Optional[Set[str]] = None) -> Tuple[UserChatColor, ...]:
        return await super().get_user_chat_color(user_ids or {self.id})

    @override
    async def get_channel_information(self, user_ids: Optional[Set[str]] = None) -> Tuple[ChannelInfo, ...]:
        return await super().get_channel_information(user_ids or {self.id})

    @override
    async def get_channel_teams(self, user_id: Optional[str] = None) -> Optional[Tuple[ChannelTeam, ...]]:
        return await super().get_channel_teams(user_id or self.id)

    def get_channel_stream_schedule(
            self,
            user_id: Optional[str] = None,
            segment_ids: Set[str] = frozenset(),
            start_time: Optional[datetime] = None,
            limit: Optional[int] = 25
    ) -> PaginatedRequest[..., ChannelStreamSchedule]:
        return super().get_channel_stream_schedule(user_id or self.id, segment_ids, start_time, limit)

    def get_clips_by_user_id(
            self,
            user_id: Optional[str] = None,
            started_at: Optional[datetime] = None,
            ended_at: Optional[datetime] = None,
            is_featured: Optional[bool] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Clip]:
        return super().get_clips_by_user_id(user_id or self.id, started_at, ended_at, is_featured, limit)

    def get_videos_by_user_id(
            self,
            user_id: Optional[str] = None,
            language: Optional[str] = None,
            period: Literal['all', 'day', 'month', 'week'] = 'all',
            sort: Literal['time', 'trending', 'views'] = 'time',
            video_type: Literal['all', 'archive', 'highlight', 'upload'] = 'all',
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Video]:
        return super().get_videos_by_user_id(user_id or self.id, language, period, sort, video_type, limit)

    def get_eventsub_subscriptions_by_user_id(
            self,
            user_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Subscription]:
        return super().get_eventsub_subscriptions_by_user_id(user_id or self.id, limit)

    async def start_commercial(self, length: int) -> StarCommercial:
        """
        Starts a commercial on the authenticated user's channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | channel:edit:commercial | Token holder is partner/affiliate and live |

        Parameters
        ----------
        length: int
            The length of the commercial to run, in seconds. Twitch tries to serve
            a commercial that's the requested length, but it may be shorter or longer.
            Must be between 1 and 180 seconds.

        Returns
        -------
        StarCommercial
            The commercial start response containing length, message, and retry_after.

        Raises
        ------
        ValueError
            If length is not between 1 and 180 seconds.
        TokenError
            If missing a valid user access token with scope.
        BadRequest
            If the broadcaster is not streaming live, not a partner/affiliate,
            or is still in cooldown period from a previous commercial.
        Unauthorized
            If the token doesn't have the required scope or doesn't match the broadcaster.
        NotFound
            If the broadcaster ID was not found.
        """
        if not 1 <= length <= 180:
            raise ValueError("length must be between 1 and 180")
        data = await self._state.http.start_commercial(self.id, length=length)
        return StarCommercial.from_data(data['data'][0])

    async def send_chat_message(
            self,
            message: str,
            broadcaster_id: Optional[str] = None,
            reply_message_id: Optional[str] = None
    ) -> SendMessageStatus:
        """
        Sends a message to the broadcaster's chat room.

        ??? warning

            Improper use can result in account termination. Recommended to use only
            in your own channel or with explicit moderator permission.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                              |
        |-------------|-----------------|---------------------------------------------------------|
        | User Access | user:write:chat | Token holder can send to chat, bot scopes if applicable |

        Parameters
        ----------
        message: str
            The message to send. Max 500 characters.
        broadcaster_id: str
            The ID of the broadcaster whose chat room the message will be sent to.
        reply_message_id: Optional[str]
            The ID of the message to reply to.

        Returns
        -------
        SendMessageStatus
            The status of the sent-message.

        Raises
        ------
        ValueError
            If message length > 500.
        TokenError
            If missing user token with scope.
        BadRequest
            If invalid parameters.
        Unauthorized
            If the token is invalid or expired.
        Forbidden
            If not permitted to send.
        """
        if len(message) > 500:
            raise ValueError("message must be <= 500 characters")

        data = await self._state.http.send_chat_message(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            sender_id=self.id,
            message=message,
            reply_parent_message_id=reply_message_id,
            for_source_only=None
        )
        return SendMessageStatus.from_data(data['data'][0])

    def get_ad_schedule(self) -> PaginatedRequest[..., AdSchedule]:
        """
        Gets the ad schedule for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes  | Authorization Requirements      |
        |-------------|------------------|---------------------------------|
        | User Access | channel:read:ads | Token holder is the broadcaster |

        Returns
        -------
        PaginatedRequest[..., AdSchedule]
            A paginated collection of AdSchedule objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        paginated_request = self._state.http.get_ad_schedule(self.id, broadcaster_id=self.id)
        paginated_request._data_transform = lambda data: tuple(AdSchedule.from_data(item) for item in data['data'])
        return paginated_request

    async def snooze_next_ad(self) -> AdSnooze:
        """
        Snoozes the next ad for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes    | Authorization Requirements      |
        |-------------|--------------------|---------------------------------|
        | User Access | channel:manage:ads | Token holder is the broadcaster |

        Returns
        -------
        AdSnooze
            The snooze information.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        data = await self._state.http.snooze_next_ad(self.id, broadcaster_id=self.id)
        return AdSnooze.from_data(data['data'][0])

    def get_extension_analytics(
            self,
            extension_id: Optional[str] = None,
            report_type: Optional[str] = None,
            started_at: Optional[datetime] = None,
            ended_at: Optional[datetime] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., AnalyticsReport]:
        """
        Gets analytics reports for extensions.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements      |
        |-------------|---------------------------|---------------------------------|
        | User Access | analytics:read:extensions | Token holder owns the extension |

        Parameters
        ----------
        extension_id: Optional[str]
            The ID of the extension.
        report_type: Optional[str]
            The type of report.
        started_at: Optional[datetime]
            The start date.
        ended_at: Optional[datetime]
            The end date.
        limit: Optional[int]
            The maximum number of reports.

        Returns
        -------
        PaginatedRequest[..., AnalyticsReport]
            A paginated collection of AnalyticsReport objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user does not own the extension.
        """
        started_at_str = to_rfc3339_string(normalize_timezone(started_at)) if started_at else None
        ended_at_str = to_rfc3339_string(normalize_timezone(ended_at)) if ended_at else None
        paginated_request = self._state.http.get_extension_analytics(
            self.id,
            extension_id=extension_id,
            report_type=report_type,
            started_at=started_at_str,
            ended_at=ended_at_str,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(AnalyticsReport.from_data(item) for item in data['data'])
        return paginated_request

    def get_game_analytics(
            self,
            game_id: Optional[str] = None,
            report_type: Optional[str] = None,
            started_at: Optional[datetime] = None,
            ended_at: Optional[datetime] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., AnalyticsReport]:
        """
        Gets analytics reports for games.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements |
        |-------------|----------------------|----------------------------|
        | User Access | analytics:read:games | Token holder owns the game |

        Parameters
        ----------
        game_id: Optional[str]
            The ID of the game.
        report_type: Optional[str]
            The type of report.
        started_at: Optional[datetime]
            The start date.
        ended_at: Optional[datetime]
            The end date.
        limit: Optional[int]
            The maximum number of reports.

        Returns
        -------
        PaginatedRequest[..., AnalyticsReport]
            A paginated collection of AnalyticsReport objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user does not own the game.
        """
        started_at_str = to_rfc3339_string(normalize_timezone(started_at)) if started_at else None
        ended_at_str = to_rfc3339_string(normalize_timezone(ended_at)) if ended_at else None
        paginated_request = self._state.http.get_game_analytics(
            self.id,
            game_id=game_id,
            report_type=report_type,
            started_at=started_at_str,
            ended_at=ended_at_str,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(AnalyticsReport.from_data(item) for item in data['data'])
        return paginated_request

    async def get_bits_leaderboard(
            self,
            count: int = 10,
            period: Literal['day', 'week', 'month', 'year', 'all'] = 'all',
            started_at: Optional[datetime] = None,
            user_id_filter: Optional[str] = None
    ) -> Tuple[BitsLeaderboardEntry, ...]:
        """
        Gets the Bits leaderboard for the authenticated broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements      |
        |-------------|-----------------|---------------------------------|
        | User Access | bits:read       | Token holder is the broadcaster |

        Parameters
        ----------
        count: int
            The number of entries to return. Max 100.
        period: Literal['day', 'week', 'month', 'year', 'all']
            The period for the leaderboard.
        started_at: Optional[datetime]
            The start time for the period.
        user_id_filter: Optional[str]
            The user ID to filter by.

        Returns
        -------
        Tuple[BitsLeaderboardEntry, ...]
            A tuple of BitsLeaderboardEntry objects.

        Raises
        ------
        ValueError
            If count > 100.
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        if count > 100:
            raise ValueError("count must be <= 100")
        started_at_str = to_rfc3339_string(normalize_timezone(started_at)) if started_at else None
        data = await self._state.http.get_bits_leaderboard(
            self.id,
            count=count,
            period=period,
            started_at=started_at_str,
            user_id_filter=user_id_filter
        )
        return tuple(BitsLeaderboardEntry.from_data(item) for item in data['data'])

    async def get_charity_campaign(self) -> CharityCampaign:
        """
        Gets the charity campaign for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements      |
        |-------------|----------------------|---------------------------------|
        | User Access | channel:read:charity | Token holder is the broadcaster |

        Returns
        -------
        CharityCampaign
            The charity campaign.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If no active campaign.
        """
        data = await self._state.http.get_charity_campaign(self.id, broadcaster_id=self.id)
        return CharityCampaign.from_data(data['data'][0])

    def get_charity_campaign_donations(
            self,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., CharityDonation]:
        """
        Gets the charity donations for the broadcaster's campaign.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements      |
        |-------------|----------------------|---------------------------------|
        | User Access | channel:read:charity | Token holder is the broadcaster |

        Parameters
        ----------
        limit: Optional[int]
            The maximum number of donations to return.

        Returns
        -------
        PaginatedRequest[..., CharityDonation]
            A paginated collection of CharityDonation objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If no active campaign.
        """
        paginated_request = self._state.http.get_charity_campaign_donations(
            self.id,
            broadcaster_id=self.id,
            fetch_limit=limit
        )

        paginated_request._data_transform = lambda data: tuple(
            CharityDonation.from_data(item) for item in data['data']
        )
        return paginated_request

    def get_chatters(
            self,
            broadcaster_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., Chatter]:
        """
        Gets the list of chatters in the broadcaster's chat room.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements |
        |-------------|-------------------------|----------------------------|
        | User Access | moderator:read:chatters | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        limit: Optional[int]
            The maximum number of chatters to return.

        Returns
        -------
        PaginatedRequest[..., Chatter]
            A paginated collection of Chatter objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        paginated_request = self._state.http.get_chatters(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(Chatter.from_data(item) for item in data['data'])
        return paginated_request

    async def update_chat_settings(self,
                                   settings: Dict[str, Any],
                                   broadcaster_id: Optional[str] = None
                                   ) -> ChatSettings:
        """
        Updates the channel's chat settings.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                | Authorization Requirements |
        |-------------|--------------------------------|----------------------------|
        | User Access | moderator:manage:chat_settings | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        settings: Dict[str, Any]
            The settings to update.

        Returns
        -------
        ChatSettings
            The updated chat settings.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or settings are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.update_chat_settings(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            settings=settings
        )
        return ChatSettings.from_data(data['data'][0])

    async def send_chat_announcement(self,
                                     message: str,
                                     broadcaster_id: Optional[str] = None,
                                     color: Literal['blue', 'green', 'orange', 'purple', 'primary'] = 'primary',
                                     ) -> None:
        """
        Sends an announcement to the channel's chat.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                | Authorization Requirements |
        |-------------|--------------------------------|----------------------------|
        | User Access | moderator:manage:announcements | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        message: str
            The announcement message.
        color: Literal['blue', 'green', 'orange', 'purple', 'primary']
            The color of the announcement.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, message, or color are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        await self._state.http.send_chat_announcement(
            self.id,
            broadcaster_id= broadcaster_id or self.id,
            moderator_id=self.id,
            message=message,
            color=color
        )

    async def send_shoutout(self,
                            to_broadcaster_id: str,
                            from_broadcaster_id: Optional[str] = None,
                            ) -> None:
        """
        Sends a shoutout to another broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements |
        |-------------|----------------------------|----------------------------|
        | User Access | moderator:manage:shoutouts | Token holder is moderator  |

        Parameters
        ----------
        from_broadcaster_id: Optional[str]
            The ID of the broadcaster sending the shoutout.
        to_broadcaster_id: str
            The ID of the broadcaster receiving the shoutout.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster IDs are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the from_broadcaster.
        """
        await self._state.http.send_shoutout(
            self.id,
            from_broadcaster_id=from_broadcaster_id or self.id,
            to_broadcaster_id=to_broadcaster_id,
            moderator_id=self.id
        )

    async def update_chat_color(self, color: str) -> None:
        """
        Updates the color used for the user's name in chat.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes        | Authorization Requirements |
        |-------------|------------------------|----------------------------|
        | User Access | user:manage:chat_color | Token holder is the user   |

        Parameters
        ----------
        color: str
            The color to set.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If color is invalid.
        Unauthorized
            If token invalid.
        """
        await self._state.http.update_user_chat_color(self.id, color=color)

    async def delete_chat_messages(self,
                                   broadcaster_id: Optional[str] = None,
                                   message_id: Optional[str] = None
                                   ) -> None:
        """
        Deletes chat messages in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                | Authorization Requirements |
        |-------------|--------------------------------|----------------------------|
        | User Access | moderator:manage:chat_messages | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        message_id: Optional[str]
            The ID of the message to delete. If None, deletes all.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or message_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        broadcaster_id = broadcaster_id or self.id
        await self._state.http.delete_chat_messages(
            self.id,
            broadcaster_id=broadcaster_id,
            moderator_id=self.id,
            message_id=message_id
        )

    async def warn_chat_user(self,
                             user_id: str,
                             reason: str,
                             broadcaster_id: Optional[str] = None
                             ) -> WarnReason:
        """
        Warns a user in chat.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements |
        |-------------|---------------------------|----------------------------|
        | User Access | moderator:manage:warnings | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        user_id: str
            The ID of the user to warn.
        reason: str
            The reason for the warning.

        Returns
        -------
        WarnReason
            The warn status.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, user_id, or reason are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        broadcaster_id = broadcaster_id or self.id
        data = await self._state.http.warn_chat_user(
            self.id,
            broadcaster_id=broadcaster_id,
            moderator_id=self.id,
            user_id_warn=user_id,
            reason=reason)
        return WarnReason.from_data(data['data'][0])

    async def create_clip(self, broadcaster_id: str, has_delay: bool = False) -> Clip:
        """
        Creates a clip from the broadcaster's stream.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements                |
        |-------------|-----------------|-------------------------------------------|
        | User Access | clips:edit      | Token holder is the broadcaster or editor |

        Parameters
        ----------
        broadcaster_id: str
            The ID of the broadcaster whose stream you want to create a clip from.
        has_delay: bool
            Whether to delay the clip.

        Returns
        -------
        Clip
            The created clip.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or editor.
        """
        data = await self._state.http.create_clip(self.id, broadcaster_id=broadcaster_id, has_delay=has_delay)
        return Clip.from_data(data['data'][0])

    async def get_creator_goals(self) -> Tuple[CreatorGoal, ...]:
        """
        Gets the creator goals for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes    | Authorization Requirements      |
        |-------------|--------------------|---------------------------------|
        | User Access | channel:read:goals | Token holder is the broadcaster |

        Returns
        -------
        Tuple[CreatorGoal, ...]
            A tuple of CreatorGoal objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        data = await self._state.http.get_creator_goals(self.id, broadcaster_id=self.id)
        return tuple(CreatorGoal.from_data(item) for item in data['data'])

    async def get_hype_train_events(
            self,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., HypeTrainEvent]:
        """
        Gets the Hype Train events for the broadcaster.

        !!! warning

            DEPRECATED Scheduled for removal on December 4, 2025. Use [Get Hype Train Status](../app/classes.md#twitch.api.UserAPI.get_hype_train_status) instead.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements      |
        |-------------|-------------------------|---------------------------------|
        | User Access | channel:read:hype_train | Token holder is the broadcaster |

        Parameters
        ----------
        limit: Optional[int]
            The maximum number of events to return.

        Returns
        -------
        PaginatedRequest[..., HypeTrainEvent]
            A paginated collection of HypeTrainEvent objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        paginated_request = self._state.http.get_hype_train_events(self.id,
                                                                   broadcaster_id=self.id,
                                                                   fetch_limit=limit)
        paginated_request._data_transform = lambda data: tuple(
            HypeTrainEvent.from_data(item) for item in data['data']
        )
        return paginated_request

    async def get_hype_train_status(self) -> HypeTrainStatus:
        """
        Gets the Hype Train status for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements      |
        |-------------|-------------------------|---------------------------------|
        | User Access | channel:read:hype_train | Token holder is the broadcaster |

        Returns
        -------
        HypeTrainStatus
            The current Hype Train status including current train and records.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        data = await self._state.http.get_hype_train_status(self.id, broadcaster_id=self.id)
        return HypeTrainStatus.from_data(data['data'][0])

    async def check_automod_status(self,
                                   messages: List[Dict[str, Any]],
                                   ) -> Tuple[AutoModStatusMessage, ...]:
        """
        Checks if messages are held by AutoMod.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements |
        |-------------|--------------------------|----------------------------|
        | User Access | moderator:manage:automod | Token holder is moderator  |

        Parameters
        ----------
        messages: List[Dict[str, Any]]
            The messages to check.

        Returns
        -------
        Tuple[AutoModStatusMessage, ...]
            The AutoMod status for each message.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or messages are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.check_automod_status(self.id, broadcaster_id=self.id, messages=messages)
        return tuple(AutoModStatusMessage.from_data(item) for item in data['data'])

    async def manage_held_automod_messages(self,
                                           msg_id: str,
                                           action: Literal['ALLOW', 'DENY']
                                           ) -> None:
        """
        Manages held AutoMod messages.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                  | Authorization Requirements |
        |-------------|-----------------------------------|---------------------------|
        | User Access | moderator:manage:automod_messages | Token holder is moderator |

        Parameters
        ----------
        msg_id: str
            The message ID.
        action: Literal['ALLOW', 'DENY']
            The action to take.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If msg_id or action are invalid.
        Unauthorized
            If token invalid.
        NotFound
            If the message was not found.
        """
        await self._state.http.manage_held_automod_messages(self.id, msg_id=msg_id, action=action)

    async def get_automod_settings(self, broadcaster_id: Optional[str] = None) -> AutoModSettings:
        """
        Gets the AutoMod settings for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                 | Authorization Requirements |
        |-------------|---------------------------------|----------------------------|
        | User Access | moderator:read:automod_settings | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.

        Returns
        -------
        AutoModSettings
            The AutoMod settings.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.get_automod_settings(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id
        )
        return AutoModSettings.from_data(data['data'][0])

    async def update_automod_settings(self,
                                      settings: Dict[str, Any],
                                      broadcaster_id: Optional[str] = None,
                                      ) -> AutoModSettings:
        """
        Updates the AutoMod settings for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                   | Authorization Requirements |
        |-------------|-----------------------------------|----------------------------|
        | User Access | moderator:manage:automod_settings | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        settings: Dict[str, Any]
            The settings to update.

        Returns
        -------
        AutoModSettings
            The updated AutoMod settings.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or settings are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.update_automod_settings(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            settings=settings
        )
        return AutoModSettings.from_data(data['data'][0])

    def get_banned_users(
            self,
            broadcaster_id: Optional[str] = None,
            user_ids: Set[str] = frozenset(),
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., BannedUser]:
        """
        Gets the banned users in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | moderation:read | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        user_ids: Set[str]
            User IDs to filter by. Max 100.
        limit: Optional[int]
            The maximum number of banned users to return.

        Returns
        -------
        PaginatedRequest[..., BannedUser]
            A paginated collection of BannedUser objects.

        Raises
        ------
        ValueError
            If user_ids > 100.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        if len(user_ids) > 100:
            raise ValueError("user_ids must not exceed 100 items")
        paginated_request = self._state.http.get_banned_users(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            user_ids=user_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            BannedUser.from_data(item) for item in data['data']
        )
        return paginated_request

    async def ban_user(self,
                       user_id: str,
                       broadcaster_id: Optional[str] = None,
                       duration: Optional[int] = None,
                       reason: str = ''
                       ) -> BannedUser:
        """
        Bans a user in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements |
        |-------------|-------------------------------|----------------------------|
        | User Access | moderator:manage:banned_users | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        user_id: str
            The ID of the user to ban.
        duration: Optional[int]
            The duration of the ban in seconds.
        reason: str
            The reason for the ban.

        Returns
        -------
        BannedUser
            The ban information.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, user_id, duration, or reason are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.ban_user(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            user_id_ban=user_id,
            duration=duration,
            reason=reason
        )
        return BannedUser.from_data(data['data'][0])

    async def unban_user(self, user_id: str, broadcaster_id: Optional[str] = None) -> None:
        """
        Unbans a user in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements |
        |-------------|-------------------------------|----------------------------|
        | User Access | moderator:manage:banned_users | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        user_id: str
            The ID of the user to unban.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        NotFound
            If the ban was not found.
        """
        await self._state.http.unban_user(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            user_id_unban=user_id
        )

    def get_unban_requests(
            self,
            broadcaster_id: Optional[str] = None,
            status: Literal['pending', 'approved', 'denied', 'acknowledged', 'canceled'] = 'pending',
            user_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., UnbanRequest]:
        """
        Gets unban requests for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes               | Authorization Requirements |
        |-------------|-------------------------------|----------------------------|
        | User Access | moderator:read:unban_requests | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        status: Literal['pending', 'approved', 'denied', 'acknowledged', 'canceled']
            The status to filter by.
        user_id: Optional[str]
            The user ID to filter by.
        limit: Optional[int]
            The maximum number of unban requests to return.

        Returns
        -------
        PaginatedRequest[..., UnbanRequest]
            A paginated collection of UnbanRequest objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or status are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        paginated_request = self._state.http.get_unban_requests(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            status=status,
            user_id_filter=user_id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(UnbanRequest.from_data(item) for item in data['data'])
        return paginated_request

    async def resolve_unban_request(self,
                                    unban_request_id: str,
                                    status: Literal['approved', 'denied'],
                                    resolution_text: Optional[str] = None,
                                    broadcaster_id: Optional[str] = None
                                    ) -> UnbanRequest:
        """
        Resolves an unban request.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                 | Authorization Requirements |
        |-------------|---------------------------------|----------------------------|
        | User Access | moderator:manage:unban_requests | Token holder is moderator  |

        Parameters
        ----------
        unban_request_id: str
            The ID of the unban request.
        status: Literal['approved', 'denied']
            The resolution status.
        resolution_text: Optional[str]
            The resolution text.
        broadcaster_id: Optional[str]
            The ID of the broadcaster.

        Returns
        -------
        UnbanRequest
            The resolved unban request.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, unban_request_id, status, or resolution_text are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        NotFound
            If the unban request was not found.
        """
        data = await self._state.http.resolve_unban_request(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            unban_request_id=unban_request_id,
            status=status,
            resolution_text=resolution_text
        )
        return UnbanRequest.from_data(data['data'][0])

    def get_blocked_terms(
            self,
            broadcaster_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., BlockedTerm]:
        """
        Gets the blocked terms in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes              | Authorization Requirements |
        |-------------|------------------------------|----------------------------|
        | User Access | moderator:read:blocked_terms | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        limit: Optional[int]
            The maximum number of blocked terms to return.

        Returns
        -------
        PaginatedRequest[..., BlockedTerm]
            A paginated collection of BlockedTerm objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        paginated_request = self._state.http.get_blocked_terms(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(BlockedTerm.from_data(item) for item in data['data'])
        return paginated_request

    async def add_blocked_term(self, text: str, broadcaster_id: Optional[str] = None) -> BlockedTerm:
        """
        Adds a blocked term to the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                | Authorization Requirements |
        |-------------|--------------------------------|----------------------------|
        | User Access | moderator:manage:blocked_terms | Token holder is moderator  |

        Parameters
        ----------
        text: str
            The term to block.
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
       
        Returns
        -------
        BlockedTerm
            The added blocked term.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or text are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.add_blocked_term(self.id,
                                                       broadcaster_id=broadcaster_id or self.id,
                                                       moderator_id=self.id,
                                                       text=text
                                                       )
        return BlockedTerm.from_data(data['data'][0])

    async def remove_blocked_term(self, term_id: str, broadcaster_id: Optional[str] = None) -> None:
        """
        Removes a blocked term from the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes                | Authorization Requirements |
        |-------------|--------------------------------|----------------------------|
        | User Access | moderator:manage:blocked_terms | Token holder is moderator  |

        Parameters
        ----------
        term_id: str
            The ID of the term to remove.
        broadcaster_id: Optional[str]
            The ID of the broadcaster.
        

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or term_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        NotFound
            If the term was not found.
        """
        await self._state.http.remove_blocked_term(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            term_id=term_id
        )

    def get_moderators(self,
                       user_ids: Set[str] = frozenset(),
                       limit: Optional[int] = 100
                       ) -> PaginatedRequest[..., Moderator]:
        """
        Gets the moderators in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements               |
        |-------------|-----------------|------------------------------------------|
        | User Access | moderation:read | Token holder is broadcaster or moderator |

        Parameters
        ----------
        user_ids: Set[str]
            User IDs to filter by. Max 100.
        limit: Optional[int]
            The maximum number of moderators to return.

        Returns
        -------
        PaginatedRequest[..., Moderator]
            A paginated collection of Moderator objects.

        Raises
        ------
        ValueError
            If user_ids > 100.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        if len(user_ids) > 100:
            raise ValueError("user_ids must not exceed 100 items")
        paginated_request = self._state.http.get_moderators(
            self.id,
            broadcaster_id=self.id,
            user_ids=user_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(Moderator.from_data(item) for item in data['data'])
        return paginated_request

    async def add_channel_moderator(self, user_id: str) -> None:
        """
        Adds a moderator to the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements  |
        |-------------|---------------------------|-----------------------------|
        | User Access | channel:manage:moderators | Token holder is broadcaster |

        Parameters
        ----------
        user_id: str
            The ID of the user to add as moderator.
        
        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        await self._state.http.add_channel_moderator(
            self.id,
            broadcaster_id=self.id,
            user_id_mod=user_id
        )

    async def remove_channel_moderator(self, user_id: str) -> None:
        """
        Removes a moderator from the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements  |
        |-------------|---------------------------|-----------------------------|
        | User Access | channel:manage:moderators | Token holder is broadcaster |

        Parameters
        ----------
        user_id: str
            The ID of the user to remove as moderator.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If the moderator was not found.
        """
        await self._state.http.remove_channel_moderator(self.id, broadcaster_id=self.id, user_id_mod=user_id)

    def get_vips(self,
                 user_ids: Set[str] = frozenset(),
                 limit: Optional[int] = 100
                 ) -> PaginatedRequest[..., ChannelVIP]:
        """
        Gets the VIPs in the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes   | Authorization Requirements               |
        |-------------|-------------------|------------------------------------------|
        | User Access | channel:read:vips | Token holder is broadcaster or moderator |

        Parameters
        ----------
        user_ids: Set[str]
            User IDs to filter by. Max 100.
        limit: Optional[int]
            The maximum number of VIPs to return.

        Returns
        -------
        PaginatedRequest[..., ChannelVIP]
            A paginated collection of ChannelVIP objects.

        Raises
        ------
        ValueError
            If user_ids > 100.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        if len(user_ids) > 100:
            raise ValueError("user_ids must not exceed 100 items")

        paginated_request = self._state.http.get_vips(
            self.id,
            broadcaster_id=self.id,
            user_ids=user_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(ChannelVIP.from_data(item) for item in data['data'])
        return paginated_request

    async def add_channel_vip(self, user_id: str) -> None:
        """
        Adds a VIP to the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes     | Authorization Requirements  |
        |-------------|---------------------|-----------------------------|
        | User Access | channel:manage:vips | Token holder is broadcaster |

        Parameters
        ----------
        user_id: str
            The ID of the user to add as VIP.
        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        await self._state.http.add_channel_vip(self.id, broadcaster_id=self.id, user_id_vip=user_id)

    async def remove_channel_vip(self, user_id: str) -> None:
        """
        Removes a VIP from the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes     | Authorization Requirements  |
        |-------------|---------------------|-----------------------------|
        | User Access | channel:manage:vips | Token holder is broadcaster |

        Parameters
        ----------
        user_id: str
            The ID of the user to remove as VIP.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If the VIP was not found.
        """
        await self._state.http.remove_channel_vip(self.id, broadcaster_id=self.id, user_id_vip=user_id)

    async def update_shield_mode_status(self,
                                        is_active: bool,
                                        broadcaster_id: Optional[str] = None
                                        ) -> ShieldModeStatus:
        """
        Updates the Shield Mode status for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes              | Authorization Requirements |
        |-------------|------------------------------|----------------------------|
        | User Access | moderator:manage:shield_mode | Token holder is moderator  |

        Parameters
        ----------
        is_active: bool
            Whether to activate Shield Mode.
        broadcaster_id: Optional[str]
            The ID of the broadcaster.

        Returns
        -------
        ShieldModeStatus
            The Shield Mode status.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.update_shield_mode_status(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id,
            is_active=is_active
        )
        return ShieldModeStatus.from_data(data['data'][0])

    async def get_shield_mode_status(self, broadcaster_id: Optional[str] = None) -> ShieldModeStatus:
        """
        Gets the Shield Mode status for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements |
        |-------------|----------------------------|----------------------------|
        | User Access | moderator:read:shield_mode | Token holder is moderator  |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster.

        Returns
        -------
        ShieldModeStatus
            The Shield Mode status.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not a moderator for the broadcaster.
        """
        data = await self._state.http.get_shield_mode_status(
            self.id,
            broadcaster_id=broadcaster_id or self.id,
            moderator_id=self.id
        )
        return ShieldModeStatus.from_data(data['data'][0])

    def get_polls(
            self,
            poll_ids: Set[str] = frozenset(),
            limit: Optional[int] = 20
    ) -> PaginatedRequest[..., Poll]:
        """
        Gets polls for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes    | Authorization Requirements               |
        |-------------|--------------------|------------------------------------------|
        | User Access | channel:read:polls | Token holder is broadcaster or moderator |

        Parameters
        ----------
        poll_ids: Set[str]
            Poll IDs to filter by. Max 5.
        limit: Optional[int]
            The maximum number of polls to return.

        Returns
        -------
        PaginatedRequest[..., Poll]
            A paginated collection of Poll objects.

        Raises
        ------
        ValueError
            If poll_ids > 5.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or poll_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        if len(poll_ids) > 5:
            raise ValueError("poll_ids must not exceed 5 items")
        paginated_request = self._state.http.get_polls(
            self.id,
            broadcaster_id=self.id,
            poll_ids=poll_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(Poll.from_data(item) for item in data['data'])
        return paginated_request

    async def create_poll(self,
                          title: str,
                          choices: List[str],
                          duration: int,
                          bits_voting_enabled: bool = False,
                          bits_per_vote: int = 0,
                          channel_points_voting_enabled: bool = False,
                          channel_points_per_vote: int = 0
                          ) -> Poll:
        """
        Creates a poll for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements               |
        |-------------|----------------------|------------------------------------------|
        | User Access | channel:manage:polls | Token holder is broadcaster or moderator |

        Parameters
        ----------
        title: str
            The poll title.
        choices: List[str]
            The choices for the poll.
        duration: int
            The duration of the poll in seconds.
        bits_voting_enabled: bool
            Whether Bits voting is enabled.
        bits_per_vote: int
            Bits per vote.
        channel_points_voting_enabled: bool
            Whether Channel Points voting is enabled.
        channel_points_per_vote: int
            Channel Points per vote.

        Returns
        -------
        Poll
            The created poll.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        data = await self._state.http.create_poll(
            self.id,
            broadcaster_id=self.id,
            title=title,
            choices=choices,
            duration=duration,
            bits_voting_enabled=bits_voting_enabled,
            bits_per_vote=bits_per_vote,
            channel_points_voting_enabled=channel_points_voting_enabled,
            channel_points_per_vote=channel_points_per_vote
        )
        return Poll.from_data(data['data'][0])

    async def end_poll(self,
                       poll_id: str,
                       status: Literal['TERMINATED', 'ARCHIVED']
                       ) -> Poll:
        """
        Ends a poll.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements               |
        |-------------|----------------------|------------------------------------------|
        | User Access | channel:manage:polls | Token holder is broadcaster or moderator |

        Parameters
        ----------
        poll_id: str
            The ID of the poll.
        status: Literal['TERMINATED', 'ARCHIVED']
            The status to set.

        Returns
        -------
        Poll
            The ended poll.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, poll_id, or status are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        NotFound
            If the poll was not found.
        """
        data = await self._state.http.end_poll(
            self.id,
            broadcaster_id=self.id,
            poll_id=poll_id,
            status=status
        )
        return Poll.from_data(data['data'][0])

    def get_predictions(
            self,
            prediction_ids: Set[str] = frozenset(),
            limit: Optional[int] = 20
    ) -> PaginatedRequest[..., Prediction]:
        """
        Gets predictions for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements               |
        |-------------|--------------------------|------------------------------------------|
        | User Access | channel:read:predictions | Token holder is broadcaster or moderator |

        Parameters
        ----------
        prediction_ids: Set[str]
            Prediction IDs to filter by. Max 5.
        limit: Optional[int]
            The maximum number of predictions to return.

        Returns
        -------
        PaginatedRequest[..., Prediction]
            A paginated collection of Prediction objects.

        Raises
        ------
        ValueError
            If prediction_ids > 5.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or prediction_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        if len(prediction_ids) > 5:
            raise ValueError("prediction_ids must not exceed 5 items")
        paginated_request = self._state.http.get_predictions(
            self.id,
            broadcaster_id=self.id,
            prediction_ids=prediction_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(Prediction.from_data(item) for item in data['data'])
        return paginated_request

    async def create_prediction(self,
                                title: str,
                                outcomes: List[str],
                                duration: int
                                ) -> Prediction:
        """
        Creates a prediction for the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements               |
        |-------------|----------------------------|------------------------------------------|
        | User Access | channel:manage:predictions | Token holder is broadcaster or moderator |

        Parameters
        ----------
        title: str
            The prediction title.
        outcomes: List[str]
            The outcomes for the prediction.
        duration: int
            The duration of the prediction in seconds.

        Returns
        -------
        Prediction
            The created prediction.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        data = await self._state.http.create_prediction(
            self.id,
            broadcaster_id=self.id,
            title=title,
            outcomes=outcomes,
            duration=duration
        )
        return Prediction.from_data(data['data'][0])

    async def end_prediction(self,
                             prediction_id: str,
                             status: Literal['RESOLVED', 'CANCELED'],
                             winning_outcome_id: Optional[str] = None
                             ) -> Prediction:
        """
        Ends a prediction.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements               |
        |-------------|----------------------------|------------------------------------------|
        | User Access | channel:manage:predictions | Token holder is broadcaster or moderator |

        Parameters
        ----------
        prediction_id: str
            The ID of the prediction.
        status: Literal['RESOLVED', 'CANCELED']
            The status to set.
        winning_outcome_id: Optional[str]
            The ID of the winning outcome if resolved.

        Returns
        -------
        Prediction
            The ended prediction.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id, prediction_id, status, or winning_outcome_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        NotFound
            If the prediction was not found.
        """
        data = await self._state.http.end_prediction(
            self.id,
            broadcaster_id=self.id,
            prediction_id=prediction_id,
            status=status,
            winning_outcome_id=winning_outcome_id
        )
        return Prediction.from_data(data['data'][0])

    async def start_raid(self,to_broadcaster_id: str) -> Raid:
        """
        Starts a raid to another channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements  |
        |-------------|----------------------|-----------------------------|
        | User Access | channel:manage:raids | Token holder is broadcaster |

        Parameters
        ----------
        to_broadcaster_id: str
            The ID of the broadcaster to raid.

        Returns
        -------
        Raid
            The raid information.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the from_broadcaster.
        """
        data = await self._state.http.start_raid(
            self.id,
            from_broadcaster_id=self.id,
            to_broadcaster_id=to_broadcaster_id
        )
        return Raid.from_data(data['data'][0])

    async def cancel_raid(self) -> None:
        """
        Cancels a raid.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements  |
        |-------------|----------------------|-----------------------------|
        | User Access | channel:manage:raids | Token holder is broadcaster |

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If no pending raid.
        """
        await self._state.http.cancel_raid(self.id, broadcaster_id=self.id)

    async def update_channel_stream_schedule(self,
                                             is_vacation_enabled: bool,
                                             vacation_start_time: Optional[datetime] = None,
                                             vacation_end_time: Optional[datetime] = None,
                                             timezone: Optional[str] = None
                                             ) -> None:
        """
        Updates the channel's stream schedule.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements  |
        |-------------|-------------------------|-----------------------------|
        | User Access | channel:manage:schedule | Token holder is broadcaster |

        Parameters
        ----------
        is_vacation_enabled: bool
            Whether vacation is enabled.
        vacation_start_time: Optional[datetime]
            Vacation start time.
        vacation_end_time: Optional[datetime]
            Vacation end time.
        timezone: Optional[str]
            The timezone.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or other parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        vacation_start_time_str = to_rfc3339_string(
            normalize_timezone(vacation_start_time)
        ) if vacation_start_time else None

        vacation_end_time_str = to_rfc3339_string(
            normalize_timezone(vacation_end_time)
        ) if vacation_end_time else None

        await self._state.http.update_channel_stream_schedule(
            self.id,
            broadcaster_id=self.id,
            is_vacation_enabled=is_vacation_enabled,
            vacation_start_time=vacation_start_time_str,
            vacation_end_time=vacation_end_time_str,
            timezone=timezone
        )

    async def create_channel_stream_schedule_segment(self,
                                                     start_time: datetime,
                                                     timezone: str,
                                                     is_recurring: bool,
                                                     duration: Optional[int] = None,
                                                     category_id: Optional[str] = None,
                                                     title: Optional[str] = None
                                                     ) -> ChannelStreamSchedule:
        """
        Creates a stream schedule segment.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements  |
        |-------------|-------------------------|-----------------------------|
        | User Access | channel:manage:schedule | Token holder is broadcaster |

        Parameters
        ----------
        start_time: datetime
            The start time.
        timezone: str
            The timezone.
        is_recurring: bool
            Whether the segment is recurring.
        duration: Optional[int]
            The duration.
        category_id: Optional[str]
            The category ID.
        title: Optional[str]
            The title.

        Returns
        -------
        ChannelStreamSchedule
            The updated schedule.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        start_time_str = to_rfc3339_string(normalize_timezone(start_time))
        data = await self._state.http.create_channel_stream_schedule_segment(
            self.id,
            broadcaster_id=self.id,
            start_time=start_time_str,
            timezone=timezone,
            is_recurring=is_recurring,
            duration=duration,
            category_id=category_id,
            title=title
        )
        return ChannelStreamSchedule.from_data(data['data'])

    async def update_channel_stream_schedule_segment(self,
                                                     segment_id: str,
                                                     start_time: Optional[datetime] = None,
                                                     duration: Optional[int] = None,
                                                     category_id: Optional[str] = None,
                                                     is_canceled: Optional[bool] = None,
                                                     timezone: Optional[str] = None,
                                                     title: Optional[str] = None
                                                     ) -> ChannelStreamSchedule:
        """
        Updates a stream schedule segment.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements  |
        |-------------|-------------------------|-----------------------------|
        | User Access | channel:manage:schedule | Token holder is broadcaster |

        Parameters
        ----------
        segment_id: str
            The ID of the segment.
        start_time: Optional[datetime]
            The new start time.
        duration: Optional[int]
            The new duration.
        category_id: Optional[str]
            The new category ID.
        is_canceled: Optional[bool]
            Whether to cancel the segment.
        timezone: Optional[str]
            The new timezone.
        title: Optional[str]
            The new title.
        Returns
        -------
        ChannelStreamSchedule
            The updated schedule.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If the segment was not found.
        """
        start_time_str = to_rfc3339_string(normalize_timezone(start_time)) if start_time else None
        data = await self._state.http.update_channel_stream_schedule_segment(
            self.id,
            broadcaster_id=self.id,
            segment_id=segment_id,
            start_time=start_time_str,
            duration=duration,
            category_id=category_id,
            is_canceled=is_canceled,
            timezone=timezone,
            title=title
        )
        return ChannelStreamSchedule.from_data(data['data'])

    async def delete_channel_stream_schedule_segment(self, segment_id: str) -> None:
        """
        Deletes a stream schedule segment.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements  |
        |-------------|-------------------------|-----------------------------|
        | User Access | channel:manage:schedule | Token holder is broadcaster |

        Parameters
        ----------
        segment_id: str
            The ID of the segment.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or segment_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        NotFound
            If the segment was not found.
        """
        await self._state.http.delete_channel_stream_schedule_segment(
            self.id,
            broadcaster_id=self.id,
            segment_id=segment_id
        )

    async def create_stream_marker(self,
                                   user_id: Optional[str] = None,
                                   description: Optional[str] = None
                                   ) -> StreamMarker:
        """
        Creates a stream marker.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements            |
        |-------------|--------------------------|---------------------------------------|
        | User Access | channel:manage:broadcast | Token holder is broadcaster or editor |

        Parameters
        ----------
        user_id: Optional[str]
            The ID of the broadcaster.
        description: Optional[str]
            The description of the marker.

        Returns
        -------
        StreamMarker
            The created marker.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If user_id or description are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or editor.
        """
        data = await self._state.http.create_stream_marker(
            self.id,
            user_id_create= user_id or self.id,
            description=description
        )
        return StreamMarker.from_data(data['data'][0])

    def get_stream_markers(
            self,
            user_id: Optional[str] = None,
            video_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., StreamMarker]:
        """
        Gets stream markers.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes     | Authorization Requirements            |
        |-------------|---------------------|---------------------------------------|
        | User Access | user:read:broadcast | Token holder is broadcaster or editor |

        Parameters
        ----------
        user_id: Optional[str]
            The ID of the broadcaster.
        video_id: Optional[str]
            The ID of the video.
        limit: Optional[int]
            The maximum number of markers to return.

        Returns
        -------
        PaginatedRequest[..., StreamMarker]
            A paginated collection of StreamMarker objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If user_id or video_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or editor.
        """
        paginated_request = self._state.http.get_stream_markers(
            self.id,
            user_id_mark=user_id or self.id,
            video_id=video_id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(StreamMarker.from_data(item) for item in data['data'])
        return paginated_request

    def get_broadcaster_subscriptions(
            self,
            user_ids: Set[str] = frozenset(),
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., UserSubscription]:
        """
        Gets subscribers to the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements  |
        |-------------|----------------------------|-----------------------------|
        | User Access | channel:read:subscriptions | Token holder is broadcaster |

        Parameters
        ----------
        user_ids: Set[str]
            User IDs to filter by. Max 100.
        limit: Optional[int]
            The maximum number of subscriptions to return.

        Returns
        -------
        PaginatedRequest[..., UserSubscription]
            A paginated collection of UserSubscription objects.

        Raises
        ------
        ValueError
            If user_ids > 100.
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_ids are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        if len(user_ids) > 100:
            raise ValueError("user_ids must not exceed 100 items")
        paginated_request = self._state.http.get_broadcaster_subscriptions(
            self.id,
            broadcaster_id=self.id,
            user_ids=user_ids,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            UserSubscription.from_data(item) for item in data['data']
        )
        return paginated_request

    async def check_user_subscription(self, broadcaster_id: str) -> UserSubscription:
        """
        Checks if a user is subscribed to the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes            | Authorization Requirements                |
        |-------------|----------------------------|-------------------------------------------|
        | User Access | channel:read:subscriptions | Token holder is broadcaster or subscriber |

        Parameters
        ----------
        broadcaster_id: str
            The ID of the broadcaster.

        Returns
        -------
        UserSubscription
            The subscription information.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or the subscriber.
        NotFound
            If no subscription found.
        """
        data = await self._state.http.check_user_subscription(
            self.id,
            broadcaster_id=broadcaster_id,
            user_id_check=self.id
        )
        return UserSubscription.from_data(data['data'][0])

    async def update_user(self, description: Optional[str] = None) -> UserInfo:
        """
        Updates the user's information.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes | Authorization Requirements |
        |-------------|-----------------|----------------------------|
        | User Access | user:edit       | Token holder is the user   |

        Parameters
        ----------
        description: Optional[str]
            The new description.

        Returns
        -------
        UserInfo
            The updated user information.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If description is invalid.
        Unauthorized
            If token invalid.
        """
        data = await self._state.http.update_user(self.id, description=description)
        return UserInfo.from_data(data['data'][0])

    def get_user_block_list(
            self,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., UserIdentity]:
        """
        Gets the user's block list.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements |
        |-------------|-------------------------|----------------------------|
        | User Access | user:read:blocked_users | Token holder is the user   |

        Parameters
        ----------
        limit: Optional[int]
            The maximum number of blocked users to return.

        Returns
        -------
        PaginatedRequest[..., UserIdentity]
            A paginated collection of UserIdentity objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        """
        paginated_request = self._state.http.get_user_block_list(
            self.id,
            broadcaster_id=self.id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            UserIdentity(item['user_id'], item['user_login'], item['user_name']) for item in data['data']
        )
        return paginated_request

    async def block_user(self,
                         target_user_id: str,
                         source_context: Optional[Literal['chat', 'whisper']] = None,
                         reason: Optional[Literal['spam', 'harassment', 'other']] = None
                         ) -> None:
        """
        Blocks a user.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements |
        |-------------|---------------------------|----------------------------|
        | User Access | user:manage:blocked_users | Token holder is the user   |

        Parameters
        ----------
        target_user_id: str
            The ID of the user to block.
        source_context: Optional[Literal['chat', 'whisper']]
            The source context.
        reason: Optional[Literal['spam', 'harassment', 'other']]
            The reason.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If target_user_id, source_context, or reason are invalid.
        Unauthorized
            If token invalid.
        """
        await self._state.http.block_user(
            self.id,
            target_user_id=target_user_id,
            source_context=source_context,
            reason=reason
        )

    async def unblock_user(self, target_user_id: str) -> None:
        """
        Unblocks a user.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes           | Authorization Requirements |
        |-------------|---------------------------|----------------------------|
        | User Access | user:manage:blocked_users | Token holder is the user   |

        Parameters
        ----------
        target_user_id: str
            The ID of the user to unblock.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If target_user_id is invalid.
        Unauthorized
            If token invalid.
        NotFound
            If the block was not found.
        """
        await self._state.http.unblock_user(self.id, target_user_id=target_user_id)

    async def get_user_extensions(self) -> Tuple[UserExtension, ...]:
        """
        Gets the user's installed extensions.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements |
        |-------------|----------------------|----------------------------|
        | User Access | user:read:extensions | Token holder is the user   |

        Returns
        -------
        Tuple[UserExtension, ...]
            A tuple of UserExtension objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        Unauthorized
            If token invalid.
        """
        data = await self._state.http.get_user_extensions(self.id)
        return tuple(UserExtension.from_data(item) for item in data['data'])

    async def get_user_active_extensions(self) -> ActiveUserExtension:
        """
        Gets the user's active extensions.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements |
        |-------------|----------------------|----------------------------|
        | User Access | user:read:extensions | Token holder is the user   |

        Returns
        -------
        ActiveUserExtension
            The active extensions.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If user_id is invalid.
        Unauthorized
            If token invalid.
        """
        data = await self._state.http.get_user_active_extensions(self.id, user_id_ext=self.id)
        return ActiveUserExtension.from_data(data['data'])

    async def update_user_extensions(self, data: Dict[str, Any]) -> UserActiveExtensionUpdate:
        """
        Updates the user's active extensions.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements |
        |-------------|----------------------|----------------------------|
        | User Access | user:edit:extensions | Token holder is the user   |

        Parameters
        ----------
        data: Dict[str, Any]
            The extension configuration data.

        Returns
        -------
        UserActiveExtensionUpdate
            The updated active extensions.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If data is invalid.
        Unauthorized
            If token invalid.
        """
        data = await self._state.http.update_user_extensions(self.id, data=data)
        return UserActiveExtensionUpdate.from_data(data['data'])

    async def modify_channel_information(self,
                                         game_id: Optional[str] = None,
                                         language: Optional[str] = None,
                                         title: Optional[str] = None,
                                         delay: Optional[int] = None,
                                         tags: Optional[List[str]] = None,
                                         content_classification_labels: Optional[Set[str]] = None,
                                         is_branded_content: Optional[bool] = None
                                         ) -> None:
        """
        Modifies channel information for users.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements      |
        |-------------|--------------------------|---------------------------------|
        | User Access | channel:manage:broadcast | Token holder is the broadcaster |

        Parameters
        ----------
        game_id: Optional[str]
            The current game ID being played on the channel.
        language: Optional[str]
            The language of the stream.
        title: Optional[str]
            The title of the stream.
        delay: Optional[int]
            Stream delay in seconds.
        tags: Optional[List[str]]
            List of labels to tag the stream.
        content_classification_labels: Optional[List[str]]
            List of CCL IDs.
        is_branded_content: Optional[bool]
            Indicates if the stream is branded content.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If parameters are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        await self._state.http.modify_channel_information(
            self.id,
            broadcaster_id=self.id,
            game_id=game_id,
            language=language,
            title=title,
            delay=delay,
            tags=tags,
            content_classification_labels=content_classification_labels,
            is_branded_content=is_branded_content,
        )

    async def get_channel_editors(self) -> Tuple[ChannelEditor, ...]:
        """
        Gets the channel editors for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes      | Authorization Requirements      |
        |-------------|----------------------|---------------------------------|
        | User Access | channel:read:editors | Token holder is the broadcaster |

        Returns
        -------
        Tuple[ChannelEditor, ...]
            A tuple of ChannelEditor objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        data = await self._state.http.get_channel_editors(self.id, broadcaster_id=self.id)
        return tuple(ChannelEditor.from_data(item) for item in data['data'])

    def get_followed_channels(
            self,
            broadcaster_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., FollowedChannel]:
        """
        Gets the channels followed by the user.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes   | Authorization Requirements |
        |-------------|-------------------|----------------------------|
        | User Access | user:read:follows | Token holder is the user   |

        Parameters
        ----------
        broadcaster_id: Optional[str]
            The ID of the broadcaster to check if followed.
        limit: Optional[int]
            The maximum number of followed channels to return.

        Returns
        -------
        PaginatedRequest[..., FollowedChannel]
            A paginated collection of FollowedChannel objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If user_id or broadcaster_id are invalid.
        Unauthorized
            If token invalid.
        """
        paginated_request = self._state.http.get_followed_channels(
            self.id,
            user_id_follows=self.id,
            broadcaster_id=broadcaster_id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            FollowedChannel.from_data(item) for item in data['data']
        )
        return paginated_request

    def get_channel_followers(
            self,
            user_id: Optional[str] = None,
            limit: Optional[int] = 100
    ) -> PaginatedRequest[..., ChannelFollower]:
        """
        Gets the followers of the channel.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes          | Authorization Requirements               |
        |-------------|--------------------------|------------------------------------------|
        | User Access | moderator:read:followers | Token holder is broadcaster or moderator |

        Parameters
        ----------
        user_id: Optional[str]
            The ID of the user to check if following.
        limit: Optional[int]
            The maximum number of followers to return.

        Returns
        -------
        PaginatedRequest[..., ChannelFollower]
            A paginated collection of ChannelFollower objects.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id or user_id are invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster or moderator.
        """
        paginated_request = self._state.http.get_channel_followers(
            self.id,
            broadcaster_id=self.id,
            user_id_check=user_id,
            fetch_limit=limit
        )
        paginated_request._data_transform = lambda data: tuple(
            ChannelFollower.from_data(item) for item in data['data']
        )
        return paginated_request

    async def get_stream_key(self) -> StreamKey:
        """
        Gets the stream key for the broadcaster.

        Token and Authorization Requirements::

        | Token Type  | Required Scopes         | Authorization Requirements      |
        |-------------|-------------------------|---------------------------------|
        | User Access | channel:read:stream_key | Token holder is the broadcaster |

        Returns
        -------
        StreamKey
            The stream key.

        Raises
        ------
        TokenError
            If missing user token with scope.
        BadRequest
            If broadcaster_id is invalid.
        Unauthorized
            If token invalid.
        Forbidden
            If the token user is not the broadcaster.
        """
        data = await self._state.http.get_stream_key(self.id, broadcaster_id=self.id)
        return StreamKey.from_data(data['data'][0])
