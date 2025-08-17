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

from typing import Optional, ClassVar, Dict, Callable, Any, NamedTuple, TYPE_CHECKING
from .errors import ConnectionClosed
from types import MappingProxyType
from ..models import Subscription
from .. import utils
import datetime
import logging
import asyncio
import aiohttp
import json

if TYPE_CHECKING:
    from ..state import ClientConnectionState
    from .client import ClientApp, ClientUser
    from ..types import eventsub

__all__ = ('ReconnectWebSocket', 'EventSubWebSocketResponse', 'EventSubWebSocket', 'Metadata')


class Metadata(NamedTuple):
    """
    EventSub metadata.

    Attributes
    ----------
    message_id: str
        Unique identifier for the message.
    message_type: str
        Type of the EventSub message.
    message_timestamp: datetime.datetime
        Timestamp when the message was created.
    raw: MappingProxyType[str, Any]
        A MappingProxyType-wrapped dictionary representing the original event payload.

    Notes
    -----
    Twitch guarantees at-least-once delivery for EventSub notifications.
    Duplicate messages retain the same message_id for deduplication.
    """

    message_id: str
    message_type: str
    message_timestamp: datetime.datetime
    raw: eventsub.Metadata

    @classmethod
    def from_data(cls, data: eventsub.Metadata) -> Metadata:
        """Create Metadata instance from EventSub data."""
        return cls(
            message_id=data['message_id'],
            message_type=data['message_type'],
            message_timestamp=utils.from_iso_string(data['message_timestamp']),
            raw=MappingProxyType(data) # type: ignore
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Metadata):
            return False
        return self.message_id == other.message_id

    def __repr__(self) -> str:
        return f"Metadata(message_id={self.message_id}, message_type={self.message_type})"

    def __hash__(self) -> int:
        return hash(self.message_id)

_logger = logging.getLogger(__name__)


class WebSocketClosure(Exception):
    """Exception indicating closure of the WebSocket."""
    pass


class ReconnectWebSocket(Exception):
    """Exception indicating the need to reconnect to the websocket."""
    def __init__(self, url: Optional[str], reason: str = "Reconnection requested") -> None:
        self.url: Optional[str] = url
        self.reason: str = reason
        super().__init__(f"Reconnect required: {reason}")


class EventSubWebSocketResponse(aiohttp.ClientWebSocketResponse):
    async def close(self, *, code: int = 4000, message: bytes = b'') -> bool:
        return await super().close(code=code, message=message)


class EventSubWebSocket:
    """EventSub WebSocket client for real-time event notifications."""
    DEFAULT_GATEWAY: ClassVar[str] = "wss://eventsub.wss.twitch.tv/ws"

    if TYPE_CHECKING:
        _state: ClientConnectionState
        _eventsub_parsers: Dict[str, Callable[..., Any]]
        gateway: str

    def __init__(self, socket: aiohttp.ClientWebSocketResponsel) -> None:
        self.socket: aiohttp.ClientWebSocketResponse = socket
        self._session_id: Optional[str] = None
        self._close_code: Optional[int] = None
        self._connected_at: Optional[datetime.datetime] = None
        self._keep_alive_timeout: float = 30.0

    @classmethod
    async def connect_websocket(cls,
                                client: ClientApp | ClientUser,
                                *,
                                gateway: Optional[str] = None
                                ) -> EventSubWebSocket:
        """Connect to EventSub WebSocket and establish session."""
        gateway = gateway or cls.DEFAULT_GATEWAY
        # i know.. i know..
        state = client._connection

        socket = await state.http.ws_connect(url=gateway)
        client.dispatch('connect')
        ws: EventSubWebSocket = cls(socket)
        ws._state = state
        ws._eventsub_parsers = state.parsers
        ws.gateway = gateway

        # Welcome Message.
        await ws.poll_event()
        return ws

    @property
    def open(self) -> bool:
        """
        Check if WebSocket is open and healthy.

        Returns
        -------
        bool
            True if connection is open.
        """
        return not self.socket.closed

    @property
    def session_id(self) -> Optional[str]:
        """
        Get current session ID.

        Returns
        -------
        Optional[str]
            Session ID if connected, None otherwise
        """
        return self._session_id

    @property
    def connected_at(self) -> Optional[datetime.datetime]:
        """
        Get connection timestamp.

        Returns
        -------
        Optional[datetime.datetime]
            When connection was established
        """
        return self._connected_at

    async def poll_event(self) -> None:
        """Poll for incoming WebSocket events and handle them appropriately."""
        try:
            msg = await asyncio.wait_for(self.socket.receive(), timeout=(self._keep_alive_timeout * 1.3))
            if msg.type is aiohttp.WSMsgType.TEXT:
                await self.received_message(data=msg.data)
            elif msg.type is aiohttp.WSMsgType.ERROR:
                _logger.error('Received error %s', msg)
                raise ConnectionClosed(self.socket) from msg.data
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING):
                _logger.debug('Received %s', msg)
                raise WebSocketClosure
        except (asyncio.TimeoutError, WebSocketClosure) as exc:
            code = self._close_code or self.socket.close_code
            raise ConnectionClosed(self.socket, code=code) from exc

    async def received_message(self, *, data: str) -> None:
        """Process received WebSocket message."""
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            _logger.error("Failed to parse JSON message: %s", data, exc_info=True)
            return

        metadata = Metadata.from_data(data['metadata'])
        payload = data['payload']

        if metadata.message_type == 'notification':
            await self._handle_notification(payload=payload, metadata=metadata)
            return

        if metadata.message_type == 'session_keepalive':
            if self._state.is_empty:
                _logger.debug("No active subscriptions, closing idle connection")
                await self.close(code=4003)
            return

        if metadata.message_type == 'session_welcome':
            session = payload['session']
            self._session_id = session['id']
            self._connected_at = utils.from_iso_string(session['connected_at'])
            self._keep_alive_timeout = session['keepalive_timeout_seconds']
            return

        if metadata.message_type == 'session_reconnect':
            url = payload['session']['reconnect_url']
            raise ReconnectWebSocket(url=url)

        if metadata.message_type == 'revocation':
            await self._state.revocation(Subscription.from_data(payload['subscription']), metadata)
            return

        raise RuntimeError(f"Unknown message type: {metadata.message_type}")

    async def close(self, code: int = 1000) -> None:
        """Gracefully close the WebSocket connection"""
        self._close_code = code
        if not self.socket.closed:
            try:
                await self.socket.close(code=code)
            except Exception as e:
                # Well, that didn't go as planned.
                _logger.error("Error closing WebSocket: %s", e)

    async def _handle_notification(self, *, payload: eventsub.NotificationPayload, metadata: Metadata) -> None:
        """Handle notification message. """
        subscription = payload['subscription']
        event = subscription['type'].replace('.', '_')
        try:
            func = self._eventsub_parsers[event]
        except KeyError:
            _logger.warning('Unknown event %s.', event)
            return
        try:
            func(payload['event'], Subscription.from_data(subscription), metadata)
        except Exception as exc:
            _logger.error('Unexpected error handling event %s, payload %s: %s', event, payload, exc,
                          exc_info=True)
