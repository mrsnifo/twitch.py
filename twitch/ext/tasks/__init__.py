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

from typing import Callable, Any, Dict, List, Coroutine, TypeVar, Optional, Union
import asyncio
import inspect
import time

__all__ = ('Loop', 'loop')

T = TypeVar('T', bound=Callable[..., Coroutine[Any, Any, None]])

import logging
_logger = logging.getLogger(__name__)


class Loop:
    """A task loop for asynchronous operations in Twitch applications."""

    def __init__(self,
                 coro: Callable[..., Coroutine[Any, Any, None]],
                 seconds: Optional[float] = None,
                 minutes: Optional[float] = None,
                 hours: Optional[float] = None,
                 count: Optional[int] = None,
                 name: Optional[str] = None,
                 max_catchup: int = 5) -> None:
        # Validate timing parameters
        timing_params = [seconds, minutes, hours]
        provided_params = [p for p in timing_params if p is not None]

        if len(provided_params) != 1:
            raise ValueError("Exactly one of seconds, minutes, or hours must be provided")

        if seconds is not None:
            if seconds <= 0:
                raise ValueError("seconds must be positive")
            calculated_interval = seconds
        elif minutes is not None:
            if minutes <= 0:
                raise ValueError("minutes must be positive")
            calculated_interval = minutes * 60
        elif hours is not None:
            if hours <= 0:
                raise ValueError("hours must be positive")
            calculated_interval = hours * 3600
        else:
            # This should never happen due to the validation above, but just in case
            raise ValueError("No valid timing parameter provided")

        if max_catchup <= 0:
            raise ValueError("max_catchup must be positive")
        if not inspect.iscoroutinefunction(coro):
            raise TypeError(f'Expected coroutine function, not {type(coro).__name__!r}.')

        self.coro = coro
        self.interval = calculated_interval
        self.count = count
        self.name = name or f"Loop-{coro.__name__}"
        self.max_catchup = max_catchup

        self._running = False
        self._paused = False
        self._stopping = False
        self._task: Optional[asyncio.Task] = None
        self._execution_count = 0
        self._start_time = 0.0
        self._pause_time = 0.0
        self._total_pause_time = 0.0

        self._on_start: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
        self._on_stop: Optional[Callable[[], Coroutine[Any, Any, None]]] = None
        self._on_before_execution: Optional[Callable[[int], Coroutine[Any, Any, None]]] = None
        self._on_error: Optional[Callable[[Exception, int], Coroutine[Any, Any, None]]] = None

        self._skip_next = False
        self._priority_queue: List[Callable[..., Coroutine[Any, Any, None]]] = []

        self._bound_instance = None

    def __get__(self, instance, owner):
        """Descriptor protocol to handle class method binding."""
        if instance is None:
            return self

        # Create a bound copy of the loop for this instance
        bound_loop = Loop(
            coro=self.coro,
            seconds=self.interval,
            count=self.count,
            name=f"{owner.__name__}.{self.name}",
            max_catchup=self.max_catchup
        )
        bound_loop._bound_instance = instance

        # Copy callbacks if they exist
        bound_loop._on_start = self._on_start
        bound_loop._on_stop = self._on_stop
        bound_loop._on_before_execution = self._on_before_execution
        bound_loop._on_error = self._on_error

        return bound_loop

    @property
    def is_running(self) -> bool:
        """Check if loop is currently running."""
        return self._running and not self._paused

    @property
    def is_paused(self) -> bool:
        """Check if loop is currently paused."""
        return self._paused

    @property
    def current_execution(self) -> int:
        """Get the current execution count."""
        return self._execution_count

    @property
    def elapsed_time(self) -> float:
        """Get elapsed time since start (excluding pause time) in seconds."""
        if self._start_time == 0:
            return 0.0
        current_time = time.perf_counter()
        if self._paused:
            return self._pause_time - self._start_time - self._total_pause_time
        return current_time - self._start_time - self._total_pause_time

    def start(self, *args: Any, **kwargs: Any) -> asyncio.Task:
        """
        Start the loop execution.

        Parameters
        ----------
        *args: Any
            Positional arguments to pass to the coroutine function.
        **kwargs: Any
            Keyword arguments to pass to the coroutine function.

        Returns
        -------
        asyncio.Task
            The task running the loop.

        Raises
        ------
        RuntimeError
            If the loop is already running or fails to resume from pause.
        """
        if self._running:
            raise RuntimeError('Loop is already running.')

        if self._paused:
            result = self.resume()
            if result is None:
                raise RuntimeError("Failed to resume paused loop")
            return result

        self._running = True
        self._stopping = False
        self._execution_count = 0
        self._start_time = time.perf_counter()
        self._total_pause_time = 0.0

        # If this is a bound method, prepend the instance to args
        if self._bound_instance is not None:
            args = (self._bound_instance,) + args

        self._task = asyncio.create_task(self._run(*args, **kwargs), name=self.name)

        if self._on_start:
            try:
                asyncio.create_task(self._on_start())
            except Exception as e:
                _logger.error(f"Error in on_start callback for loop '{self.name}': {e}")

        return self._task

    def stop(self) -> None:
        """
        Stop the loop gracefully.

        The loop will finish its current execution and then stop.
        """
        if self._running:
            self._stopping = True

    def pause(self) -> None:
        """
        Pause the loop execution.

        The loop will pause after completing its current execution.
        """
        if self._running and not self._paused:
            self._paused = True
            self._pause_time = time.perf_counter()

    def resume(self) -> Optional[asyncio.Task]:
        """
        Resume the loop from a paused state.

        Returns
        -------
        Optional[asyncio.Task]
            The task running the loop, or None if not paused.
        """
        if self._paused:
            pause_duration = time.perf_counter() - self._pause_time
            self._total_pause_time += pause_duration
            self._paused = False
            return self._task
        return None

    def cancel(self) -> None:
        """
        Cancel the loop immediately.

        This stops the loop without waiting for the current execution to complete.
        """
        if self._task and not self._task.done():
            self._task.cancel()

        self._running = False
        self._paused = False
        self._stopping = False

    def skip_next_execution(self) -> None:
        """Skip the next scheduled execution."""
        self._skip_next = True

    def queue_priority_task(self, task: Callable[..., Coroutine[Any, Any, None]]) -> None:
        """
        Queue a high-priority task to run before the next execution.

        Parameters
        ----------
        task: Callable[..., Coroutine[Any, Any, None]]
            The coroutine function to run as a priority task.

        Raises
        ------
        Exception
            If the task cannot be queued.
        """
        try:
            self._priority_queue.append(task)
        except Exception as e:
            _logger.error(f"Failed to queue priority task for loop '{self.name}': {e}")
            raise

    async def _run(self, *args: Any, **kwargs: Any) -> None:
        """Internal loop execution implementation."""
        last_execution_time = time.perf_counter()
        accumulated_time = 0.0
        consecutive_errors = 0
        max_consecutive_errors = 10

        try:
            while not self._stopping:
                try:
                    # Handle pause
                    while self._paused and not self._stopping:
                        await asyncio.sleep(0.01)

                    if self._stopping:
                        break

                    current_time = time.perf_counter()
                    accumulated_time += current_time - last_execution_time

                    # Calculate how many executions we need to catch up
                    executions_to_run = min(int(accumulated_time / self.interval), self.max_catchup)
                    if executions_to_run == 0:
                        executions_to_run = 1

                    # Run priority tasks first
                    while self._priority_queue:
                        try:
                            priority_task = self._priority_queue.pop(0)
                            await priority_task()
                        except Exception as e:
                            _logger.error(f"Error in priority task for loop '{self.name}': {e}")

                    # Execute main function (catch-up mechanism)
                    for execution_iteration in range(executions_to_run):
                        if self._stopping:
                            break

                        if self._skip_next:
                            self._skip_next = False
                            continue

                        try:
                            # Call before execution callback
                            if self._on_before_execution:
                                await self._on_before_execution(self._execution_count)

                            # Execute main coroutine
                            await self.coro(*args, **kwargs)

                            # Reset error counter on successful execution
                            consecutive_errors = 0

                        except Exception as e:
                            consecutive_errors += 1
                            _logger.error(f"Error in execution {self._execution_count} of loop '{self.name}': {e}")

                            # Handle error via callback or break on too many consecutive errors
                            if self._on_error:
                                try:
                                    await self._on_error(e, self._execution_count)
                                except Exception as callback_error:
                                    _logger.error(f"Error in error callback for loop '{self.name}': {callback_error}")

                            if consecutive_errors >= max_consecutive_errors:
                                _logger.critical(f"Too many consecutive errors ({consecutive_errors}) "
                                                 f"in loop '{self.name}', stopping")
                                self._stopping = True
                                break

                        self._execution_count += 1

                        if self.count and self._execution_count >= self.count:
                            self._stopping = True
                            break

                    # Sleep calculation with drift correction
                    accumulated_time -= executions_to_run * self.interval
                    next_execution_time = last_execution_time + (executions_to_run * self.interval)
                    sleep_time = next_execution_time - time.perf_counter()

                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)

                    last_execution_time = next_execution_time

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    _logger.error(f"Unexpected error in loop '{self.name}': {e}")

                    if self._on_error:
                        try:
                            await self._on_error(e, self._execution_count)
                        except Exception as callback_error:
                            _logger.error(f"Error in error callback for loop '{self.name}': {callback_error}")
                    break

        except Exception as e:
            _logger.critical(f"Critical error in loop '{self.name}': {e}")
        finally:
            # Cleanup
            self._running = False
            self._paused = False
            self._stopping = False

            if self._on_stop:
                try:
                    await self._on_stop()
                except Exception as e:
                    _logger.error(f"Error in on_stop callback for loop '{self.name}': {e}")

    def on_start(self, callback: Callable[[], Coroutine[Any, Any, None]]) -> Callable[[], Coroutine[Any, Any, None]]:
        """
        Set callback for when the loop starts.

        Parameters
        ----------
        callback: Callable[[], Coroutine[Any, Any, None]]
            The coroutine function to call when the loop starts.

        Returns
        -------
        Callable[[], Coroutine[Any, Any, None]]
            The same callback function (for chaining).
        """
        self._on_start = callback
        return callback

    def on_stop(self, callback: Callable[[], Coroutine[Any, Any, None]]) -> Callable[[], Coroutine[Any, Any, None]]:
        """
        Set callback for when the loop stops.

        Parameters
        ----------
        callback: Callable[[], Coroutine[Any, Any, None]]
            The coroutine function to call when the loop stops.

        Returns
        -------
        Callable[[], Coroutine[Any, Any, None]]
            The same callback function (for chaining).
        """
        self._on_stop = callback
        return callback

    def before_execution(self,
                         callback: Callable[[int],
                         Coroutine[Any, Any, None]]
                         ) -> Callable[[int], Coroutine[Any, Any, None]]:
        """
        Set callback called before each execution.

        Parameters
        ----------
        callback: Callable[[int], Coroutine[Any, Any, None]]
            The coroutine function to call before each execution.
            Receives the current execution count as a parameter.

        Returns
        -------
        Callable[[int], Coroutine[Any, Any, None]]
            The same callback function (for chaining).
        """
        self._on_before_execution = callback
        return callback

    def on_error(self,
                 callback: Callable[[Exception, int],
                 Coroutine[Any, Any, None]]
                 ) -> Callable[[Exception, int], Coroutine[Any, Any, None]]:
        """
        Set callback for error handling.

        Parameters
        ----------
        callback: Callable[[Exception, int], Coroutine[Any, Any, None]]
            The coroutine function to call when an error occurs.
            Receives the exception and current execution count as parameters.

        Returns
        -------
        Callable[[Exception, int], Coroutine[Any, Any, None]]
            The same callback function (for chaining).
        """
        self._on_error = callback
        return callback

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the loop's current state.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing loop information with keys:
            - name: str - Loop name
            - running: bool - Whether the loop is running
            - paused: bool - Whether the loop is paused
            - current_execution: int - Current execution count
            - interval: float - Execution interval in seconds
            - elapsed_time: float - Elapsed time in seconds
            - priority_queue_size: int - Size of priority queue
        """
        return {
            'name': self.name,
            'running': self._running,
            'paused': self._paused,
            'current_execution': self._execution_count,
            'interval': self.interval,
            'elapsed_time': self.elapsed_time,
            'priority_queue_size': len(self._priority_queue),
        }


def loop(func: Optional[T] = None,
         *,
         seconds: Optional[float] = None,
         minutes: Optional[float] = None,
         hours: Optional[float] = None,
         count: Optional[int] = None,
         name: Optional[str] = None,
         max_catchup: int = 5
         ) -> Union[Loop, Callable[[T], Loop]]:
    """
    Decorator to create a task loop for Twitch applications.

    This decorator transforms a coroutine function into a Loop instance
    that can be started, stopped, paused, and resumed. Perfect for
    recurring tasks like monitoring streams, updating data, or
    performing periodic maintenance.

    Parameters
    ----------
    func: Optional[T]
        The function to decorate.
    seconds: Optional[float]
        Interval in seconds between executions.
    minutes: Optional[float]
        Interval in minutes between executions.
    hours: Optional[float]
        Interval in hours between executions.
    count: Optional[int]
        Maximum number of executions. If None, loop runs indefinitely.
    name: Optional[str]
        Custom name for the loop.
    max_catchup: int
        Maximum number of catch-up executions in one cycle.

    Returns
    -------
    Union[Loop, Callable[[T], Loop]]
        A Loop instance or decorator function.

    Raises
    ------
    ValueError
        If no timing parameter is provided or multiple are provided.

    Example
    -------
    Simple loop::

        @loop(seconds=30)
        async def my_task():
            print("Running...")

        my_task.start()

    With parameters::

        @loop(minutes=5, count=10)
        async def limited_task():
            print("This runs 10 times")

        limited_task.start()

    Passing variables::

        @loop(seconds=10)
        async def process_user(user_id, username):
            print(f"Processing {username} ({user_id})")

        process_user.start("123456", "streamer_name")
    """
    timing_params = [seconds, minutes, hours]
    provided_params = [p for p in timing_params if p is not None]

    if len(provided_params) != 1:
        raise ValueError("Exactly one of seconds, minutes, or hours must be provided")

    def decorator(f: T) -> Loop:
        """
        The actual decorator that wraps the coroutine function.

        Parameters
        ----------
        f: T
            The coroutine function to wrap.

        Returns
        -------
        Loop
            A configured Loop instance.
        """
        loop_name = name or f"twitch.py:tasks:{f.__name__}"
        return Loop(
            coro=f,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            count=count,
            name=loop_name,
            max_catchup=max_catchup
        )

    if func is not None:
        return decorator(func)

    return decorator