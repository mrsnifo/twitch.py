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

from typing import Set, Optional
from ..errors import BadRequest
from ..app import App
from . import models
import asyncio

__all__ = ('DeviceCodeFlow', 'AuthorizationCodeGrantFlow')


class BaseFlow(App):
    """Base flow class for Twitch OAuth operations."""

    def __init__(self, client_id: str, client_secret: str) -> None:
        super().__init__(client_id, client_secret)

    async def validate_token(self, token: str) -> models.ValidateToken:
        """
        Validate a Twitch access token.

        Verifies that the provided access token is valid and returns
        information about the token including its expiration time,
        scopes, and associated user.

        Parameters
        ----------
        token: str
            The access token to validate.

        Returns
        -------
        ValidateToken
            Token validation information.

        Raises
        ------
        Unauthorized
            If the token is invalid.
        """
        data = await self.http.validate_token(token)
        return models.ValidateToken.from_data(data)

    async def refresh_token(self, token: str) -> models.Token:
        """
        Refresh an expired or expiring access token.

        Uses a refresh token to obtain a new access token and refresh token
        pair. The old tokens will be invalidated after successful refresh.

        Parameters
        ----------
        token: str
            The refresh token to use for obtaining new tokens.

        Returns
        -------
        Token
            New access and refresh tokens.

        Raises
        ------
        BadRequest
            If the refresh token is invalid.
        NotFound
            If the client ID does not exist.
        Unauthorized
            If the refresh token is expired or invalid.
        """
        data = await self.http.refresh_token(token)
        return models.Token.from_data(data)

    async def revoke_token(self, token: str) -> None:
        """
        Revoke an access token, invalidating it immediately.

        Revokes the specified access token, making it invalid for future
        API requests. This is useful for logout functionality or security
        purposes.

        Parameters
        ----------
        token: str
            The access token to revoke.

        Raises
        ------
        BadRequest
            If the access token is invalid.
        NotFound
            If the client ID does not exist.
        """
        await self.http.revoke_token(token)

    async def credentials_grant_flow(self) -> models.ClientCredentials:
        """
        Perform OAuth2 client credentials grant flow.

        ??? info

            Obtains an app access token using the client credentials grant flow.
            This token can be used for app-only requests that don't require
            user authorization.

        Returns
        -------
        ClientCredentials
            App access token information.

        Raises
        ------
        BadRequest
            If invalid client ID.
        Forbidden
            If invalid client secret.
        Unauthorized
            If the client credentials are invalid or expired.
        """
        data = await self.http.credentials_grant_flow()
        return models.ClientCredentials.from_data(data)


class DeviceCodeFlow(BaseFlow):
    """
    OAuth2 Device Code Flow.

    This flow is designed for devices that either lack a browser or have
    limited input capabilities. The user authorizes the application on
    a separate device with a browser.

     ???+ tip

        If you already have a token, you can prevent creating another one::

        await flow.authorize(token=client.get_token(client.http.client_id)[0])

    Examples
    --------
    Context Manager::

        async with DeviceCodeFlow("CLIENT_ID", "CLIENT_SECRET") as flow:
            device_code = await flow.request_device_code({"user:read:email"})
            print(f"Go to: {device_code.verification_uri}")
            print(f"Enter code: {device_code.user_code}")
            token = await flow.wait_for_device_token(device_code.device_code)

    Manual::

        flow = DeviceCodeFlow("CLIENT_ID", "CLIENT_SECRET")
        await flow.authorize()
        device_code = await flow.request_device_code({"user:read:email"})
        print(f"Go to: {device_code.verification_uri}")
        print(f"Enter code: {device_code.user_code}")
        token = await flow.wait_for_device_token(device_code.device_code)
        await flow.close()

    From existing App::

        app = App("CLIENT_ID", "CLIENT_SECRET")
        await app.authorize()
        flow = await DeviceCodeFlow.from_app(app)
        # Flow is now ready to use with the app's existing token
    """

    @classmethod
    def from_app(cls, app: App) -> DeviceCodeFlow:
        """
        Create a DeviceCodeFlow instance from an existing App with authorization.

        !!! danger

            The provided App instance must already be authenticated before
            calling this method.

        Parameters
        ----------
        app: App
            An existing App instance that should already be authorized.
            The flow will inherit the app's client credentials and current token.

        Returns
        -------
        DeviceCodeFlow
            A new DeviceCodeFlow instance that's already authorized with
            the app's token.

        Raises
        ------
        IndexError
            If the app has no tokens available.
        """
        flow_instance = cls(app.http.client_id, app.http.client_secret)
        return flow_instance

    async def request_device_code(self, scopes: Set[str] = frozenset()) -> models.DeviceCode:
        """
        Request a device code and user code for device flow authentication.

        Initiates the device flow by requesting a device code, user code,
        and verification URI from Twitch. The user will need to visit the
        verification URI and enter the user code to authorize the application.

        Parameters
        ----------
        scopes: Set[str]
            Set of OAuth scopes to request for the token. If empty,
            default scopes will be used.

        Returns
        -------
        DeviceCode
            Contains device_code, user_code, verification_uri,
            expires_in, and interval for polling.

        Raises
        ------
        BadRequest
            If invalid client ID or scopes are provided.
        Forbidden
            If the client is not authorized for device flow.
        """
        data = await self.http.request_device_code(scopes)
        return models.DeviceCode.from_data(data)

    async def get_device_token(self, device_code: str) -> models.Token:
        """
        Poll for an access token using the device code.

        Attempts to exchange a device code for an access token. This should
        be called repeatedly until the user completes authorization or
        the device code expires.

        Parameters
        ----------
        device_code: str
            The device code obtained from request_device_code().

        Returns
        -------
        Token
            Access token and refresh token if authorization is complete.

        Raises
        ------
        BadRequest
            If the device code is invalid, expired, or authorization is still pending.
        """
        data = await self.http.get_device_token(device_code)
        return models.Token.from_data(data)

    async def wait_for_device_token(
            self,
            device_code: str,
            interval: int = 5,
            timeout: int = 300
    ) -> models.Token:
        """
        Wait for user authorization and automatically retrieve the token.

        Continuously polls for an access token until the user completes
        authorization, the request times out, or an error occurs. This
        method handles the polling logic automatically, including backing
        off when requested by the server.

        Parameters
        ----------
        device_code: str
            The device code obtained from request_device_code().
        interval: int
            Base polling interval in seconds. The actual interval may be
            adjusted based on server responses.
        timeout: int
            Maximum time to wait for authorization in seconds.

        Returns
        -------
        Token
            Access token and refresh token once authorization is complete.

        Raises
        ------
        asyncio.TimeoutError
            If the timeout is reached before authorization completes.
        BadRequest
            If the device code is invalid, expired, or the user denied
            the authorization request.
        """

        async def _poll_for_token():
            while True:
                try:
                    return await self.get_device_token(device_code)
                except BadRequest as exc:
                    if 'authorization_pending' in str(exc):
                        pass
                    elif 'slow_down' in str(exc):
                        continue
                    else:
                        raise
                await asyncio.sleep(interval * 1.2)

        return await asyncio.wait_for(_poll_for_token(), timeout=timeout)


class AuthorizationCodeGrantFlow(BaseFlow):
    """
    OAuth2 Authorization Code Grant Flow.

    This flow is designed for web applications that can securely store
    a client secret and handle HTTP redirects. Users are redirected to
    Twitch to authorize the application, then redirected back with an
    authorization code that can be exchanged for tokens.

    ???+ tip

        This flow is ideal for web applications with server-side components
        that can handle HTTP redirects and store secrets securely.

    Examples
    --------
    With FastAPI Server::

        from twitch.oauth import AuthorizationCodeGrantFlow
        from fastapi.responses import RedirectResponse
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        import uvicorn

        flow = AuthorizationCodeGrantFlow('CLIENT_ID', 'CLIENT_SECRET')

        @asynccontextmanager
        async def lifespan(_):
            await flow.authorize()
            yield
            await flow.close()

        app = FastAPI(lifespan=lifespan)

        @app.get('/login')
        def login():
            auth_url = flow.get_authorization_url(
                redirect_uri='http://localhost:3000/callback',
                scopes={'user:read:email'}
            )
            return RedirectResponse(url=auth_url)

        @app.get('/callback')
        async def callback(code: str):
            token = await flow.get_authorization_token(code=code, redirect_uri='http://localhost:3000/callback')
            return token.raw

        uvicorn.run(app, host='localhost', port=3000)

    Manual::

        flow = AuthorizationCodeGrantFlow('CLIENT_ID', 'CLIENT_SECRET')
        await flow.authorize()

        # Generate auth URL for user
        auth_url = flow.get_authorization_url(
            redirect_uri='http://localhost:3000/callback',
            scopes={'user:read:email'}
        )
        print(f'Visit: {auth_url}')

        # After getting code from callback, exchange for token
        code = input("Enter the code from the callback URL: ")
        token = await flow.get_authorization_token(code, 'http://localhost:3000/callback')
        await flow.close()
    """

    @classmethod
    def from_app(cls, app: App) -> AuthorizationCodeGrantFlow:
        """
        Create a AuthorizationCodeGrantFlow instance from an existing App with authorization.

        !!! danger

            The provided App instance must already be authenticated before
            calling this method.

        Parameters
        ----------
        app: App
            An existing App instance that should already be authorized.
            The flow will inherit the app's client credentials and current token.

        Returns
        -------
        AuthorizationCodeGrantFlow
            A new AuthorizationCodeGrantFlow instance that's already authorized with
            the app's token.

        Raises
        ------
        IndexError
            If the app has no tokens available.
        """
        flow_instance = cls(app.http.client_id, app.http.client_secret)
        return flow_instance

    def get_authorization_url(
            self,
            redirect_uri: str,
            scopes: Set[str] = frozenset(),
            state: Optional[str] = None,
            force_verify: bool = False
    ) -> str:
        """
        Generate the authorization URL for the authorization code grant flow.

        Creates a URL that users should visit to authorize your application.
        After authorization, Twitch will redirect them to your redirect_uri
        with an authorization code.

        Parameters
        ----------
        redirect_uri: str
            Your app's registered redirect URI. The authorization code will
            be sent to this URI after user authorization.
        scopes: Set[str]
            Set of OAuth scopes to request for the token. If empty,
            default scopes will be used.
        state: Optional[str]
            A randomly generated string to help prevent CSRF attacks.
            Strongly recommended for security.
        force_verify: bool
            Whether to force the user to re-authorize your app's access
            to their resources. Default is False.

        Returns
        -------
        str
            The authorization URL that users should visit to authorize
            your application.
        """
        data = self.http.get_authorization_url(redirect_uri, scopes, state, force_verify)
        return data

    async def get_authorization_token(self, code: str, redirect_uri: str) -> models.Token:
        """
        Exchange an authorization code for an access token and refresh token.

        After the user authorizes your application, Twitch redirects them to
        your redirect URI with an authorization code. Use this method to
        exchange that code for usable access and refresh tokens.

        Parameters
        ----------
        code: str
            The authorization code returned from the authorization step.
            This is provided in the 'code' query parameter of the callback URL.
        redirect_uri: str
            Your app's registered redirect URI. This must exactly match
            the redirect_uri used in get_authorization_url().

        Returns
        -------
        Token
            Contains access_token, refresh_token, expires_in, scopes,
            and token_type information.

        Raises
        ------
        BadRequest
            If the authorization code is invalid, expired, or the
            redirect_uri doesn't match.
        Unauthorized
            If the client credentials are invalid.
        Forbidden
            If the client is not authorized for this grant type.
        """
        data = await self.http.get_authorization_token(code, redirect_uri)
        return models.Token.from_data(data)
