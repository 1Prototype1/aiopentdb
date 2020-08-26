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

import enum

__all__ = (
    'CategoryType',
    'QuestionType',
    'Difficulty',
    'Encoding'
)


class CategoryType(enum.Enum):
    """Enum that represents an OpenTDB category object type."""

    general_knowledge      = 9
    books                  = 10
    film                   = 11
    music                  = 12
    musicals_and_theatres  = 13
    television             = 14
    video_games            = 15
    board_games            = 16
    nature                 = 17
    computers              = 18
    mathematics            = 19
    mythology              = 20
    sports                 = 21
    geography              = 22
    history                = 23
    politics               = 24
    art                    = 25
    celebrities            = 26
    animals                = 27
    vehicles               = 28
    comics                 = 29
    gadgets                = 30
    anime_and_manga        = 31
    cartoon_and_animations = 32


class QuestionType(enum.Enum):
    """Enum that represents an OpenTDB question object type."""

    multiple = 'multiple'
    boolean  = 'boolean'


class Difficulty(enum.Enum):
    """Enum that represents an OpenTDB difficulty."""

    easy   = 'easy'
    medium = 'medium'
    hard   = 'hard'


class Encoding(enum.Enum):
    """Enum that represents an OpenTDB encoding."""

    url    = 'url3986'
    base64 = 'base64'
