"""
    aiopentdb
    ~~~~~~~~~

    Async Python wrapper for the OpenTDB API

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

import collections as _collections

from .client import *
from .enums import *
from .errors import *
from .iterators import *
from .objects import *

__version__ = '1.0.0'

_VersionInfo = _collections.namedtuple('VersionInfo', 'major minor micro releaselevel serial')
version_info = _VersionInfo(1, 0, 0, 'final', 0)
