"""
MIT License

Copyright (c) 2020 CyCanCode

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = (
    'RequestError',
    'NoResults',
    'InvalidParameter',
    'TokenNotFound',
    'TokenEmpty'
)


class RequestError(Exception):
    """Base error class for all HTTP request related errors."""


class NoResults(RequestError):
    """Error raised when the API could not return results."""

    def __init__(self) -> None:
        super().__init__('Could not return results')


class InvalidParameter(RequestError):
    """Error raised when the arguments passed are invalid."""

    def __init__(self) -> None:
        super().__init__('Arguments passed are invalid')


class TokenNotFound(RequestError):
    """Error raised when the session token does not exist."""

    def __init__(self) -> None:
        super().__init__('Session Token does not exist')


class TokenEmpty(RequestError):
    """Error raised when the session token is empty."""

    def __init__(self) -> None:
        super().__init__(
            'Session Token has returned all possible questions for the specified query'
        )
