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

from typing import  Any, Tuple, Type, Optional, TYPE_CHECKING
from types import MappingProxyType, TracebackType
from .api import AppAPI, UserAPI
from .errors import TokenError
from .http import HTTPClient
import aiohttp
import logging

if TYPE_CHECKING:
    from .state import ConnectionState

_logger = logging.getLogger(__name__)


class App:
    """
    Application interface for API connections and user management.

    Provides core functionality for managing API connections, handling user
    authentication tokens, and accessing both application-level and user-level APIs.

    !!! warning "Token Validation"

        User tokens are not automatically validated or refreshed periodically
        and may require manual refresh for long-running applications.

    Parameters
    ----------
    client_id: str
        The application's unique client identifier.
    client_secret: str
        The application's client secret for secure authentication.
    **options: Any
        Additional configuration options

        - connector: Optional[aiohttp.BaseConnector]
            Custom HTTP connector for the session.
        - proxy: Optional[str]
            Proxy server URL for HTTP requests.
        - proxy_auth: Optional[aiohttp.BasicAuth]
            Authentication credentials for proxy server.
        - http_trace: Optional[aiohttp.TraceConfig]
            HTTP tracing configuration for debugging.

    Examples
    --------
    Context Manager::

        async with App("CLIENT_ID", "CLIENT_SECRET") as app:
            global_emotes = await app.application.get_global_emotes()

    Manual::

        app = App("CLIENT_ID", "CLIENT_SECRET")
        await app.authorize()
        global_emotes = await app.application.get_global_emotes()
        await app.close()
    """

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            **options: Any
    ) -> None:
        connector: Optional[aiohttp.BaseConnector] = options.get('connector', None)
        proxy: Optional[str] = options.pop('proxy', None)
        proxy_auth: Optional[aiohttp.BasicAuth] = options.pop('proxy_auth', None)
        http_trace: Optional[aiohttp.TraceConfig] = options.pop('http_trace', None)
        self.http: HTTPClient = HTTPClient(
            client_id,
            client_secret,
            connector,
            proxy=proxy,
            proxy_auth=proxy_auth,
            http_trace=http_trace,
        )
        self._connection: ConnectionState = self._get_connection_state(**options)

    @property
    def application(self) -> Optional[AppAPI]:
        """
        Get the application API instance.

        Returns
        -------
        Optional[AppAPI]
            The application API instance if authorized, None otherwise.
        """
        return self._connection.application

    @property
    def tokens(self) -> MappingProxyType[str, Tuple[str, Optional[str]]]:
        """
        Get all stored user tokens.

        Returns
        -------
        MappingProxyType[str, Tuple[str, Optional[str]]]
            Read-only mapping of user IDs to (access_token, refresh_token) tuples.
            Refresh tokens may be None if not provided.
        """
        return self.http.tokens

    @property
    def users_scopes(self) -> MappingProxyType[str, Tuple[str, ...]]:
        """
        Get the scopes for all authorized users.

        Returns
        -------
        MappingProxyType[str, Tuple[str, ...]]
            Read-only mapping of user IDs to their granted OAuth scopes.
        """
        return self.http.users_scopes

    @property
    def tokens_validity(self) -> MappingProxyType[str, Tuple[float, float]]:
        """
        Get token validity timestamps for all users.

        Returns
        -------
        MappingProxyType[str, Tuple[float, float]]
            Read-only mapping of user IDs to (last_validated, expires_in) tuples.
            Timestamps are in Unix epoch format.
        """
        return self.http.tokens_validity

    def _get_connection_state(self, **options) -> ConnectionState:
        """Create and return a new connection state instance."""
        # Circular Import.
        from .state import ConnectionState
        return ConnectionState(http=self.http, **options)

    async def __aenter__(self) -> App:
        """Async context manager entry."""
        try:
            await self.authorize()
        except Exception:
            await self.close()
            raise
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:
        """Async context manager exit."""
        await self.close()

    def get_token_quota(self, user_id: str) -> Optional[int]:
        """
        Get the remaining token quota for a specific user.

        Parameters
        ----------
        user_id: str
            The user identifier to check quota for.

        Returns
        -------
        Optional[int]
            The remaining quota count, or None if quota information
            is not available or user doesn't exist.
        """
        return self.http.get_token_quota(user_id)

    def get_token(self, user_id: str) -> Optional[Tuple[str, Optional[str]]]:
        """
        Get stored tokens for a specific user.

        Retrieves the access token and refresh token (if available) for the
        specified user from local storage.

        Parameters
        ----------
        user_id: str
            The user identifier to retrieve tokens for.

        Returns
        -------
        Optional[Tuple[str, Optional[str]]]
            The stored (access_token, refresh_token) tuple, or None if not found.
        """
        return self.tokens.get(user_id)

    def add_token(self, user_id: str, access_token: str, refresh_token: Optional[str]) -> UserAPI:
        """
        Add or update tokens for a user without validation.

        Parameters
        ----------
        user_id: str
            The user identifier.
        access_token: str
            The access token for API requests.
        refresh_token: Optional[str]
            The refresh token for token renewal. Can be None.

        Returns
        -------
        UserAPI
            A UserAPI instance for the user with stored tokens.
        """
        self.http.add_token(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token
        )
        return self._connection.store_user(user_id)

    def remove_token(self, user_id: str) -> None:
        """
        Remove stored tokens for a user.

        !!! warning

            This method only removes tokens from local storage and does NOT
            revoke them on Twitch's servers. The tokens will remain valid
            until they expire naturally.

        Parameters
        ----------
        user_id: str
            The user identifier whose tokens should be removed.
        """
        self.http.remove_token(user_id=user_id)

    def clear(self) -> None:
        """
        Reset the client to its initial state.

        Clears all internal state including tasks and events.
        After calling this method, the client can be reused.
        """
        self._connection.clear()
        self.http.clear()

    async def close(self) -> None:
        """Closes the connection to Twitch."""
        await self.http.close()

    async def add_user(self, access_token: str, refresh_token: Optional[str]) -> UserAPI:
        """
        Add and validate a new user with provided tokens.

        Validates the provided tokens with Twitch's API and stores them
        if valid. This method should be preferred over add_token() when
        token validation is needed.

        Parameters
        ----------
        access_token: str
            The user's access token.
        refresh_token: Optional[str]
            The user's refresh token for automatic renewal.

        Returns
        -------
        UserAPI
            A UserAPI instance for the validated and stored user.

        Raises
        ------
        AuthFailure
            If the tokens are invalid or authorization fails.
        """
        user_id, tokens = await self.http.add_user(
            access_token=access_token,
            refresh_token=refresh_token
        )
        return self._connection.store_user(user_id)

    def get_user_by_id(self, user_id: str) -> UserAPI:
        """
        Get a UserAPI instance for an already authorized user.

        ???+ warning
            This method does not validate stored tokens. If tokens are invalid
            or expired, API calls through the returned UserAPI may fail.

        Parameters
        ----------
        user_id: str
            The user identifier to get API access for.

        Returns
        -------
        UserAPI
            A UserAPI instance for the specified user.

        Raises
        ------
        ValueError
            If the user_id matches the client_id (use application property instead).
        TokenError
            If no tokens are stored for the specified user_id.
        """
        if user_id == self.http.client_id:
            raise ValueError(
                "Cannot create User for client_id. "
                "Use the application property instead."
            )

        if user_id not in self.tokens:
            raise TokenError("No token associated with this user ID.")
        return self._connection.store_user(user_id)

    async def authorize(self, *, token: Optional[str] = None) -> None:
        """
        Authorize the application for API access.

        ???+ note
            This method is called automatically when using the async context
            manager. The application property will be available after successful
            authorization.

        Obtains an application access token using the client credentials
        flow, enabling access to application-level APIs.

        Parameters
        ----------
        token: Optional[str]
            An optional pre-existing app access token. If None,
            automatically generates one using client credentials flow.

        Raises
        ------
        BadRequest
            If invalid client id.
        Forbidden
            If invalid client secret.
        Unauthorized
            If the client credentials are invalid or expired.
        """
        user_id, tokens = await self.http.authorize(token)
        self._connection.application = AppAPI(
            user_id,
            state=self._connection,
        )