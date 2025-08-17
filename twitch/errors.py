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

from typing import Optional, Dict, Any, Union
from aiohttp import ClientResponse

__all__ = ('TwitchException',
           'ClientException',
           'HTTPException',
           'TwitchServerError',
           'Forbidden',
           'NotFound',
           'RateLimited',
           'BadRequest',
           'Unauthorized',
           'AuthFailure',
           'Conflict',
           'TokenError'
           )


class TwitchException(Exception):
    """Base exception for twitch.py."""
    pass


class ClientException(TwitchException):
    """ Exception raised when an operation in the Client class fails."""
    pass

class HTTPException(TwitchException):
    """
    Exception raised for failed HTTP requests to the Twitch API.

    Attributes
    ----------
    response: aiohttp.ClientResponse
        The original aiohttp response object.
    status: int
        The HTTP status code of the response.
    code: int or str
        The Twitch API-specific error code, if available.
    text: str
        The error message or description.
    headers: dict
        The response headers from aiohttp.
    """

    def __init__(self, response: ClientResponse, message: Optional[Union[str, Dict[str, Any]]] = None):
        self.response = response
        self.status = getattr(response, 'status', 0)
        self.headers = dict(response.headers) if hasattr(response, 'headers') else {}

        if isinstance(message, dict):
            self.code = message.get('status', message.get('error', 0))
            self.text = message.get('message', message.get('error_description', ''))
            if 'error' in message and isinstance(message['error'], str):
                self.text = f"{message['error']}: {message.get('message', '')}"
        elif isinstance(message, str):
            self.text = message
            self.code = 0
        else:
            self.text = getattr(response, 'reason', 'Unknown error')
            self.code = 0
        super().__init__(self.text)

    def is_client_error(self) -> bool:
        """Check if this is a client error (4xx status code)."""
        return 400 <= self.status < 500

    def is_server_error(self) -> bool:
        """Check if this is a server error (5xx status code)."""
        return 500 <= self.status < 600


class TwitchServerError(HTTPException):
    """Exception raised when a 500 range status code occurs."""
    pass


class Forbidden(HTTPException):
    """Exception raised when status code 403 occurs."""
    pass


class NotFound(HTTPException):
    """Exception raised when status code 404 occurs."""
    pass


class RateLimited(HTTPException):
    """Exception raised when rate limited and max timeout exceeded."""
    pass


class BadRequest(HTTPException):
    """Exception raised when status code 400 occurs."""
    pass


class Unauthorized(HTTPException):
    """Exception raised when status code 401 occurs."""
    pass


class Conflict(HTTPException):
    """Exception raised when status code 409 occurs."""
    pass


class AuthFailure(ClientException):
    """Exception raised when authentication fails, typically due to invalid credentials."""
    pass


class TokenError(ClientException):
    """Exception raised when there are token-related issues."""
    pass
