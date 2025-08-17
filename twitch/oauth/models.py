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

from typing import NamedTuple, Tuple, TYPE_CHECKING
from types import MappingProxyType

if TYPE_CHECKING:
    from ..types import tokens

__all__ = ('Token', 'ValidateToken', 'ClientCredentials', 'DeviceCode')

class Token(NamedTuple):
    """
    Represents a token.

    Attributes
    ----------
    access_token: str
        The OAuth access token.
    refresh_token: str
        The refresh token.
    token_type: str
        The type of token (usually "bearer").
    scopes: Tuple[str, ...]
        Tuple of scopes granted to the token.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    access_token: str
    refresh_token: str
    token_type: str
    scopes: Tuple[str, ...]
    raw: tokens.Token

    @classmethod
    def from_data(cls, data: tokens.Token) -> Token:
        scope_data = data.get('scope', [])
        if isinstance(scope_data, str):
            scope = tuple(scope_data.split()) if scope_data else ()
        elif isinstance(scope_data, list):
            scope = tuple(scope_data)
        else:
            scope = ()

        return cls(
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            token_type=data['token_type'],
            scopes=scope,
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: Token) -> bool:
        if not isinstance(other, Token):
            return False
        return self.access_token == other.access_token

    def __hash__(self) -> int:
        return hash(self.access_token)

    def __repr__(self) -> str:
        return f"Token(token_type={self.token_type!r})"


class ValidateToken(NamedTuple):
    """
    Represents a validated OAuth token response.

    Attributes
    ----------
    client_id: str
        The client ID associated with the token.
    login: str
        The login name of the user associated with the token.
    scopes: Tuple[str, ...]
        Tuple of scopes granted to the token.
    user_id: str
        The user ID associated with the token.
    expires_in: int
        Number of seconds until the token expires.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    client_id: str
    login: str
    scopes: Tuple[str, ...]
    user_id: str
    expires_in: int
    raw: tokens.ValidateToken

    @classmethod
    def from_data(cls, data: tokens.ValidateToken) -> ValidateToken:
        scopes_data = data.get('scopes', [])
        if isinstance(scopes_data, str):
            scopes = (scopes_data, )
        elif isinstance(scopes_data, list):
            scopes = tuple(scopes_data)
        else:
            scopes = ()

        return cls(
            client_id=data['client_id'],
            login=data['login'],
            scopes=scopes,
            user_id=data['user_id'],
            expires_in=data['expires_in'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ValidateToken) -> bool:
        if not isinstance(other, ValidateToken):
            return False
        return self.user_id == other.user_id and self.client_id == other.client_id

    def __hash__(self) -> int:
        return hash((self.user_id, self.client_id))

    def __repr__(self) -> str:
        return f"ValidateToken(user_id={self.user_id!r}, login={self.login!r})"


class ClientCredentials(NamedTuple):
    """
    Represents a client credentials token.

    Attributes
    ----------
    access_token: str
        The OAuth access token.
    expires_in: int
        Number of seconds until the token expires.
    token_type: str
        The type of token (usually "bearer").
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    access_token: str
    expires_in: int
    token_type: str
    raw: tokens.ClientCredentials

    @classmethod
    def from_data(cls, data: tokens.ClientCredentials) -> ClientCredentials:
        return cls(
            access_token=data['access_token'],
            expires_in=data['expires_in'],
            token_type=data['token_type'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: ClientCredentials) -> bool:
        if not isinstance(other, ClientCredentials):
            return False
        return self.access_token == other.access_token

    def __hash__(self) -> int:
        return hash(self.access_token)

    def __repr__(self) -> str:
        return f"ClientCredentials(token_type={self.token_type!r})"


class DeviceCode(NamedTuple):
    """
    Represents a device code response for device flow authentication.

    Attributes
    ----------
    device_code: str
        The device code used for polling.
    user_code: str
        The user code to be displayed to the user.
    verification_uri: str
        The URI where the user should authenticate.
    expires_in: int
        Number of seconds until the device code expires.
    interval: int
        The minimum interval in seconds between polling requests.
    raw: MappingProxyType[str, Any]
        A shallow-frozen dictionary representing the original payload.
    """

    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int
    raw: tokens.DeviceCode

    @classmethod
    def from_data(cls, data: tokens.DeviceCode) -> DeviceCode:
        return cls(
            device_code=data['device_code'],
            user_code=data['user_code'],
            verification_uri=data['verification_uri'],
            expires_in=data['expires_in'],
            interval=data['interval'],
            raw=MappingProxyType(data)  # type: ignore
        )

    def __eq__(self, other: DeviceCode) -> bool:
        if not isinstance(other, DeviceCode):
            return False
        return self.device_code == other.device_code

    def __hash__(self) -> int:
        return hash(self.device_code)

    def __repr__(self) -> str:
        return f"DeviceCode(user_code={self.user_code!r})"
