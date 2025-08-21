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

from typing import (TypeVar, Coroutine, Dict, Tuple, TYPE_CHECKING, List, Optional, Any, AsyncIterator, Callable,
                    Awaitable, Set, ClassVar)
from . import utils, __version__, __url__
from urllib.parse import urlencode
from types import MappingProxyType
import aiohttp
import asyncio
import logging
import time

from .errors import (
    HTTPException,
    TwitchServerError,
    Forbidden,
    NotFound,
    RateLimited,
    Unauthorized,
    BadRequest,
    TokenError,
    AuthFailure,
    Conflict
)

if TYPE_CHECKING:
    from .types.helix import EventsubSubscription, Data, DataL, PData, EmoteData
    from .types.tokens import ClientCredentials, ValidateToken, DeviceCode, Token
    from .types import helix

__all__  = ('PaginatedRequest', 'HTTPClient')

_logger = logging.getLogger(__name__)

T = TypeVar('T')
Response = Coroutine[Any, Any, T]


class Route:
    BASE: ClassVar[str] = "https://api.twitch.tv/helix/"
    OAUTH2: ClassVar[str] = "https://id.twitch.tv/oauth2/"

    def __init__(self, method: str, path: str, *, base_url: str = None, **params) -> None:
        self.method = method.upper()
        self.path = path.lstrip('/')
        self.base_url = base_url or self.BASE
        self.params = {k: v for k, v in params.items() if v is not None}

    @classmethod
    def oauth2(cls, method: str, path: str, **params) -> Route:
        """Create OAuth2 route"""
        return cls(method, path, base_url=cls.OAUTH2, **params)

    @property
    def url(self) -> str:
        if not self.params:
            return f"{self.base_url}{self.path}"

        query_params = []
        for k, v in self.params.items():
            if isinstance(v, (list, tuple, set, frozenset)):
                query_params.extend((k, str(item)) for item in v)
            else:
                query_params.append((k, str(v)))

        query = urlencode(query_params)
        return f"{self.base_url}{self.path}?{query}"


class PaginatedRequest[T, R]:
    """
    Paginated request handler for API endpoints with cursor-based pagination.

    Attributes
    ----------
    cursor: Optional[str]
        Current pagination cursor for the next request.

    Examples
    --------
    Fetch all items::

        followers = await user.get_channel_followers()

    Iterate one by one::

        async for follower in user.get_channel_followers():
            ...

    Manual pagination::

        paginator = user.get_channel_followers()
        page = await paginator.next()
    """

    def __init__(
            self,
            request_func: Callable[..., Awaitable[Any]],
            route: Route,
            max_first: int,
            fetch_limit: Optional[int] = None,
            **request_params: Any
    ) -> None:
        self.cursor: Optional[str] = None
        self._max_first: int = max_first
        self._fetched_count: int = 0
        self._request_func: Callable[..., Awaitable[Any]] = request_func
        self._base_route: Route = route
        self._request_params: Dict[str, Any] = request_params
        self._fetch_limit: Optional[int] = fetch_limit
        self._done: bool = False
        self._data_transform: Optional[Callable[[T], Tuple[R, ...]]] = None

    @property
    def done(self) -> bool:
        """Whether pagination has completed and no more pages are available."""
        return self._done

    @property
    def fetched_count(self) -> int:
        """Total number of items fetched across all pages so far."""
        return self._fetched_count

    def _calculate_page_size(self) -> int:
        """Calculate the appropriate page size for the next request."""
        if self._fetch_limit is None:
            return self._max_first
        remaining = self._fetch_limit - self._fetched_count
        return min(remaining, self._max_first)

    async def _fetch_page(self, direction: str, page_size: int) -> Tuple[R, ...]:
        """Common fetch logic for pagination requests."""
        params = self._base_route.params.copy()
        if self.cursor:
            params[direction] = self.cursor
        params['first'] = page_size

        current_route = Route(
            self._base_route.method,
            self._base_route.path,
            base_url=self._base_route.base_url,
            **params
        )

        response = await self._request_func(current_route, **self._request_params)
        data = self._data_transform(response) if self._data_transform else tuple(response.get('data', []))
        pagination = response.get('pagination', {})
        self.cursor = pagination.get('cursor')

        return data

    async def next(self) -> Tuple[R, ...]:
        """
        Fetch the next page of items.

        Returns
        -------
        Tuple[R, ...]
            Tuple of items from the next page. Empty tuple if no more pages.
        """
        if self._done or (self._fetch_limit and self._fetched_count >= self._fetch_limit):
            self._done = True
            return ()

        page_size = self._calculate_page_size()
        if page_size <= 0:
            self._done = True
            return ()

        data = await self._fetch_page('after', page_size)
        self._fetched_count += len(data)

        if not self.cursor or not data or (self._fetch_limit and self._fetched_count >= self._fetch_limit):
            self._done = True

        return data

    async def before(self) -> Tuple[R, ...]:
        """
        Fetch the previous page of items.

        !!! warning

            Most Twitch API endpoints do not support backward pagination.
            This method is provided for completeness but may not work with all endpoints.

        Returns
        -------
        Tuple[R, ...]
            Tuple of items from the previous page.

        Raises
        ------
        BadRequest
            If the endpoint doesn't support backward pagination.

        Examples
        --------
        Backward pagination (if supported)::

            paginator = PaginatedRequest(http.get, route, max_first=50)
            previous_page = await paginator.before()
        """
        return await self._fetch_page('before', self._max_first)

    async def __call__(self) -> Tuple[R, ...]:
        """
        Fetch all available pages and return as a single tuple.

        Continues fetching pages until either no more data is available
        or the fetch_limit is reached.

        Returns
        -------
        Tuple[R, ...]
            All items from all fetched pages.

        Examples
        --------
        Fetch all available items::

            paginator = PaginatedRequest(http.get, route, max_first=100)
            all_items = await paginator()

        Fetch with limit::

            paginator = PaginatedRequest(http.get, route, max_first=100, fetch_limit=500)
            limited_items = await paginator()  # Max 500 items
        """
        all_items = []
        while not self._done:
            page_data = await self.next()
            if not page_data:
                break
            all_items.extend(page_data)
        return tuple(all_items)

    def __await__(self):
        """Allow the paginator to be awaited directly."""
        return self.__call__().__await__()

    def __aiter__(self) -> AsyncIterator[R]:
        """Return an async iterator for the paginator."""
        return self._iterate()

    async def _iterate(self) -> AsyncIterator[R]:
        """Async iterator yielding items one by one."""
        while not self._done:
            data = await self.next()
            for item in data:
                yield item


class RateLimitBucket:
    """Handles Twitch API token-bucket rate limiting for user tokens."""

    __slots__ = ('limit', 'remaining', 'reset_time', '_lock')

    def __init__(self) -> None:
        self.limit: int = 800
        self.remaining: int = 800
        self.reset_time: float = 0.0
        self._lock = asyncio.Lock()

    def update(self, response: aiohttp.ClientResponse) -> None:
        """Update rate limit info from Twitch response headers."""
        old_remaining = self.remaining
        self.limit = int(response.headers.get('Ratelimit-Limit', self.limit))
        self.remaining = int(response.headers.get('Ratelimit-Remaining', self.remaining))

        reset_header = response.headers.get('Ratelimit-Reset')
        if reset_header:
            self.reset_time = int(reset_header)

        reset_in = self.get_reset_after()
        _logger.debug(f"Rate limit: {old_remaining} -> {self.remaining}/{self.limit} (resets in {reset_in:.1f}s)")

    def get_reset_after(self) -> float:
        """Calculate seconds until reset."""
        if self.reset_time <= 0:
            return 0.0
        current_time = time.time()
        reset_after = max(0.0, self.reset_time - current_time)
        return reset_after

    def is_exhausted(self) -> bool:
        """Check if bucket is exhausted."""
        return self.remaining <= 0

    async def acquire(self, cost: int = 1) -> None:
        """Acquire points from the bucket, waiting if necessary."""
        async with self._lock:
            if self.remaining < cost:
                wait_time = self.get_reset_after()
                if wait_time > 0:
                    _logger.debug(
                        "Rate limit exhausted. Waiting %.2f seconds for reset...",
                        wait_time,
                    )
                    await asyncio.sleep(wait_time)
                    self.remaining = self.limit


class HTTPClient:
    """HTTP client for making Twitch API requests with multiple user access tokens."""

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            connector: Optional[aiohttp.BaseConnector] = None,
            *,
            proxy: Optional[str] = None,
            proxy_auth: Optional[aiohttp.BasicAuth] = None,
            http_trace: Optional[aiohttp.TraceConfig] = None,
            max_ratelimit_timeout: Optional[float] = None,
    ) -> None:
        self.connector: Optional[aiohttp.BaseConnector] = connector
        self.__session: Optional[aiohttp.ClientSession] = None

        self.client_id: str = client_id
        self.client_secret: str = client_secret

        # Token storage.
        self._tokens: Dict[str, Tuple[str, Optional[str]]] = {}
        self._token_scopes: Dict[str, Tuple[str, ...]] = {}
        self._tokens_validity: Dict[str, Tuple[float, float]] = {}

        self.mock_url: Optional[str] = None
        self.proxy: Optional[str] = proxy
        self.proxy_auth: Optional[aiohttp.BasicAuth] = proxy_auth
        self.http_trace: Optional[aiohttp.TraceConfig] = http_trace
        self.max_ratelimit_timeout: Optional[float] = max_ratelimit_timeout

        # Rate limit buckets per token.
        self._rate_limit_buckets: Dict[str, RateLimitBucket] = {}

        # User agent
        self.user_agent = f"twitch.py/{__version__} aiohttp/{aiohttp.__version__} (+{__url__})"

    def clear(self) -> None:
        if self.__session and self.__session.closed:
            self.__session = None

    async def ws_connect(self, url: str, *, compress: int = 0) -> aiohttp.ClientWebSocketResponse:
        kwargs = {
            'proxy': self.proxy,
            'proxy_auth': self.proxy_auth,
            'max_msg_size': 0,
            'timeout': 30.0,
            'autoclose': False,
            'headers': {
                'User-Agent': self.user_agent,
            },
            'compress': compress,
        }
        return await self.__session.ws_connect(url, **kwargs)

    def _ensure_bucket(self, user_id: str) -> RateLimitBucket:
        """Get or create rate limit bucket for a user."""
        if user_id not in self._rate_limit_buckets:
            self._rate_limit_buckets[user_id] = RateLimitBucket()
        return self._rate_limit_buckets[user_id]

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.__session:
            await self.__session.close()

    async def request(self, route: Route, *, user_id: Optional[str] = None, auth: bool = True, **kwargs: Any) -> Any:
        """Make an HTTP request."""
        method = route.method
        url = route.url

        headers = {'User-Agent': self.user_agent}

        if 'headers' in kwargs:
            headers.update(kwargs.pop('headers'))

        bucket = None

        if auth:
            if user_id not in self._tokens:
                raise TokenError(f"Missing token for User ID {user_id}")

            access_token, bucket = self._tokens[user_id][0], self._ensure_bucket(user_id)

            headers['Client-ID'] = self.client_id
            headers['Authorization'] = f"Bearer {access_token}"

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['json'] = kwargs.pop('json')

        kwargs['headers'] = headers

        if self.proxy:
            kwargs['proxy'] = self.proxy
        if self.proxy_auth:
            kwargs['proxy_auth'] = self.proxy_auth

        if bucket and bucket.is_exhausted():
            wait_time = bucket.get_reset_after()
            if wait_time > 0:
                _logger.debug("Rate limit exhausted. Waiting %.2f seconds before request...", wait_time)
                await asyncio.sleep(wait_time)
                bucket.remaining = bucket.limit

        for tries in range(5):
            try:
                async with self.__session.request(method, url, **kwargs) as response:
                    _logger.debug("%s %s returned %s", method, url, response.status)
                    data = await utils.json_or_text(response)
                    if bucket:
                        bucket.update(response)

                    if 200 <= response.status < 300:
                        _logger.debug("%s %s received %s", method, url, data)
                        return data

                    if response.status == 429:
                        remaining = int(response.headers.get('Ratelimit-Remaining', 0))
                        if remaining > 0:
                            raise RateLimited(response, data)
                        reset_time = response.headers.get("Ratelimit-Reset")
                        current_time = time.time()
                        retry_after = max(0.0, int(reset_time) - current_time) if reset_time else 60.0

                        _logger.warning("Real rate limit! Reset: %s, Current: %.0f, Retry after: %.2fs",
                                        reset_time, current_time, retry_after)

                        if self.max_ratelimit_timeout and retry_after > self.max_ratelimit_timeout:
                            raise RateLimited(response, data)

                        sleep_time = retry_after + 1.0
                        _logger.warning("Rate limited. Retrying in %.2f seconds. (attempt %d/5)",
                                        sleep_time, tries + 1)
                        await asyncio.sleep(sleep_time)

                        if bucket:
                            bucket.remaining = bucket.limit
                            _logger.debug(f"Bucket reset to {bucket.remaining}/{bucket.limit}")
                        continue

                    if response.status in {500, 502, 503, 504}:
                        await asyncio.sleep(1 + tries * 2)
                        continue
                    if response.status == 400:
                        raise BadRequest(response, data)
                    elif response.status == 401:
                        raise Unauthorized(response, data)
                    elif response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status == 409:
                        raise Conflict(response, data)
                    elif response.status >= 500:
                        raise TwitchServerError(response, data)
                    else:
                        raise HTTPException(response, data)

            except OSError as exc:
                if tries < 4 and exc.errno in {54, 10054}:
                    await asyncio.sleep(1 + tries * 2)
                    continue
                raise

        raise RuntimeError("Unreachable, All retries exhausted")

    def credentials_grant_flow(self) -> Response[ClientCredentials]:
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        route = Route.oauth2('POST', path='token')
        return self.request(route, auth=False, data=body)

    def device_code_request(self, scopes: Set[str]) -> Response[DeviceCode]:
        body = {
            'client_id': self.client_id,
            'scopes': ' '.join(scopes)
        }
        route = Route.oauth2('POST', path='device')
        return self.request(route, auth=False, data=body)

    def device_token_request(self, device_code: str) -> Response[Token]:
        body = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'device_code': device_code,
            'grant_type': 'urn:ietf:params:oauth:grant-type:device_code'
        }
        route = Route.oauth2('POST', path='token')
        return self.request(route, auth=False, data=body)

    def validate_token(self, token: str) -> Response[ValidateToken]:
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {token}'
        }
        route = Route.oauth2('GET', path='validate')
        return self.request(route, auth=False, headers=headers)

    def refresh_token(self, token: str) -> Response[Token]:
        body = {
            'grant_type': 'refresh_token',
            'refresh_token': token,
            'client_secret': self.client_secret,
            'client_id': self.client_id
        }
        route = Route.oauth2('POST', path='token')
        return self.request(route, auth=False, data=body)

    def revoke_token(self, token: str) -> Response[None]:
        body = {
            'token': token,
            'client_id': self.client_id
        }
        route = Route.oauth2('POST', path='revoke')
        return self.request(route, auth=False, data=body)


    @property
    def tokens(self) -> MappingProxyType[str, Tuple[str, Optional[str]]]:
        return MappingProxyType(self._tokens)

    @property
    def users_scopes(self) -> MappingProxyType[str, Tuple[str, ...]]:
        return MappingProxyType(self._token_scopes)

    @property
    def tokens_validity(self) -> MappingProxyType[str, Tuple[float, float]]:
        return MappingProxyType(self._tokens_validity)

    def get_token_quota(self, user_id: str) -> Optional[int]:
        bucket = self._rate_limit_buckets.get(user_id)
        return bucket.remaining if bucket is not None else None

    def add_token(self, *, user_id: str, access_token: str, refresh_token: Optional[str]) -> None:
        self._tokens[user_id] = (access_token, refresh_token)

    def remove_token(self, *, user_id: str) -> None:
        self._tokens.pop(user_id, None)
        self._token_scopes.pop(user_id, None)
        self._tokens_validity.pop(user_id, None)
        self._rate_limit_buckets.get(user_id, None)

    async def add_user(self,
                        *,
                        access_token: str,
                        refresh_token: Optional[str] = None
                        ) -> Tuple[str, Optional[Tuple[str, Optional[str]]]]:
        try:
            data = await self.validate_token(access_token)
            self._tokens_validity[data['user_id']] = (0.0, data['expires_in'])
            self._token_scopes[data['user_id']] = tuple(data['scopes']) if data['scopes'] else ()
            self.add_token(user_id=data['user_id'], access_token=access_token, refresh_token=refresh_token)
            return data['user_id'], None
        except Unauthorized as exc:
            if refresh_token is not None:
                try:
                    refresh_data = await self.refresh_token(refresh_token)
                    return await self.add_user(
                        access_token=refresh_data['access_token'],
                        refresh_token=refresh_data['refresh_token']
                    )
                except BadRequest:
                    raise AuthFailure("Invalid access token and refresh token") from exc
            raise AuthFailure("Improper access token has been passed") from exc

    async def authorize(self, token: Optional[str]) -> Tuple[str, Optional[Tuple[str, Optional[str]]]]:
        if self.__session is None or self.__session.closed:
            # Circular Import.
            from .eventsub.gateway import EventSubWebSocketResponse

            self.__session = aiohttp.ClientSession(
                connector=self.connector,
                ws_response_class=EventSubWebSocketResponse,
                trace_configs=None if self.http_trace is None else [self.http_trace]
            )

        if token:
            data = await self.validate_token(token)
            token_data = (token, None)
        else:
            data = await self.credentials_grant_flow()
            token_data = (data['access_token'], None)

        expires_in = data.get('expires_in', 3600)
        self._tokens_validity[self.client_id] = (0.0, expires_in)
        self.add_token(
            user_id=self.client_id,
            access_token=token_data[0],
            refresh_token=token_data[1]
        )

        return self.client_id, token_data

    async def maintain_tokens(
            self,
            *,
            validation_interval: float,
            refresh_threshold: float,
            min_wake: float,
            max_wake: float
    ) -> Tuple[float, Tuple[str, ...]]:
        now = time.time()
        next_wake = float('inf')
        updated_user_ids = set()

        for user_id in list(self._tokens.keys()):
            if not (token_data := self._tokens.get(user_id)):
                continue

            access_token, refresh_token = token_data
            last_validated, expires_in = self._tokens_validity.get(user_id, (0.0, 0.0))

            # Check if validation needed.
            age = now - last_validated
            if age >= validation_interval or user_id not in self._tokens_validity:
                try:
                    data = await self.validate_token(access_token)
                    expires_in = float(data['expires_in'])
                    self._tokens_validity[user_id] = (now, expires_in)
                    self._token_scopes[user_id] = tuple(data['scopes']) if data['scopes'] else ()
                    age = 0
                except Unauthorized:
                    expires_in = 0.0
                    self._tokens_validity[user_id] = (now, expires_in)
                    age = 0

            remaining = expires_in - age
            # Refresh if expiring soon.
            if 0 < remaining <= refresh_threshold:
                try:
                    if user_id == self.client_id:
                        # Client credentials flow
                        flow = await self.credentials_grant_flow()
                        new_expires = float(flow['expires_in'])
                        self._tokens_validity[user_id] = (now, new_expires)
                        self.add_token(user_id=user_id, access_token=flow['access_token'], refresh_token=None)
                        remaining = new_expires
                        _logger.info(f"Refreshed client token {user_id}")

                        # Track updated user ID
                        updated_user_ids.add(user_id)
                    else:
                        # User token refresh
                        if not refresh_token:
                            _logger.debug(f"Dropping token {user_id} - no refresh token")
                            self.remove_token(user_id=user_id)
                            updated_user_ids.add(user_id)
                            next_wake = min(next_wake, min_wake)
                            continue

                        flow = await self.refresh_token(refresh_token)
                        new_refresh = flow.get('refresh_token', refresh_token)
                        # Force validation on next wake-up cycle
                        self._tokens_validity[user_id] = (0.0, 0.0)
                        self.add_token(user_id=user_id, access_token=flow['access_token'], refresh_token=new_refresh)
                        remaining = 0.0
                        next_wake = min(next_wake, min_wake)
                        _logger.info(f"Refreshed user token {user_id}")

                        # Track updated user ID
                        updated_user_ids.add(user_id)

                except (BadRequest, Unauthorized) as e:
                    _logger.debug(f"Failed to refresh token {user_id}: {e}")
                    self.remove_token(user_id=user_id)
                    updated_user_ids.add(user_id)
                    next_wake = min(next_wake, min_wake)
                    continue

            if remaining > refresh_threshold:
                next_wake = min(next_wake, remaining - refresh_threshold)
            else:
                next_wake = min(next_wake, min_wake)

        final_wake_time = max(min(next_wake if next_wake != float('inf') else min_wake, max_wake), min_wake)
        return final_wake_time, tuple(updated_user_ids)

    def get_eventsub_subscriptions(
            self,
            user_id: str,
            /,
            status: Optional[str],
            subscriptions_type: Optional[str],
            subscription_user_id: Optional[str],
            subscription_id: Optional[str],
            fetch_limit: Optional[int],
    ) -> PaginatedRequest[EventsubSubscription, ...]:
        route = Route(
            'GET',
            'eventsub/subscriptions',
            status=status,
            type=subscriptions_type,
            user_id=subscription_user_id,
            id=subscription_id
        )
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def create_eventsub_subscription(
            self,
            user_id: str,
            /,
            subscription_type: str,
            subscription_version: str,
            subscription_condition: Dict[str, Any],
            transport: Dict[str, Any]
    ) -> Response[EventsubSubscription]:
        route = Route('POST', 'eventsub/subscriptions')
        if self.mock_url:
            route.base_url = self.mock_url
        body = {
            'type': subscription_type,
            'version': subscription_version,
            'condition': subscription_condition,
            'transport': transport
        }
        return self.request(route=route, json=body, user_id=user_id)

    def delete_eventsub_subscription(self, user_id: str, /, subscription_id: str) -> Response[None]:
        route = Route('DELETE','eventsub/subscriptions', id=subscription_id)
        return self.request(route=route, user_id=user_id)

    def start_commercial(self, broadcaster_id: str, length: int) -> Response[DataL[helix.StarCommercial]]:
        route = Route('POST', 'channels/commercial')
        body = {'broadcaster_id': broadcaster_id, 'length': length}
        return self.request(route=route, user_id=broadcaster_id, data=body)

    def get_cheermotes(self,
                       user_id: str,
                       /,
                       broadcaster_id: Optional[str]
                       ) -> Response[DataL[helix.Cheermote]]:
        route = Route('GET', 'bits/cheermotes', broadcaster_id=broadcaster_id)
        return self.request(route=route, user_id=user_id)

    def get_channel_emotes(self, user_id: str, /, broadcaster_id: str) -> Response[EmoteData[helix.ChannelEmote]]:
        route = Route('GET', 'chat/emotes', broadcaster_id=broadcaster_id)
        return self.request(route=route, user_id=user_id)

    def get_global_emotes(self, user_id: str, /) -> Response[EmoteData[helix.GlobalEmote]]:
        route = Route('GET', 'chat/emotes/global')
        return self.request(route=route, user_id=user_id)

    def get_emote_sets(self, user_id: str, /, emote_set_ids: Set[str]) -> Response[EmoteData[helix.EmoteSet]]:
        route = Route('GET', 'chat/emotes/set', emote_set_id=emote_set_ids)
        return self.request(route=route, user_id=user_id)

    def get_channel_chat_badges(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.ChatBadgeSet]]:
        route = Route('GET', 'chat/badges', broadcaster_id=broadcaster_id)
        return self.request(route=route, user_id=user_id)

    def get_global_chat_badges(self, user_id: str, /) -> Response[DataL[helix.ChatBadgeSet]]:
        route = Route('GET', 'chat/badges/global')
        return self.request(route=route, user_id=user_id)

    def get_chat_settings(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.ChatSettings]]:
        route = Route('GET', 'chat/settings', broadcaster_id=broadcaster_id, moderator_id=user_id)
        return self.request(route=route, user_id=user_id)

    def get_shared_chat_session(self,
                                user_id: str,
                                /,
                                broadcaster_id: str
                                ) -> Response[DataL[helix.SharedChatSession]]:
        route = Route('GET', 'shared_chat/session', broadcaster_id=broadcaster_id)
        return self.request(route=route, user_id=user_id)


    def send_chat_message(self,
                          user_id: str,
                          /,
                          broadcaster_id: str,
                          sender_id: str,
                          message: str,
                          reply_parent_message_id: Optional[str],
                          for_source_only: Optional[bool]
                          ) -> Response[DataL[helix.SendMessageStatus]]:
        route = Route('POST', 'chat/messages')
        body: Dict[str, Any] = {
            'broadcaster_id': broadcaster_id,
            'sender_id': sender_id,
            'message': message,
        }
        if reply_parent_message_id:
            body['reply_parent_message_id'] = reply_parent_message_id
        if for_source_only is not None:
            body['for_source_only'] = for_source_only
        return self.request(route=route, user_id=user_id, data=body)

    def get_user_chat_color(self,
                            user_id: str,
                            /,
                            user_ids: Set[str]
                            ) -> Response[DataL[helix.UserChatColor]]:
        route = Route('GET', 'chat/color', user_id=user_ids)
        return self.request(route=route, user_id=user_id)

    def get_channel_information(self,
                                user_id: str,
                                /,
                                broadcaster_ids: Set[str]
                                ) -> Response[DataL[helix.ChannelInformation]]:
        route = Route('GET', 'channels', broadcaster_id=broadcaster_ids)
        return self.request(route=route, user_id=user_id)

    def get_channel_teams(self, user_id: str, /,  broadcaster_id: str) -> Response[DataL[helix.ChannelTeam]]:
        route = Route('GET', 'teams/channel', broadcaster_id=broadcaster_id)
        return self.request(route=route, user_id=user_id)

    def get_teams(self,
                 user_id: str,
                 /,
                 team_id: Optional[str],
                 team_name: Optional[str]
                 ) -> Response[DataL[helix.TeamUsers]]:
        route = Route('GET', 'teams', id=team_id, name=team_name)
        return self.request(route=route, user_id=user_id)

    def get_users(self,
                 user_id: str,
                 /,
                 user_ids: Set[str],
                 user_logins: Set[str]
                 ) -> Response[DataL[helix.UserInfo]]:
        route = Route('GET', 'users', id=user_ids, login=user_logins)
        return self.request(route=route, user_id=user_id)

    def get_top_games(self,
                      user_id: str,
                      /,
                      fetch_limit: Optional[int]
                      ) -> PaginatedRequest[PData[helix.Game], ...]:
        route = Route('GET', 'games/top')
        return PaginatedRequest(self.request, route=route, user_id=user_id, max_first=100, fetch_limit=fetch_limit)

    def get_games(self,
                  user_id: str,
                  /,
                  game_ids: Set[str],
                  game_names: Set[str],
                  igdb_ids: Set[str]
                  ) -> Response[DataL[helix.Game]]:
        route = Route('GET', 'games', id=game_ids, name=game_names, igdb_id=igdb_ids)
        return self.request(route=route, user_id=user_id)

    def search_categories(self,
                          user_id: str,
                          /,
                          query: str,
                          fetch_limit: Optional[int]
                          ) -> PaginatedRequest[PData[helix.Category], ...]:
        route = Route('GET', 'search/categories', query=query)
        return PaginatedRequest(self.request, route=route, user_id=user_id, max_first=100, fetch_limit=fetch_limit)


    def search_channels(self,
                          user_id: str,
                          /,
                          query: str,
                          live_only: bool,
                          fetch_limit: Optional[int]
                          ) -> PaginatedRequest[PData[helix.SearchChannel], ...]:
        route = Route('GET', 'search/channels', query=query, live_only=live_only)
        return PaginatedRequest(self.request, route=route, user_id=user_id, max_first=100, fetch_limit=fetch_limit)

    def get_clips(self,
                  user_id: str,
                  /,
                  broadcaster_id: Optional[str],
                  game_id: Optional[str],
                  clip_ids: Set[str],
                  started_at: Optional[str] ,
                  ended_at: Optional[str],
                  is_featured: Optional[bool],
                  fetch_limit: Optional[int]
                  ) -> PaginatedRequest[PData[helix.Clip], ...]:
        route = Route('GET', 'clips',
                      broadcaster_id=broadcaster_id,
                      game_id=game_id,
                      id=clip_ids,
                      started_at=started_at,
                      ended_at=ended_at,
                      is_featured=is_featured)
        return PaginatedRequest(
            self.request,
            route=route,
            user_id=user_id,
            max_first=100,
            fetch_limit=fetch_limit
        )

    def get_videos(self,
                   user_id: str,
                   /,
                   video_ids: Set[str],
                   video_user_id: Optional[str],
                   game_id: Optional[str],
                   language: Optional[str],
                   period: Optional[str],
                   sort: Optional[str],
                   video_type: Optional[str],
                   fetch_limit: Optional[int]
                   ) -> PaginatedRequest[PData[helix.Video], ...]:
        route = Route('GET', 'videos',
                      id=video_ids,
                      user_id=video_user_id,
                      game_id=game_id,
                      language=language,
                      period=period,
                      sort=sort,
                      type=video_type)
        return PaginatedRequest(
            self.request,
            route=route,
            user_id=user_id,
            max_first=100,
            fetch_limit=fetch_limit
        )

    def get_streams(self,
                    user_id: str,
                    /,
                    user_ids: Set[str],
                    user_logins: Set[str],
                    game_ids: Set[str],
                    stream_type: Optional[str],
                    languages: Set[str],
                    fetch_limit: Optional[int]
                   ) -> PaginatedRequest[PData[helix.StreamInfo], ...]:
        route = Route('GET', 'streams',
                      user_id=user_ids,
                      user_login=user_logins,
                      game_id=game_ids,
                      type=stream_type,
                      language=languages
                      )
        return PaginatedRequest(
            self.request,
            route=route,
            user_id=user_id,
            max_first=100,
            fetch_limit=fetch_limit
        )

    def get_content_classification_labels(self,
                                          user_id: Optional[str],
                                          /,
                                          locale: str) -> Response[DataL[helix.ContentClassificationLabel]]:
        route = Route('GET', 'content_classification_labels', locale=locale)
        return self.request(route=route, user_id=user_id)

    def get_channel_stream_schedule(self,
                                    user_id: str,
                                    /,
                                    broadcaster_id: str,
                                    segment_ids: Set[str],
                                    start_time: Optional[str],
                                    fetch_limit: Optional[int]
                                    ) -> PaginatedRequest[PData[helix.ChannelStreamSchedule], ...]:
        route = Route(
            'GET',
            path='schedule',
            broadcaster_id=broadcaster_id,
            id=segment_ids,
            start_time=start_time
        )

        return PaginatedRequest(
            self.request,
            route=route,
            user_id=user_id,
            max_first=25,
            fetch_limit=fetch_limit
        )

    def get_drops_entitlements(self,
                               user_id: str,
                               /,
                               entitlement_ids: Set[str],
                               target_user_id: Optional[str],
                               game_id: Optional[str],
                               fulfillment_status: Optional[str],
                               fetch_limit: Optional[int]
                               ) -> PaginatedRequest[PData[helix.DropsEntitlement], ...]:
        route = Route(
            'GET',
            path='entitlements/drops',
            id=entitlement_ids,
            user_id=target_user_id,
            game_id=game_id,
            fulfillment_status=fulfillment_status
        )
        return PaginatedRequest(
            self.request,
            route=route,
            user_id=user_id,
            max_first=1000,
            fetch_limit=fetch_limit
        )

    def update_drops_entitlements(self,
                                  user_id: str,
                                  /,
                                  entitlement_ids: Set[str],
                                  fulfillment_status: Optional[str]
                                  ) -> Response[DataL[helix.DropsEntitlementUpdate]]:
        route = Route('PATCH', 'entitlements/drops')
        body = {
            'entitlement_ids': list(entitlement_ids),
            'fulfillment_status': fulfillment_status
        }
        return self.request(route=route, user_id=user_id, data=body)

    def get_conduits(self, user_id: str) -> Response[DataL[helix.Conduit]]:
        route = Route('GET', 'eventsub/conduits')
        return self.request(route=route, user_id=user_id)

    def create_conduit(self, user_id: str, /, shard_count: int) -> Response[DataL[helix.Conduit]]:
        body = {'shard_count': shard_count}
        route = Route('POST', 'eventsub/conduits')
        return self.request(route=route, user_id=user_id, data=body)

    def update_conduit(self,
                       user_id: str,
                       /,
                       conduit_id: str,
                       shard_count: int
                       ) -> Response[DataL[helix.Conduit]]:
        body = {'id': conduit_id, 'shard_count': shard_count}
        route = Route('POST', 'eventsub/conduits')
        return self.request(route=route, user_id=user_id, data=body)

    def delete_conduit(self, user_id: str, /, conduit_id: str) -> Response[None]:
        route = Route('DELETE', 'eventsub/conduits', id=conduit_id)
        return self.request(route=route, user_id=user_id)

    def get_conduit_shards(self,
                           user_id: str,
                           /,
                           conduit_id: str,
                           status: str,
                           fetch_limit: Optional[int]
                           ) -> PaginatedRequest[PData[helix.ConduitShard], ...]:
        route = Route(
            'GET',
            path='eventsub/conduits/shards',
            conduit_id=conduit_id,
            status=status,
        )
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def update_conduit_shards(self,
                              user_id: str,
                              /,
                              conduit_id: str,
                              shards: Tuple[Dict[str, Any], ...]
                              )  -> Response[helix.UpdateConduitShards]:
        body = {
            'conduit_id': conduit_id,
            'shards': list(shards)
        }
        route = Route('PATCH', path='eventsub/conduits/shards')
        return self.request(route=route, user_id=user_id, json=body)

    def get_extension_transactions(self,
                                   user_id: str,
                                   extension_id: str,
                                   transaction_ids: Set[str],
                                   fetch_limit: Optional[int]
                                   ) -> PaginatedRequest[PData[helix.ExtensionTransaction], ...]:
        route = Route('GET', 'extensions/transactions', extension_id=extension_id, id=transaction_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_extension_bits_products(self,
                                    user_id: str,
                                    /,
                                    extension_id: str,
                                    should_include_all: bool
                                    )-> Response[DataL[helix.ExtensionBitsProduct]]:
        route = Route(
            'GET',
            'bits/extensions',
            extension_id=extension_id,
            should_include_all=should_include_all
        )
        return self.request(route, user_id=user_id)

    def update_extension_bits_product(self,
                                      user_id: str,
                                      /,
                                      extension_id: str,
                                      sku: str,
                                      cost: Dict[str, Any],
                                      name: str, in_development: bool,
                                      display_name: Optional[str],
                                      expiration: Optional[str],
                                      is_broadcast: bool
                                      ) -> Response[DataL[helix.ExtensionBitsProduct]]:
        route = Route('PUT', 'bits/extensions', extension_id=extension_id)
        body = {
            'sku': sku,
            'cost': cost,
            'name': name,
            'in_development': in_development,
            'display_name': display_name,
            'expiration': expiration,
            'is_broadcast': is_broadcast
        }
        return self.request(route, user_id=user_id, json=body)

    def get_released_extensions(self,
                                user_id: str,
                                extension_id: str,
                                extension_version: Optional[str]
                                ) -> Response[DataL[helix.Extension]]:
        route = Route(
            'GET',
            'extensions/released',
            extension_id=extension_id,
            extension_version=extension_version
        )
        return self.request(route, user_id=user_id)

    def send_extension_pubsub_message(self,
                                      user_id: str,
                                      /,
                                      extension_id: str,
                                      target: List[str],
                                      is_global_broadcast: bool,
                                      message: str
                                      ) -> Response[None]:
        route = Route('POST', 'extensions/pubsub')
        body = {
            'extension_id': extension_id,
            'target': target,
            'is_global_broadcast': is_global_broadcast,
            'message': message
        }
        return self.request(route, user_id=user_id, json=body)

    def get_extensions(self,
                       user_id: str,
                       /,
                       extension_id: str,
                       extension_version: Optional[str]
                       ) -> Response[DataL[helix.Extension]]:
        route = Route(
            'GET',
            'extensions',
            extension_id=extension_id,
            extension_version=extension_version
        )
        return self.request(route, user_id=user_id)

    def get_ad_schedule(self,
                        user_id: str,
                        /,
                        broadcaster_id: str
                        ) -> PaginatedRequest[PData[helix.AdSchedule], ...]:
        route = Route('GET', 'channels/ads', broadcaster_id=broadcaster_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, max_first=1)

    def snooze_next_ad(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.AdSnooze]]:
        route = Route('POST', 'channels/ads/schedule/snooze', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def get_extension_analytics(self,
                                user_id: str,
                                /,
                                extension_id: Optional[str],
                                report_type: Optional[str],
                                started_at: Optional[str],
                                ended_at: Optional[str],
                                fetch_limit: Optional[int]
                                ) -> PaginatedRequest[PData[helix.AnalyticsReport], ...]:
        route = Route('GET', 'analytics/extensions', extension_id=extension_id, type=report_type,
                      started_at=started_at, ended_at=ended_at)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_game_analytics(self,
                           user_id: str,
                           /,
                           game_id: Optional[str],
                           report_type: Optional[str],
                           started_at: Optional[str],
                           ended_at: Optional[str],
                           fetch_limit: Optional[int]
                           ) ->  PaginatedRequest[PData[helix.AnalyticsReport], ...]:
        route = Route('GET', 'analytics/games', game_id=game_id, type=report_type, started_at=started_at,
                      ended_at=ended_at)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_bits_leaderboard(self,
                             user_id: str,
                             /,
                             count: int,
                             period: str,
                             started_at: Optional[str],
                             user_id_filter: Optional[str]
                             ) -> Response[DataL[helix.BitsLeaderboardEntry]]:
        route = Route('GET', 'bits/leaderboard', count=count, period=period, started_at=started_at,
                      user_id=user_id_filter)
        return self.request(route, user_id=user_id)

    def get_charity_campaign(self,
                             user_id: str,
                             /,
                             broadcaster_id: str
                             ) -> Response[DataL[helix.CharityCampaign]]:
        route = Route('GET', 'charity/campaigns', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def get_charity_campaign_donations(self,
                                       user_id: str,
                                       /,
                                       broadcaster_id: str,
                                       fetch_limit: Optional[int]
                                       ) -> PaginatedRequest[PData[helix.CharityDonation], ...]:
        route = Route('GET', 'charity/donations', broadcaster_id=broadcaster_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_chatters(self,
                     user_id: str,
                     /,
                     broadcaster_id: str,
                     moderator_id: str,
                     fetch_limit: Optional[int]
                     ) -> PaginatedRequest[PData[helix.BaseUser], ...]:
        route = Route('GET', 'chat/chatters', broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=1000)

    def update_chat_settings(self,
                             user_id: str,
                             /,
                             broadcaster_id: str,
                             moderator_id: str,
                             settings: Dict[str, Any]
                             ) -> Response[DataL[helix.ChatSettings]]:
        route = Route('PATCH', 'chat/settings', broadcaster_id=broadcaster_id, moderator_id=moderator_id)
        return self.request(route, user_id=user_id, json=settings)

    def send_chat_announcement(self,
                               user_id: str,
                               /,
                               broadcaster_id: str,
                               moderator_id: str,
                               message: str,
                               color: str
                               ) -> Response[None]:
        route = Route(
            'POST',
            'chat/announcements',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        body = {'message': message, 'color': color}
        return self.request(route, user_id=user_id, json=body)

    def send_shoutout(self,
                      user_id: str,
                      /,
                      from_broadcaster_id: str,
                      to_broadcaster_id: str,
                      moderator_id: str
                      ) -> Response[None]:
        route = Route('POST', 'chat/shoutouts', from_broadcaster_id=from_broadcaster_id,
                      to_broadcaster_id=to_broadcaster_id, moderator_id=moderator_id)
        return self.request(route, user_id=user_id)

    def update_user_chat_color(self, user_id: str, /, color: str) -> Response[None]:
        route = Route('PUT', 'chat/color', user_id=user_id, color=color)
        return self.request(route, user_id=user_id)

    def delete_chat_messages(self,
                             user_id: str,
                             /,
                             broadcaster_id: str,
                             moderator_id: str,
                             message_id: Optional[str]
                             ) -> Response[None]:
        route = Route(
            'DELETE',
            'moderation/chat',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id,
            message_id=message_id
        )
        return self.request(route, user_id=user_id)

    def warn_chat_user(self,
                       user_id: str,
                       /,
                       broadcaster_id: str,
                       moderator_id: str,
                       user_id_warn: str,
                       reason: str
                       ) -> Response[DataL[helix.WarnReason]]:
        route = Route(
            'POST',
            'moderation/warnings',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        body = {'user_id': user_id_warn, 'reason': reason}
        return self.request(route, user_id=user_id, json=body)

    def create_clip(self, user_id: str, /, broadcaster_id: str, has_delay: bool) -> Response[DataL[helix.Clip]]:
        route = Route('POST', 'clips', broadcaster_id=broadcaster_id, has_delay=has_delay)
        return self.request(route, user_id=user_id)

    def get_creator_goals(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.CreatorGoal]]:
        route = Route('GET', 'goals', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def get_hype_train_events(self,
                              user_id: str,
                              /,
                              broadcaster_id: str,
                              fetch_limit: Optional[int]
                              ) ->  PaginatedRequest[PData[helix.HypeTrainEvent], ...]:
        route = Route('GET', 'hypetrain/events', broadcaster_id=broadcaster_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def check_automod_status(self,
                             user_id: str,
                             /,
                             broadcaster_id: str,
                             messages: List[Dict[str, Any]]
                             ) -> Response[DataL[helix.AutoModStatusMessage]]:
        route = Route('POST', 'moderation/enforcements/status', broadcaster_id=broadcaster_id)
        body = {'data': messages}
        return self.request(route, user_id=user_id, json=body)

    def manage_held_automod_messages(self, user_id: str, /, msg_id: str, action: str) -> Response[None]:
        route = Route('POST', 'moderation/automod/message')
        body = {'user_id': user_id, 'msg_id': msg_id, 'action': action}
        return self.request(route, user_id=user_id, json=body)

    def get_automod_settings(self,
                             user_id: str,
                             /,
                             broadcaster_id: str,
                             moderator_id: str
                             ) -> Response[DataL[helix.AutoModSettings]]:
        route = Route('GET', 'moderation/automod/settings', broadcaster_id=broadcaster_id,
                      moderator_id=moderator_id)
        return self.request(route, user_id=user_id)

    def update_automod_settings(self,
                                user_id: str,
                                /,
                                broadcaster_id: str,
                                moderator_id: str,
                                settings: Dict[str, Any]
                                ) -> Response[DataL[helix.AutoModSettings]]:
        route = Route('PUT', 'moderation/automod/settings', broadcaster_id=broadcaster_id,
                      moderator_id=moderator_id)
        return self.request(route, user_id=user_id, json=settings)

    def get_banned_users(self,
                         user_id: str,
                         /,
                         broadcaster_id: str,
                         moderator_id: str,
                         user_ids: Set[str],
                         fetch_limit: Optional[int]
                         ) -> PaginatedRequest[PData[helix.BannedUser], ...]:
        route = Route(
            'GET', 
            'moderation/banned',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id,
            user_id=user_ids
        )
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def ban_user(self,
                 user_id: str,
                 /,
                 broadcaster_id: str,
                 moderator_id: str,
                 user_id_ban: str,
                 duration: Optional[int],
                 reason: str
                 ) -> Response[DataL[helix.BannedUser]]:
        route = Route(
            'POST',
            'moderation/bans',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        body = {'data': {'user_id': user_id_ban, 'duration': duration, 'reason': reason}}
        return self.request(route, user_id=user_id, json=body)

    def unban_user(self,
                   user_id: str,
                   /,
                   broadcaster_id: str,
                   moderator_id: str,
                   user_id_unban: str
                   ) -> Response[None]:
        route = Route(
            'DELETE',
            'moderation/bans',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id,
            user_id=user_id_unban
        )
        return self.request(route, user_id=user_id)

    def get_unban_requests(self,
                           user_id: str,
                           /,
                           broadcaster_id: str,
                           moderator_id: str,
                           status: str,
                           user_id_filter: Optional[str],
                           fetch_limit: Optional[int]
                           ) -> PaginatedRequest[PData[helix.UnbanRequest], ...]:
        route = Route(
            'GET',
            'moderation/unban_requests',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id,
            status=status,
            user_id=user_id_filter
        )
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def resolve_unban_request(self,
                              user_id: str,
                              /,
                              broadcaster_id: str,
                              moderator_id: str,
                              unban_request_id: str,
                              status: str,
                              resolution_text: Optional[str]
                              ) -> Response[DataL[helix.UnbanRequest]]:
        route = Route('PATCH', 'moderation/unban_requests', broadcaster_id=broadcaster_id,
                      moderator_id=moderator_id, unban_request_id=unban_request_id)
        body = {'status': status, 'resolution_text': resolution_text}
        return self.request(route, user_id=user_id, json=body)

    def get_blocked_terms(self,
                          user_id: str,
                          /,
                          broadcaster_id: str,
                          moderator_id: str,
                          fetch_limit: Optional[int]
                          ) -> PaginatedRequest[PData[helix.BlockedTerm], ...]:
        route = Route(
            'GET',
            'moderation/blocked_terms',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def add_blocked_term(self,
                         user_id: str,
                         /,
                         broadcaster_id: str,
                         moderator_id: str,
                         text: str) -> Response[DataL[helix.BlockedTerm]]:
        route = Route(
            'POST',
            'moderation/blocked_terms',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        body = {'text': text}
        return self.request(route, user_id=user_id, json=body)

    def remove_blocked_term(self,
                            user_id: str,
                            /,
                            broadcaster_id: str,
                            moderator_id: str,
                            term_id: str) -> Response[None]:
        route = Route('DELETE', 'moderation/blocked_terms', broadcaster_id=broadcaster_id,
                      moderator_id=moderator_id, id=term_id)
        return self.request(route, user_id=user_id)

    def get_moderators(self,
                       user_id: str,
                       /,
                       broadcaster_id: str,
                       user_ids: Set[str],
                       fetch_limit: Optional[int]
                       ) -> PaginatedRequest[PData[helix.Moderator], ...]:
        route = Route('GET', 'moderation/moderators', broadcaster_id=broadcaster_id, user_id=user_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def add_channel_moderator(self, user_id: str, /, broadcaster_id: str, user_id_mod: str) -> Response[None]:
        route = Route(
            'POST',
            'moderation/moderators',
            broadcaster_id=broadcaster_id,
            user_id=user_id_mod
        )
        return self.request(route, user_id=user_id)

    def remove_channel_moderator(self, user_id: str, /, broadcaster_id: str, user_id_mod: str) -> Response[None]:
        route = Route(
            'DELETE',
            'moderation/moderators',
            broadcaster_id=broadcaster_id,
            user_id=user_id_mod
        )
        return self.request(route, user_id=user_id)

    def get_vips(self,
                 user_id: str,
                 /,
                 broadcaster_id: str,
                 user_ids: Set[str],
                 fetch_limit: Optional[int]
                 ) -> PaginatedRequest[PData[helix.BaseUser], ...]:
        route = Route('GET', 'channels/vips', broadcaster_id=broadcaster_id, user_id=user_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def add_channel_vip(self, user_id: str, /, broadcaster_id: str, user_id_vip: str) -> Response[None]:
        route = Route('POST', 'channels/vips', broadcaster_id=broadcaster_id, user_id=user_id_vip)
        return self.request(route, user_id=user_id)

    def remove_channel_vip(self, user_id: str, /, broadcaster_id: str, user_id_vip: str) -> Response[None]:
        route = Route('DELETE', 'channels/vips', broadcaster_id=broadcaster_id, user_id=user_id_vip)
        return self.request(route, user_id=user_id)

    def update_shield_mode_status(self,
                                  user_id: str,
                                  /,
                                  broadcaster_id: str,
                                  moderator_id: str,
                                  is_active: bool
                                  ) -> Response[DataL[helix.ShieldModeStatus]]:
        route = Route(
            'PUT',
            'moderation/shield_mode',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        body = {'is_active': is_active}
        return self.request(route, user_id=user_id, json=body)

    def get_shield_mode_status(self,
                               user_id: str,
                               /,
                               broadcaster_id: str,
                               moderator_id: str
                               ) -> Response[DataL[helix.ShieldModeStatus]]:
        route = Route(
            'GET',
            'moderation/shield_mode',
            broadcaster_id=broadcaster_id,
            moderator_id=moderator_id
        )
        return self.request(route, user_id=user_id)

    def get_polls(self,
                  user_id: str,
                  /,
                  broadcaster_id: str,
                  poll_ids: Set[str],
                  fetch_limit: Optional[int]
                  ) -> PaginatedRequest[PData[helix.Poll], ...]:
        route = Route('GET', 'polls', broadcaster_id=broadcaster_id, id=poll_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=20)

    def create_poll(self,
                    user_id: str,
                    /,
                    broadcaster_id: str,
                    title: str,
                    choices: List[str],
                    duration: int,
                    bits_voting_enabled: bool,
                    bits_per_vote: int,
                    channel_points_voting_enabled: bool,
                    channel_points_per_vote: int
                    ) -> Response[DataL[helix.Poll]]:
        route = Route('POST', 'polls', broadcaster_id=broadcaster_id)
        body = {
            'title': title,
            'choices': [{'title': choice} for choice in choices],
            'duration': duration,
            'bits_voting_enabled': bits_voting_enabled,
            'bits_per_vote': bits_per_vote,
            'channel_points_voting_enabled': channel_points_voting_enabled,
            'channel_points_per_vote': channel_points_per_vote
        }
        return self.request(route, user_id=user_id, json=body)

    def end_poll(self,
                 user_id: str,
                 /,
                 broadcaster_id: str,
                 poll_id: str,
                 status: str
                 ) -> Response[DataL[helix.Poll]]:
        route = Route('PATCH', 'polls', broadcaster_id=broadcaster_id, id=poll_id, status=status)
        return self.request(route, user_id=user_id)

    def get_predictions(self,
                        user_id: str,
                        /,
                        broadcaster_id: str,
                        prediction_ids: Set[str],
                        fetch_limit: Optional[int]
                        ) -> PaginatedRequest[PData[helix.Prediction], ...]:
        route = Route('GET', 'predictions', broadcaster_id=broadcaster_id, id=prediction_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=20)

    def create_prediction(self,
                          user_id: str,
                          /,
                          broadcaster_id: str,
                          title: str,
                          outcomes: List[str],
                          duration: int
                          ) -> Response[DataL[helix.Prediction]]:
        route = Route('POST', 'predictions', broadcaster_id=broadcaster_id)
        body = {
            'title': title,
            'outcomes': [{'title': outcome} for outcome in outcomes],
            'prediction_window': duration
        }
        return self.request(route, user_id=user_id, json=body)

    def end_prediction(self,
                       user_id: str,
                       /,
                       broadcaster_id: str,
                       prediction_id: str,
                       status: str,
                       winning_outcome_id: Optional[str]
                       ) -> Response[DataL[helix.Prediction]]:
        route = Route(
            'PATCH',
            'predictions',
            broadcaster_id=broadcaster_id,
            id=prediction_id,
            status=status,
            winning_outcome_id=winning_outcome_id
        )
        return self.request(route, user_id=user_id)

    def start_raid(self,
                   user_id: str,
                   /,
                   from_broadcaster_id: str,
                   to_broadcaster_id: str
                   ) -> Response[DataL[helix.Raid]]:
        route = Route(
            'POST',
            'raids',
            from_broadcaster_id=from_broadcaster_id,
            to_broadcaster_id=to_broadcaster_id
        )
        return self.request(route, user_id=user_id)

    def cancel_raid(self, user_id: str, /, broadcaster_id: str) -> Response[None]:
        route = Route('DELETE', 'raids', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def update_channel_stream_schedule(self,
                                       user_id: str,
                                       /,
                                       broadcaster_id: str,
                                       is_vacation_enabled: bool,
                                       vacation_start_time: Optional[str],
                                       vacation_end_time: Optional[str],
                                       timezone: Optional[str]
                                       ) -> Response[None]:
        route = Route('PATCH', 'schedule/settings', broadcaster_id=broadcaster_id)
        body = {
            'is_vacation_enabled': is_vacation_enabled,
            'vacation_start_time': vacation_start_time,
            'vacation_end_time': vacation_end_time,
            'timezone': timezone
        }
        return self.request(route, user_id=user_id, json=body)

    def create_channel_stream_schedule_segment(self,
                                               user_id: str,
                                               /,
                                               broadcaster_id: str,
                                               start_time: str,
                                               timezone: str,
                                               is_recurring: bool,
                                               duration: Optional[int],
                                               category_id: Optional[str],
                                               title: Optional[str]
                                               ) -> Response[Data[helix.ChannelStreamSchedule]]:
        route = Route('POST', 'schedule/segment', broadcaster_id=broadcaster_id)
        body = {
            'start_time': start_time,
            'timezone': timezone,
            'is_recurring': is_recurring,
            'duration': duration,
            'category_id': category_id,
            'title': title
        }
        return self.request(route, user_id=user_id, json=body)

    def update_channel_stream_schedule_segment(self,
                                               user_id: str,
                                               /,
                                               broadcaster_id: str,
                                               segment_id: str,
                                               start_time: Optional[str],
                                               duration: Optional[int],
                                               category_id: Optional[str],
                                               is_canceled: Optional[bool],
                                               timezone: Optional[str],
                                               title: Optional[str]
                                               ) -> Response[Data[helix.ChannelStreamSchedule]]:
        route = Route('PATCH', 'schedule/segment', broadcaster_id=broadcaster_id, id=segment_id)
        body = {
            'start_time': start_time,
            'duration': duration,
            'category_id': category_id,
            'is_canceled': is_canceled,
            'timezone': timezone,
            'title': title
        }
        return self.request(route, user_id=user_id, json=body)

    def delete_channel_stream_schedule_segment(self,
                                               user_id: str,
                                               /,
                                               broadcaster_id: str,
                                               segment_id: str
                                               ) -> Response[None]:
        route = Route('DELETE', 'schedule/segment', broadcaster_id=broadcaster_id, id=segment_id)
        return self.request(route, user_id=user_id)

    def create_stream_marker(self,
                             user_id: str,
                             /,
                             user_id_create: str,
                             description: Optional[str]
                             ) -> Response[DataL[helix.StreamMarker]]:
        route = Route('POST', 'streams/markers')
        body = {'user_id': user_id_create, 'description': description}
        return self.request(route, user_id=user_id, json=body)

    def get_stream_markers(self,
                           user_id: str,
                           /,
                           user_id_mark: Optional[str],
                           video_id: Optional[str],
                           fetch_limit: Optional[int]
                           ) -> PaginatedRequest[PData[helix.StreamMarker], ...]:
        route = Route('GET', 'streams/markers', user_id=user_id_mark, video_id=video_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_broadcaster_subscriptions(self,
                                      user_id: str,
                                      /,
                                      broadcaster_id: str,
                                      user_ids: Set[str],
                                      fetch_limit: Optional[int]
                                      ) -> PaginatedRequest[PData[helix.UserSubscription], ...]:
        route = Route('GET', 'subscriptions', broadcaster_id=broadcaster_id, user_id=user_ids)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def check_user_subscription(self,
                                user_id: str,
                                /,
                                broadcaster_id: str,
                                user_id_check: str
                                ) -> Response[DataL[helix.UserSubscription]]:
        route = Route('GET', 'subscriptions/user', broadcaster_id=broadcaster_id, user_id=user_id_check)
        return self.request(route, user_id=user_id)

    def update_user(self,
                    user_id: str,
                    /,
                    description: Optional[str]
                    ) -> Response[DataL[helix.UserInfo]]:
        route = Route('PUT', 'users', description=description)
        return self.request(route, user_id=user_id)

    def get_user_block_list(self,
                            user_id: str,
                            /,
                            broadcaster_id: str,
                            fetch_limit: Optional[int]
                            ) -> PaginatedRequest[PData[helix.BaseUser], ...]:
        route = Route('GET', 'users/blocks', broadcaster_id=broadcaster_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def block_user(self,
                   user_id: str,
                   /,
                   target_user_id: str,
                   source_context: Optional[str],
                   reason: Optional[str]) -> Response[None]:
        route = Route(
            'PUT',
            'users/blocks',
            target_user_id=target_user_id,
            source_context=source_context,
            reason=reason
        )
        return self.request(route, user_id=user_id)

    def unblock_user(self, user_id: str, /, target_user_id: str) -> Response[None]:
        route = Route('DELETE', 'users/blocks', target_user_id=target_user_id)
        return self.request(route, user_id=user_id)

    def get_user_extensions(self, user_id: str, /,) -> Response[DataL[helix.UserExtension]]:
        route = Route('GET', 'users/extensions/list')
        return self.request(route, user_id=user_id)

    def get_user_active_extensions(self,
                                   user_id: str,
                                   /,
                                   user_id_ext: Optional[str
                                   ]) -> Response[Data[helix.ActiveUserExtension]]:
        route = Route('GET', 'users/extensions', user_id=user_id_ext)
        return self.request(route, user_id=user_id)

    def update_user_extensions(self,
                               user_id: str, /,
                               data: Dict[str, Any]
                               ) -> Response[Data[helix.UserActiveExtensionUpdate]]:
        route = Route('PUT', 'users/extensions')
        return self.request(route, user_id=user_id, json=data)

    def get_extension_live_channels(self,
                                    user_id: str, /,
                                    extension_id: str,
                                    fetch_limit: Optional[int]
                                    ) -> PaginatedRequest[PData[helix.ExtensionLiveChannel], ...]:
        route = Route('GET', 'extensions/live', extension_id=extension_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_extension_channel_configuration(self,
                                            user_id: str, /,
                                            broadcaster_id: str,
                                            extension_id: str) -> Response[PData[helix.ExtensionConfiguration]]:
        route = Route(
            'GET',
            'extensions/configurations',
            broadcaster_id=broadcaster_id,
            extension_id=extension_id
        )
        return self.request(route, user_id=user_id)

    def modify_channel_information(self,
                                   user_id: str,
                                   /,
                                   broadcaster_id: str,
                                   game_id: Optional[str] = None,
                                   language: Optional[str] = None,
                                   title: Optional[str] = None,
                                   delay: Optional[int] = None,
                                   tags: Optional[List[str]] = None,
                                   content_classification_labels: Optional[Set[str]] = None,
                                   is_branded_content: Optional[bool] = None
                                   ) -> Response[None]:
        route = Route('PATCH', 'channels', broadcaster_id=broadcaster_id)
        body = {}
        if game_id is not None:
            body['game_id'] = game_id
        if language is not None:
            body['language'] = language
        if title is not None:
            body['title'] = title
        if delay is not None:
            body['delay'] = delay
        if tags is not None:
            body['tags'] = tags
        if content_classification_labels is not None:
            body['content_classification_labels'] = list(content_classification_labels)
        if is_branded_content is not None:
            body['is_branded_content'] = is_branded_content

        return self.request(route, user_id=user_id, json=body)

    def get_channel_editors(self,
                            user_id: str,
                            /,
                            broadcaster_id: str
                            ) -> Response[Data[helix.ChannelEditor]]:
        route = Route('GET', 'channels/editors', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def get_followed_channels(self,
                              user_id: str,
                              /,
                              user_id_follows: str,
                              broadcaster_id: Optional[str] = None,
                              fetch_limit: Optional[int] = None
                              ) -> PaginatedRequest[PData[helix.FollowedChannel], ...]:
        route = Route('GET', 'channels/followed', user_id=user_id_follows, broadcaster_id=broadcaster_id)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_channel_followers(self,
                              user_id: str,
                              /,
                              broadcaster_id: str,
                              user_id_check: Optional[str] = None,
                              fetch_limit: Optional[int] = None
                              ) -> PaginatedRequest[PData[helix.ChannelFollower], ...]:
        route = Route('GET', 'channels/followers', broadcaster_id=broadcaster_id, user_id=user_id_check)
        return PaginatedRequest(self.request, route=route, user_id=user_id, fetch_limit=fetch_limit, max_first=100)

    def get_stream_key(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.StreamKey]]:
        route = Route('GET', 'streams/key', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)

    def get_hype_train_status(self, user_id: str, /, broadcaster_id: str) -> Response[DataL[helix.HypeTrainStatus]]:
        route = Route('GET', 'hypetrain/status', broadcaster_id=broadcaster_id)
        return self.request(route, user_id=user_id)
