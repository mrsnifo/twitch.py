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

from typing import Optional, Any, Dict, Union, Tuple
import datetime
import aiohttp
import logging
import yarl
import json
import time

__all__ = (
    'from_iso_string',
    'to_rfc3339_string',
    'normalize_timezone',
    'json_or_text',
    'setup_logging',
    'parse_mock_urls',
    'ExponentialBackoff',
)


def from_iso_string(timestamp: str) -> datetime.datetime:
    """Convert ISO8601 string to datetime object."""
    return datetime.datetime.fromisoformat(timestamp)

def to_rfc3339_string(dt: datetime.datetime) -> str:
    """Convert datetime to RFC3339 string format for Twitch API."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.isoformat()

def normalize_timezone(dt: datetime.datetime) -> datetime.datetime:
    """Normalize datetime to have timezone information."""
    return dt.replace(tzinfo=datetime.timezone.utc) if dt.tzinfo is None else dt

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    """Return parsed JSON if possible, otherwise return plain text."""
    body = await response.text(encoding='utf-8')
    content_type = response.headers.get('content-type', '').lower()
    try:
        if 'application/json' in content_type:
            return json.loads(body) if body else {}
        else:
            return json.loads(body)
    except (ValueError, json.JSONDecodeError):
        return body

def setup_logging(handler: Optional[logging.Handler] = None,
                  level: Optional[int] = None,
                  root: bool = True
                  ) -> None:
    """Setup logging configuration."""

    # Use provided handler or default to console
    handler = handler or logging.StreamHandler()

    # Set formatter with timestamp, level, and message
    handler.setFormatter(logging.Formatter(
        '[{asctime}] [{levelname}] {name}: {message}',
        '%Y-%m-%d %H:%M:%S',
        style='{'
    ))

    logger = logging.getLogger() if root else logging.getLogger(__name__.split('.')[0])
    logger.setLevel(level if level is not None else logging.INFO)
    logger.addHandler(handler)

def parse_mock_urls(input_url: str) -> Tuple[str, str]:
    """Parse input URL and return HTTP and WebSocket mock URLs."""
    url = yarl.URL(input_url)
    mock_url = f"{url.host}:{url.port}" if url.host else input_url
    return f"http://{mock_url}/", f"ws://{mock_url}/ws"


class ExponentialBackoff:
    """Handles retry intervals with exponential backoff."""

    __slots__ = ('base_delay', 'max_delay', 'reset_interval', 'retry_count', 'last_failure_time')

    def __init__(self, base_delay: int = 1, max_delay: int = 180, reset_interval: int = 300) -> None:
        self.base_delay: int = base_delay
        self.max_delay: int = max_delay
        self.reset_interval: int = reset_interval
        self.retry_count: int = 0
        self.last_failure_time: float = time.monotonic()

    def get_delay(self) -> int:
        """ Determine the delay before the next retry attempt."""
        current_time = time.monotonic()
        elapsed_time = current_time - self.last_failure_time

        if elapsed_time > self.reset_interval:
            self.retry_count = 0

        delay = min(self.base_delay * 2 ** self.retry_count, self.max_delay)
        self.retry_count += 1
        self.last_failure_time = current_time
        return delay
