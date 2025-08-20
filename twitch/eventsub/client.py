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

from typing import Any, Callable, Type, Optional, Dict, Tuple, TYPE_CHECKING
from ..errors import HTTPException, TokenError, Unauthorized, NotFound
from ..state import ClientConnectionState, ClientUserConnectionState
from .errors import ConnectionClosed, ShardError, ShardNotFound
from .gateway import EventSubWebSocket, ReconnectWebSocket
from .event import UserEvents, AppEvents
from types import TracebackType
from ..app import App
from .. import utils
import logging
import asyncio
import aiohttp

if TYPE_CHECKING:
    from ..api import UserAPI

__all__ = ('ClientApp', 'ClientUser')

_logger = logging.getLogger(__name__)


class _LoopSentinel:
    """Sentinel class to handle loop access before client initialization."""

    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        msg = (
            "Cannot access 'loop' before the client is fully initialized. "
            "Run inside an asynchronous context or use 'Client.setup_hook'."
        )
        raise AttributeError(msg)

_loop: Any = _LoopSentinel()


class BaseClient(App):
    """Base client for Twitch API with event handling and token management."""

    if TYPE_CHECKING:
        _connection: ClientConnectionState

    def __init__(self, client_id: str, client_secret: str, **options: Any) -> None:
        super().__init__(client_id, client_secret, **options)
        self.ws: EventSubWebSocket = None  # type: ignore
        self.loop: asyncio.AbstractEventLoop = _loop
        self._ready: Optional[asyncio.Event] = None
        self._closing_task: Optional[asyncio.Task] = None
        self._token_task: Optional[asyncio.Task] = None

    def is_closed(self) -> bool:
        """
        Check if the client is closed.

        Returns
        -------
        bool
            True if the client is closed, False otherwise.
        """
        return self._closing_task is not None

    def is_ready(self) -> bool:
        """
        Check if the client is ready.

        Returns
        -------
        bool
            True if the client is ready, False otherwise.
        """
        return self._ready is not None and self._ready.is_set()

    async def __aenter__(self) -> BaseClient:
        self._async_setup()
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:
        if self._closing_task:
            await self._closing_task
        else:
            await self.close()

    def _async_setup(self) -> None:
        """Set up async components and event loop."""
        loop = asyncio.get_running_loop()
        self.loop = loop
        self._connection.loop = loop
        self._ready = asyncio.Event()

    def _get_connection_state(self, **options) -> ClientConnectionState:
        return ClientConnectionState(http=self.http, dispatch=self.dispatch, **options)

    async def setup_hook(self) -> None:
        """
        Hook called after client setup.

         ???+ info

            Override this method to perform custom initialization
            or setup tasks after the client is authorized.

        !!! danger

            Long-running or blocking operations in this method can block
            the client startup.
        """
        pass

    def event(self, coro: Callable[..., Any], /) -> None:
        """
        Register an event handler.

        Parameters
        ----------
        coro: Callable[..., Any]
            The coroutine function to register as an event handler.

        Raises
        ------
        TypeError
            If the provided function is not a coroutine function.
        """
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('The registered event must be a coroutine function')
        setattr(self, coro.__name__, coro)

    def dispatch(self, event: str, /, *args: Any, **kwargs: Any) -> None:
        """
        Dispatch an event to registered handlers.

        Parameters
        ----------
        event: str
            The event name to dispatch.
        *args: Any
            Positional arguments to pass to event handlers.
        **kwargs: Any
            Keyword arguments to pass to event handlers.
        """
        method = 'on_' + event
        try:
            coro = getattr(self, method)
            if coro is not None and asyncio.iscoroutinefunction(coro):
                _logger.debug('Dispatching event %s', event)
                wrapped = self._run_event(coro, method, *args, **kwargs)
                self.loop.create_task(wrapped, name=f'twitch.py:client:{method}')
        except AttributeError:
            pass

    async def _run_event(
            self,
            coro: Callable[..., Any],
            event_name: str,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """Run an event handler with error handling."""
        try:
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception as error:
            await self.on_error(event_name, error, *args, **kwargs)

    @staticmethod
    async def on_error(
            event_method: str,
            error: Exception,
            /,
            *args: Any,
            **kwargs: Any
    ) -> None:
        """
        Handle errors from event handlers.

        ???+ info

            Override this method to implement custom error handling
            or logging behavior.

        Parameters
        ----------
        event_method: str
            Event method name that caused the error.
        error: Exception
            The exception that occurred.
        *args: Any
            Event positional arguments.
        **kwargs: Any
            Event keyword arguments.
        """
        _logger.exception(
            'Ignoring error: %s from %s, args: %s kwargs: %s',
            error, event_method, args, kwargs
        )

    def add_token(self, user_id: str, access_token: str, refresh_token: Optional[str]) -> UserAPI:
        user = super().add_token(user_id, access_token, refresh_token)
        self.dispatch('token_update', user_id, access_token, refresh_token)
        return user

    async def add_user(self, access_token: str, refresh_token: Optional[str]) -> UserAPI:
        user = await super().add_user(access_token, refresh_token)
        tokens = self.tokens.get(user.id)
        self.dispatch('token_update', user.id, tokens[0], tokens[1])
        return user

    def remove_token(self, user_id: str) -> None:
        super().remove_token(user_id)
        self.dispatch('token_remove', user_id)

    def token_maintenance_task(self) -> None:
        """
        Start the token maintenance background task.

        !!! info

            Override this method to disable automatic token validation
            or implement custom token refresh behavior.
        """
        if self._token_task is not None and not self._token_task.done():
            self._token_task.cancel()

        self._token_task = asyncio.create_task(
            self._token_maintain(),
            name='twitch.py:client:token_maintenance'
        )

    async def _token_maintain(
            self,
            validation_interval: float = 3600.0,
            refresh_threshold: float = 600.0,
            min_wake: float = 300.0,
            max_wake: float = 900.0
    ) -> None:
        """Maintain tokens with periodic validation and refresh."""
        _logger.debug("Token maintenance loop started")
        backoff = utils.ExponentialBackoff(base_delay=1, max_delay=60)

        while not self.is_closed():
            try:
                sleep_duration, updated_user_ids = await self.http.maintain_tokens(
                    validation_interval=validation_interval,
                    refresh_threshold=refresh_threshold,
                    min_wake=min_wake,
                    max_wake=max_wake
                )

                for user_id in updated_user_ids:
                    tokens = self.tokens.get(user_id)
                    if tokens is None:
                        self.dispatch('token_remove', user_id)
                    else:
                        self.dispatch('token_update', user_id, tokens[0], tokens[1])

                _logger.debug(
                    "Token maintenance completed, sleeping for %.1fs",
                    sleep_duration
                )
                await asyncio.sleep(sleep_duration)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                delay = backoff.get_delay()
                _logger.error(
                    "Token maintenance loop error: %s, retrying in %ss",
                    exc, delay, exc_info=True
                )
                await asyncio.sleep(delay)

    async def authorize(self, token: Optional[str] = None, /) -> None:
        if self.loop is _loop:
            self._async_setup()

        await super().authorize(token=token)
        tokens = self.tokens.get(self.http.client_id)
        self.dispatch('token_update', self.http.client_id, tokens[0], tokens[1])

        await self.setup_hook()
        self.token_maintenance_task()

    async def wait_until_ready(self) -> None:
        """
        Wait until the client is ready.

        Raises
        ------
        RuntimeError
            If the client is not initialized.
        """
        if self._ready is not None:
            await self._ready.wait()
        else:
            raise RuntimeError(
                "The client is not initialized. Use the asynchronous context "
                "manager to initialize the client."
            )

    def clear(self) -> None:
        self._closing_task = None
        self._token_task = None
        if self._ready is not None:
            self._ready.clear()
        super().clear()

    async def close(self) -> None:
        if self._closing_task:
            return await self._closing_task

        async def _close():
            if self.ws is not None and self.ws.open:
                await self.ws.close(code=1000)

            await self.http.close()

            if self._ready is not None:
                self._ready.clear()

            if self._token_task is not None and not self._token_task.done():
                self._token_task.cancel()

            self.loop = _loop

        self._closing_task = asyncio.create_task(_close())
        return await self._closing_task


class ClientApp(BaseClient):
    """
    Twitch EventSub WebSocket client for app-based connections.

    Handles conduit-based event subscriptions, shard management,
    and WebSocket connections for Twitch applications.

    Parameters
    ----------
    client_id: str
        The application's unique client identifier.
    client_secret: str
        The application's client secret for secure authentication.
    **options: Any
        Additional configuration options

        - ignore_conflict: bool
            If True, ignores subscription conflicts and returns existing
            subscription. If False, raises conflict errors. Default False.
        - connector: Optional[aiohttp.BaseConnector]
            Custom HTTP connector for the session.
        - proxy: Optional[str]
            Proxy server URL for HTTP requests.
        - proxy_auth: Optional[aiohttp.BasicAuth]
            Authentication credentials for proxy server.
        - http_trace: Optional[aiohttp.TraceConfig]
            HTTP tracing configuration for debugging.
    """

    def __init__(self, client_id: str, client_secret: str, **options: Any):
        super().__init__(client_id, client_secret, **options)

    @property
    def eventsub(self) -> AppEvents:
        """
        Get the app events handler for creating EventSub subscriptions.

        ??? note
            Subscription creation behavior is controlled by the ignore_conflict
            option set during client initialization.

        ??? info "Event Dispatching"

            Events are dispatched to specific handlers, or with `_raw` suffix if
            no model exists. You can force newer unsupported versions for testing -
            these will dispatch as raw events.

        Returns
        -------
        AppEvents
            The events handler for app-based subscriptions.
        """
        return self._connection.events

    async def identify_shard(self, conduit_id: str, shard_id: int, /, *, session_id: str) -> None:
        """
        Identify a shard with the conduit.

        Parameters
        ----------
        conduit_id: str
            The conduit ID to register the shard with.
        shard_id: int
            The shard ID to identify.
        session_id: str
            The WebSocket session ID.

        Raises
        ------
        ShardError
            If shard identification fails.
        TokenError
            If missing a valid app access token with required scopes.
        Unauthorized
            If the token is invalid, expired, or doesn't have the required scopes.
        NotFound
            If conduit not found.
        """
        shard = {
            'id': str(shard_id),
            'transport': {
                'method': 'websocket',
                'session_id': session_id
            }
        }
        data = await self.application.update_conduit_shards(conduit_id, (shard,))
        if data.errors:
            raise ShardError(shard_id, data.errors[0].code, data.errors[0].message)
        self.dispatch('shard_connect', shard_id)

    async def authorize(self, token: Optional[str] = None, /, *, conduit_id: Optional[str] = None) -> None:
        await super().authorize(token)
        self._connection.events = AppEvents(self.http.client_id, state=self._connection, conduit_id=conduit_id)
        self.dispatch('ready')
        if self._ready is not None:
            self._ready.set()

    async def connect(self, conduit_id: str, *, shard_ids: Tuple[int, ...], reconnect: bool = True) -> None:
        """
        Connect to Twitch EventSub WebSocket with shard management.

        !!! danger "Important: Keep All Shards Connected"

            **You need an active WebSocket connection for every shard in your conduit.**

            If you have dead shards (no connection), you'll miss events.
            Always keep your shard count equal to your active connections.

        Parameters
        ----------
        conduit_id: str
            The conduit ID for event subscriptions.
        shard_ids: Tuple[int, ...]
            Tuple of shard IDs to check for availability. The first non-enabled shard will be used for the connection.
        reconnect: bool
            Whether to automatically reconnect on connection failures.

        Raises
        ------
        ShardError
            If shard identification fails.
        ShardNotFound
            If all provided shards are already enabled.
        TokenError
            If missing a valid app access token with required scopes.
        Unauthorized
            If the token is invalid, expired, or doesn't have the required scopes.
        NotFound
            If conduit not found.
        ConnectionClosed
            If WebSocket connection is closed unexpectedly.
        """
        backoff = utils.ExponentialBackoff()
        ws_params = {}

        enabled_shards = self.application.get_conduit_shards(
            conduit_id=conduit_id,
            status='enabled',
            limit=max(shard_ids) + 1
        )

        enabled_ids = {int(s.id) async for s in enabled_shards if s.status == 'enabled'}
        shard_id = next((sid for sid in shard_ids if sid not in enabled_ids), None)

        if shard_id is None:
            raise ShardNotFound("All provided shards are already enabled")

        while not self.is_closed():
            try:
                socket = EventSubWebSocket.connect_websocket(self, **ws_params)
                self.ws = await asyncio.wait_for(socket, timeout=60.0)
                await self.identify_shard(conduit_id, shard_id, session_id=self.ws.session_id)
                while True:
                    await self.ws.poll_event()

            except ReconnectWebSocket as exc:
                self.dispatch('disconnect')
                _logger.debug('WebSocket reconnecting to %s', exc.url)
                ws_params['gateway'] = exc.url

            except (OSError,
                    TokenError,
                    HTTPException,
                    ConnectionClosed,
                    aiohttp.ClientError,
                    asyncio.TimeoutError
                    ) as exc:
                self.dispatch('disconnect')

                if not reconnect or isinstance(exc, (TokenError, Unauthorized, NotFound)):
                    await self.close()
                    if isinstance(exc, ConnectionClosed) and exc.code == 1000:
                        return
                    raise

                if self.is_closed():
                    return

                if isinstance(exc, ConnectionClosed) and exc.code != 1000:
                    await self.close()
                    raise

                delay = backoff.get_delay()
                _logger.exception('Attempting reconnect in %d seconds', delay)
                ws_params.pop('gateway', None)
                await asyncio.sleep(delay)

    async def start(self, conduit_id: str, *, shard_ids: Tuple[int, ...] = (0,),  reconnect: bool = True) -> None:
        """
        Start the client by authorizing and connecting.

        !!! danger "Important: Keep All Shards Connected"

            **You need an active WebSocket connection for every shard in your conduit.**

            If you have dead shards (no connection), you'll miss events.
            Always keep your shard count equal to your active connections.

        Parameters
        ----------
        conduit_id: str
            The conduit ID for event subscriptions.
        shard_ids: Tuple[int, ...]
            Tuple of shard IDs to create connections for.
        reconnect: bool
            Whether to automatically reconnect on connection failures.
        """
        await self.authorize(conduit_id=conduit_id)
        await self.connect(conduit_id, shard_ids=shard_ids, reconnect=reconnect)

    def run(
            self,
            conduit_id: str,
            shard_ids: Tuple[int, ...] = (0,),
            *,
            reconnect: bool = True,
            log_handler: Optional[logging.Handler] = None,
            log_level: Optional[int] = None,
            root_logger: bool = False
    ) -> None:
        """
        Run the client with event loop management.

        !!! danger "Important: Keep All Shards Connected"

            **You need an active WebSocket connection for every shard in your conduit.**

            If you have dead shards (no connection), you'll miss events.
            Always keep your shard count equal to your active connections.

        Parameters
        ----------
        conduit_id: str
            The conduit ID for event subscriptions.
        shard_ids: Tuple[int, ...]
            Tuple of shard IDs to create connections for.
        reconnect: bool
            Whether to automatically reconnect on connection failures.
        log_handler: Optional[logging.Handler]
            Custom logging handler. If None, uses default setup.
        log_level: Optional[int]
            Logging level. If None, uses default level.
        root_logger: bool
            Whether to configure the root logger.
        """
        if log_handler is None:
            utils.setup_logging(handler=log_handler, level=log_level, root=root_logger)

        async def runner() -> None:
            async with self:
                await self.start(conduit_id, shard_ids=shard_ids, reconnect=reconnect)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return


class ClientUser(BaseClient):
    """
    Twitch EventSub WebSocket client for user-based connections.

    Handles user authentication, event subscriptions, and WebSocket
    connections for individual Twitch users with automatic token management.

    Parameters
    ----------
    client_id: str
        The application's unique client identifier.
    client_secret: str
        The application's client secret for secure authentication.
    **options: Any
        Additional configuration options

        - ignore_conflict: bool
            If True, ignores subscription conflicts and returns existing
            subscription. If False, raises conflict errors. Default False.
        - connector: Optional[aiohttp.BaseConnector]
            Custom HTTP connector for the session.
        - proxy: Optional[str]
            Proxy server URL for HTTP requests.
        - proxy_auth: Optional[aiohttp.BasicAuth]
            Authentication credentials for proxy server.
        - http_trace: Optional[aiohttp.TraceConfig]
            HTTP tracing configuration for debugging.
    """

    if TYPE_CHECKING:
        _connection: ClientUserConnectionState

    def __init__(self, client_id: str, client_secret: str, **options: Any):
        self.__user: Optional[UserAPI] = None
        self._handlers: Dict[str, Callable[..., None]] = {
            'websocket_ready': self._handle_websocket_ready
        }
        self._websocket_ready: Optional[asyncio.Event] = None

        super().__init__(client_id, client_secret, **options)
        self._connection._get_websocket = self._get_websocket

    @property
    def user(self) -> UserAPI:
        """
        Get the authenticated user API instance.

        Returns
        -------
        UserAPI
            The authenticated user's API interface.

        Raises
        ------
        AttributeError
            If user is not authenticated. Call login() first.
        """
        if self.__user is None:
            raise AttributeError("User not authenticated. Call login() first.")
        return self.__user

    @property
    def eventsub(self) -> UserEvents:
        """
        Get the user events handler for creating EventSub subscriptions.

        ???+ tip

            You can create subscriptions even if the WebSocket is not connected.
            The client will automatically establish a WebSocket connection when needed.

        ??? note

            Subscription creation behavior is controlled by the ignore_conflict
            option set during client initialization.

        ??? info "Event Dispatching"

            Events are dispatched to specific handlers, or with `_raw` suffix if
            no model exists. You can force newer unsupported versions for testing.


        Returns
        -------
        UserEvents
            The events handler for user-based subscriptions.
        """
        return self._connection.events

    def _get_connection_state(self, **options) -> ClientUserConnectionState:
        return ClientUserConnectionState(
            http=self.http,
            dispatch=self.dispatch,
            handlers=self._handlers,
            **options
        )

    def _get_websocket(self) -> Optional[EventSubWebSocket]:
        """Return the WebSocket instance if it's an EventSub WebSocket, otherwise None."""
        return self.ws if isinstance(self.ws, EventSubWebSocket) else None

    def _handle_websocket_ready(self) -> None:
        """Signal that the WebSocket is ready for event subscriptions."""
        if self._websocket_ready is not None:
            self._websocket_ready.set()

    def _async_setup(self) -> None:
        super()._async_setup()
        self._websocket_ready = asyncio.Event()

    def clear(self) -> None:
        super().clear()
        self.__user = None
        if self._websocket_ready is not None:
            self._websocket_ready.clear()

    async def close(self) -> None:
        if self._closing_task:
            return await self._closing_task

        async def _close():
            if self.ws is not None and self.ws.open:
                await self.ws.close(code=1000)

            await self._connection.wait()
            await self.http.close()

            if self._ready is not None:
                self._ready.clear()

            if self._token_task is not None and not self._token_task.done():
                self._token_task.cancel()

            self.loop = _loop

        self._closing_task = asyncio.create_task(_close())
        return await self._closing_task

    async def login(self, access_token: str, refresh_token: Optional[str]) -> None:
        """
        Authenticate a user with access and refresh tokens.

        Parameters
        ----------
        access_token: str
            Valid Twitch user access token.
        refresh_token: Optional[str]
            Optional refresh token for automatic token renewal.

        Raises
        ------
        AuthFailure
            If the tokens are invalid or authorization fails.
        """
        self.__user = await self.add_user(access_token, refresh_token)
        self._connection.events = UserEvents(self.__user.id, state=self._connection)
        self.dispatch('ready')
        if self._ready is not None:
            self._ready.set()

    async def connect(
            self,
            *,
            reconnect: bool = True,
            mock_url: Optional[str] = None
    ) -> None:
        """
        Connect to Twitch EventSub WebSocket with automatic reconnection.

        ???+ note
            This method handles automatic resubscription to events after reconnection.
            The client will attempt to maintain all active subscriptions across
            connection interruptions.

        Parameters
        ----------
        reconnect: bool
            Whether to automatically reconnect on connection failures.
        mock_url: Optional[str]
            Mock WebSocket URL for testing purposes. If provided,
            the client will connect to this URL instead of the official
            Twitch EventSub endpoint.

        Raises
        ------
        ConnectionClosed
            If WebSocket connection is closed unexpectedly and reconnect is False.
        """
        backoff = utils.ExponentialBackoff()
        ws_params = {}

        mock_gateway = None
        if mock_url:
            self.http.mock_url, mock_gateway = utils.parse_mock_urls(mock_url)
            ws_params['gateway'] = mock_gateway

        is_initial = True
        while not self.is_closed():
            try:
                await self._connection.wait(initial=is_initial)
                if self._websocket_ready is not None:
                    await self._websocket_ready.wait()

                if self.is_closed():
                    return

                socket = EventSubWebSocket.connect_websocket(self, **ws_params)
                self.ws = await asyncio.wait_for(socket, timeout=60.0)

                if self._websocket_ready is not None:
                    self._websocket_ready.clear()

                if not is_initial:
                    self._connection.establish_session(self.ws.session_id)
                else:
                    events = await self._connection.drain_subscriptions()
                    self._connection.establish_session(self.ws.session_id)
                    self._connection._resubscribe_task = self.loop.create_task(
                        self._connection.resubscribe_events(self.ws.session_id, events)
                    )

                is_initial = False

                while True:
                    await self.ws.poll_event()

            except ReconnectWebSocket as exc:
                self.dispatch('disconnect')
                _logger.debug('WebSocket reconnecting to %s', exc.url)
                ws_params['gateway'] = exc.url

            except (OSError, HTTPException, ConnectionClosed, aiohttp.ClientError, asyncio.TimeoutError) as exc:
                self.dispatch('disconnect')
                ws_params['gateway'] = mock_gateway
                is_initial = True

                if isinstance(exc, ConnectionClosed) and exc.code == 4003:
                    continue

                if not reconnect:
                    await self.close()
                    if isinstance(exc, ConnectionClosed) and exc.code == 1000:
                        return
                    raise

                if self.is_closed():
                    return

                if isinstance(exc, ConnectionClosed) and exc.code != 1000:
                    await self.close()
                    raise

                delay = backoff.get_delay()
                _logger.exception('Attempting reconnect in %d seconds.', delay)
                await asyncio.sleep(delay)

    async def start(
            self,
            access_token: str,
            refresh_token: Optional[str] = None,
            *,
            reconnect: bool = True,
            mock_url: Optional[str] = None,
    ) -> None:
        """
        Start the client by authorizing, logging in, and connecting.

        Parameters
        ----------
        access_token: str
            Valid Twitch user access token.
        refresh_token: Optional[str]
            Optional refresh token for automatic token renewal.
        reconnect: bool
            Whether to automatically reconnect on connection failures.
        mock_url: Optional[str]
            Mock WebSocket URL for testing purposes.

        Raises
        ------
        TokenError
            If the access token is invalid or missing required scopes.
        Unauthorized
            If the token is expired or doesn't have the required permissions.
        ConnectionClosed
            If WebSocket connection is closed unexpectedly and reconnect is False.
        HTTPException
            If there's an HTTP error during startup.
        """
        await self.authorize()
        await self.login(access_token, refresh_token)
        await self.connect(reconnect=reconnect, mock_url=mock_url)

    def run(
            self,
            access_token: str,
            refresh_token: Optional[str] = None,
            *,
            reconnect: bool = True,
            mock_url: Optional[str] = None,
            log_handler: Optional[logging.Handler] = None,
            log_level: Optional[int] = None,
            root_logger: bool = False
    ) -> None:
        """
        Run the client with event loop management.

        !!! danger

            This is a blocking call that runs the client until stopped.
            Sets up logging and handles the async context automatically.

        Parameters
        ----------
        access_token: str
            Valid Twitch user access token.
        refresh_token: Optional[str]
            Optional refresh token for automatic token renewal.
        reconnect: bool
            Whether to automatically reconnect on connection failures.
        mock_url: Optional[str]
            Mock WebSocket URL for testing purposes.
        log_handler: Optional[logging.Handler]
            Custom logging handler. If None, uses default setup.
        log_level: Optional[int]
            Logging level. If None, uses default level.
        root_logger: bool
            Whether to configure the root logger. Default False.
        """
        if log_handler is None:
            utils.setup_logging(handler=log_handler, level=log_level, root=root_logger)

        async def runner() -> None:
            async with self:
                await self.start(access_token, refresh_token, reconnect=reconnect, mock_url=mock_url)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            return
