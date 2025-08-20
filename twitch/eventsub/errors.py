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

from aiohttp import ClientWebSocketResponse
from ..errors import ClientException
from typing import Optional

__all__ = ('ConnectionClosed', 'ShardError', 'ShardNotFound')

class ConnectionClosed(ClientException):
    """Exception raised when the WebSocket connection is closed unexpectedly."""

    def __init__(self, socket: ClientWebSocketResponse, *, code: Optional[int] = None) -> None:
        self.code: int = code or socket.close_code or -1
        self.reason: str = ''
        super().__init__(f'WebSocket closed with {self.code} close code.')


class ShardError(ClientException):
    """
    Exception raised for individual shard-specific errors.

    Attributes
    ----------
    shard_id: str
        The ID of the shard that failed.
    code: str
        The error code for this specific shard failure.
    message: str
        The error message describing what went wrong.
    """

    def __init__(self, shard_id: int, code: str, message: str) -> None:
        self.shard_id: int = shard_id
        self.code: str = code
        self.message: str = message
        super().__init__(f"Shard ID {shard_id} {message}")


class ShardNotFound(ClientException):
    """Exception raised when no available shards are found for connection."""
    pass