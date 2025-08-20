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

from typing import Any, Optional, Callable, TYPE_CHECKING, Tuple, Type, NamedTuple
from ..errors import HTTPException, NotFound, Unauthorized, BadRequest
from .gateway import EventSubWebSocket, ReconnectWebSocket
from .errors import ConnectionClosed, ShardError
from .client import ClientApp
from .. import utils
import asyncio
import aiohttp
import logging

__all__ = ('Shard', 'MultiShardClientApp')

_logger = logging.getLogger(__name__)

class _QueueItem(NamedTuple):
    """
    Queue item for shard event communication.

    A lightweight data structure for passing shard events through the event queue.
    Uses integer status codes for efficient event type identification.

    Parameters
    ----------
    status: int
        Event status code identifying the type of event. Status codes:

        * 0 - close: Close the shard connection
        * 1 - reconnect: Reconnect the shard
        * 2 - terminate: Terminate shard with error
        * 3 - clean_close: Clean shutdown
    shard: Optional[Shard]
        The shard instance associated with this event, or None for app-level events.
    error: Optional[Exception], default None
        Exception instance if the event was triggered by an error.

    Attributes
    ----------
    status: int
        The event status code.
    shard: Optional[Shard]
        The shard instance associated with this event, or None for app-level events.
    error: Optional[Exception]
        The associated error, if any.
    """

    status: int
    shard: Optional[Shard]
    error: Optional[Exception]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _QueueItem):
            return NotImplemented
        return (self.status == other.status and
                self.shard == other.shard and
                self.error == other.error)

    def __hash__(self) -> int:
        return hash((self.status, id(self.shard), self.error))

    def __repr__(self) -> str:
        shard_id = self.shard.id if self.shard else None
        return f'_QueueItem(status={self.status}, shard={shard_id}, error={self.error})'


class Shard:
    """
    Individual shard connection handler for multi-shard EventSub WebSocket clients.

    Parameters
    ----------
    conduit_id: str
        The conduit ID this shard belongs to.
    shard_id: int
        The unique identifier for this shard.
    ws: EventSubWebSocket
        The WebSocket connection for this shard.
    client: MultiShardClientApp
        The parent multi-shard client instance.
    queue_put: Callable[[_QueueItem], None]
        Function to put items into the parent's event queue.
    reconnect: bool
        Whether this shard should attempt automatic reconnection on failures.
    """

    def __init__(self,
                 conduit_id: str,
                 shard_id: int,
                 *,
                 ws: EventSubWebSocket,
                 client: MultiShardClientApp,
                 queue_put: Callable[[_QueueItem], None],
                 reconnect: bool
                 ) -> None:
        self.ws: EventSubWebSocket = ws
        self._conduit_id = conduit_id
        self._shard_id = shard_id
        self._client: ClientApp = client
        self._dispatch: Callable[..., None] = client.dispatch
        self._queue_put: Callable[[_QueueItem], None] = queue_put
        self._reconnect = reconnect
        self._backoff: utils.ExponentialBackoff = utils.ExponentialBackoff()
        self._task: Optional[asyncio.Task] = None
        self._handled_exceptions: Tuple[Type[Exception], ...] = (
            OSError,
            HTTPException,
            ConnectionClosed,
            aiohttp.ClientError,
            asyncio.TimeoutError,
            ShardError
        )

    @property
    def id(self) -> int:
        """
        Get the shard's unique identifier.

        Returns
        -------
        int
            The shard ID assigned to this shard instance.
        """
        return self._shard_id

    def launch(self) -> None:
        """
        Launch the shard worker task.

        !!! warning

            This method should only be called once per shard instance.
            Multiple calls will cancel the previous task.

        Creates and starts an asyncio task that handles event polling
        for this shard's WebSocket connection.
        """
        self._task = self._client.loop.create_task(self.worker())

    def _cancel_task(self) -> None:
        """Cancel the active worker task if running."""
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def close(self) -> None:
        """
        Close the shard connection and clean up resources.

        Cancels the worker task and closes the WebSocket connection
        with a clean shutdown code.
        """
        self._cancel_task()
        await self.ws.close(code=1000)

    async def reconnect(self, gateway: Optional[str] = None) -> None:
        """
        Reconnect the shard to a new or existing WebSocket gateway.

        Parameters
        ----------
        gateway: Optional[str]
            Specific gateway URL to reconnect to. If None, uses the default gateway.
        """
        self._cancel_task()
        try:
            coro = EventSubWebSocket.connect_websocket(self._client, gateway=gateway)
            self.ws = await asyncio.wait_for(coro, timeout=60.0)
            await self._client.identify_shard(self._conduit_id, self._shard_id, session_id=self.ws.session_id)
        except self._handled_exceptions as exc:
            await self._handle_disconnect(exc)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            item = _QueueItem(2, self, exc)
            self._queue_put(item)
        else:
            self.launch()

    @property
    def is_running(self) -> bool:
        """
        Check if the shard worker task is currently running.

        Returns
        -------
        bool
            True if the worker task exists and is not done, False otherwise.
        """
        return self._task is not None and not self._task.done()

    async def disconnect(self) -> None:
        """Gracefully disconnect the shard and dispatch disconnect events."""
        await self.close()
        self._dispatch('shard_disconnect', self.id)

    async def _handle_disconnect(self, exc: Exception) -> None:
        """Handle unexpected disconnections with reconnection logic."""
        self._dispatch('disconnect')
        self._dispatch('shard_disconnect', self.id)

        if not self._reconnect or isinstance(exc, (NotFound, Unauthorized)):
            item = _QueueItem(2, self, exc)
            self._queue_put(item)
            return

        if self._client.is_closed():
            return

        retry = self._backoff.get_delay()
        _logger.error('Attempting a reconnect for shard ID %s in %.2fs', self.id, retry, exc_info=exc)
        await asyncio.sleep(retry)
        reconnect_exc = ReconnectWebSocket(url=None)
        item = _QueueItem(1, self, reconnect_exc)
        self._queue_put(item)

    async def worker(self) -> None:
        """Main worker loop for handling WebSocket events."""
        while not self._client.is_closed():
            try:
                await self.ws.poll_event()
            except ReconnectWebSocket as e:
                item = _QueueItem(1, self, e)
                self._queue_put(item)
                break
            except self._handled_exceptions as e:
                await self._handle_disconnect(e)
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                item = _QueueItem(2, self, e)
                self._queue_put(item)
                break

    def __repr__(self) -> str:
        return f"Shard(id={self._shard_id}, is_running={self.is_running})"


class MultiShardClientApp(ClientApp):
    """
    Multi-shard Twitch EventSub WebSocket client for high-throughput applications.

    ???+ note

        This client is designed for applications expecting high event volumes.
        For most use cases, the standard ClientApp is sufficient and simpler to use.

    Parameters
    ----------
    client_id: str
        The application's unique client identifier.
    shard_connect_timeout: Optional[float]
        Timeout in seconds for individual shard connections.
    client_secret: str
        The application's client secret for secure authentication.
    **kwargs: Any
        Additional configuration options passed to the parent ClientApp.
    """

    if TYPE_CHECKING:
        __queue: asyncio.Queue[_QueueItem]

    def __init__(self, client_id: str, client_secret: str, **kwargs: Any) -> None:
        self.shard_connect_timeout: Optional[float] = kwargs.pop('shard_connect_timeout', 180.0)
        super().__init__(client_id, client_secret, **kwargs)
        self.__shards = {}

    @property
    def shards(self) -> Tuple[Shard, ...]:
        """
        Get all active shard instances.

        Returns
        -------
        Tuple[Shard, ...]
            Read-only tuple containing all currently managed shard instances.
            Shards are ordered by their creation time, not shard ID.
        """
        return tuple(self.__shards.values())

    def _async_setup(self) -> None:
        super()._async_setup()
        self.__queue: asyncio.Queue[_QueueItem] = asyncio.Queue()

    def get_shard(self, shard_id: int, /) -> Optional[Shard]:
        """
        Get a specific shard by its ID.

        Parameters
        ----------
        shard_id: int
            The ID of the shard to retrieve.

        Returns
        -------
        Optional[Shard]
            The shard instance if found, None if no shard exists with the given ID.
        """
        try:
            parent = self.__shards[shard_id]
        except KeyError:
            return None
        else:
            return parent

    async def launch_shard(self, conduit_id: str, shard_id: int, *, reconnect: bool) -> None:
        """
        Launch a single shard connection.

        ???+ note
            Connection failures other than the above exceptions will trigger
            automatic retry with exponential backoff.

        Parameters
        ----------
        conduit_id: str
            The conduit ID to register the shard with.
        shard_id: int
            The unique identifier for this shard.
        reconnect: bool
            Whether this shard should attempt automatic reconnection.

        Raises
        ------
        ShardError
            If shard identification fails with an unrecoverable error.
        BadRequest
            If the request parameters are invalid.
        NotFound
            If the conduit is not found.
        Unauthorized
            If authentication fails.
        """
        try:
            coro = EventSubWebSocket.connect_websocket(self)
            ws = await asyncio.wait_for(coro, timeout=self.shard_connect_timeout)
            await self.identify_shard(conduit_id, shard_id, session_id=ws.session_id)
        except (ShardError, NotFound, Unauthorized, BadRequest):
            await self.close()
            raise
        except (Exception, OSError):
            if self.is_closed():
                raise
            _logger.exception('Failed to connect for shard_id: %s. Retrying...', shard_id)
            await asyncio.sleep(6.0)
            return await self.launch_shard(conduit_id, shard_id, reconnect=reconnect)

        self.__shards[shard_id] = ret = Shard(
            conduit_id,
            shard_id,
            ws=ws,
            client=self,
            queue_put=self.__queue.put_nowait,
            reconnect=reconnect
        )
        ret.launch()
        return None

    async def launch_shards(self, conduit_id: str, shard_ids: Tuple[int, ...], *, reconnect: bool) -> None:
        """
        Launch multiple shard connections sequentially.

        Parameters
        ----------
        conduit_id: str
            The conduit ID to register all shards with.
        shard_ids: Tuple[int, ...]
            Tuple of shard IDs to launch.
        reconnect: bool
            Whether shards should attempt automatic reconnection.
        """
        if self.is_closed():
            return

        for shard_id in shard_ids:
            await self.launch_shard(conduit_id, shard_id, reconnect=reconnect)

    async def connect(self, conduit_id: str, *, shard_ids: Tuple[int, ...], reconnect: bool = True) -> None:
        """
        Connect to Twitch EventSub with multiple shards.

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
            Whether shards should automatically reconnect on failures.

        Raises
        ------
        ShardError
            If any shard fails to connect with an unrecoverable error.
        NotFound
            If the conduit is not found.
        Unauthorized
            If authentication fails.
        BadRequest
            If request parameters are invalid.
        ConnectionClosed
            If connections are closed unexpectedly without reconnect enabled.
        """
        await self.launch_shards(conduit_id, shard_ids, reconnect=reconnect)
        while not self.is_closed():
            item = await self.__queue.get()
            if item.status == 0:
                await self.close()
                if isinstance(item.error, ConnectionClosed):
                    if item.error.code != 1000:
                        raise item.error
                return
            elif item.status == 1:
                if isinstance(item.error, ReconnectWebSocket):
                    await item.shard.reconnect(gateway=item.error.url)
            elif item.status == 2:
                await self.close()
                raise item.error
            elif item.status == 3:
                return

    async def close(self) -> None:
        if self._closing_task:
            return await self._closing_task

        async def _close():
            to_close = [asyncio.ensure_future(shard.close(), loop=self.loop) for shard in self.__shards.values()]
            if to_close:
                await asyncio.wait(to_close)
            await self.http.close()
            item = _QueueItem(3, None, None)
            self.__queue.put_nowait(item)

        self._closing_task = asyncio.create_task(_close())
        return await self._closing_task