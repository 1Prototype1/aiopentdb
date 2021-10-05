"""
    aiopentdb.errors
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright (c) 2020 CyCanCode.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ('OpenTDBError', 'NoResults', 'InvalidParameter', 'TokenNotFound', 'TokenEmpty')

class OpenTDBError(Exception):
    """Base error class for all OpenTDB related errors."""

class NoResults(OpenTDBError):
    """Error raised when the API could not return any result.

    This error is a subclass of :class:`.OpenTDBError`.
    """

    def __init__(self):
        super().__init__('could not return results')

class InvalidParameter(OpenTDBError):
    """Error raised when the arguments passed during an API call are invalid.

    This error is a subclass of :class:`.OpenTDBError`.
    """

    def __init__(self):
        super().__init__('arguments passed in are not valid')

class TokenNotFound(OpenTDBError):
    """Error raised when a session token is not found.

    This error is a subclass of :class:`.OpenTDBError`.
    """

    def __init__(self):
        super().__init__('session token does not exist')

class TokenEmpty(OpenTDBError):
    """Error raised when a session token is empty.

    This error is a subclass of :class:`.OpenTDBError`.
    """

    def __init__(self):
        super().__init__('session token has returned all possible questions')
