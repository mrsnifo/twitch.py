"""
twitch.py

Real-time Twitch EventSub and Helix API Integration

:copyright: (c) 2025-present mrsnifo
:license: MIT, see LICENSE for more details.
"""

__title__ = 'twitch.py'
__version__ = '4.0.3'
__license__ = 'MIT License'
__author__ = 'mrsnifo'
__copyright__ = 'Copyright 2025-present mrsnifo'
__email__ = 'snifo@mail.com'
__url__ = 'https://github.com/mrsnifo/twitch.py'

from .errors import *
from .models import *
from .app import *

from . import (
    eventsub as eventsub,
    oauth as oauth,
    utils as utils,
)
