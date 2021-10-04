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

import dataclasses
import random
from typing import List, Union

from .enums import CategoryType, Difficulty, QuestionType

__all__ = (
    'Category',
    'Count',
    'GlobalCount',
    'Question'
)


@dataclasses.dataclass(frozen=True)
class Category:
    """|noinstantiate|

    |dataclass| an OpenTDB category object.

    Attributes
    ----------
    name: :class:`str`
        Name of the category object.
    id: :class:`int`
        ID of the category object.
    type: :class:`.CategoryType`
        Type of the category object.
    """

    name: str
    id: int
    type: CategoryType


@dataclasses.dataclass(frozen=True)
class Count:
    """|noinstantiate|

    |dataclass| an OpenTDB count object.

    Attributes
    ----------
    category: :class:`.Category`
        Category that owns the count object.
    total: :class:`int`
        Total question count.
    easy: :class:`int`
        Easy question count.
    medium: :class:`int`
        Medium question count.
    hard: :class:`int`
        Hard question count.
    """

    category: Category
    total: int
    easy: int
    medium: int
    hard: int


@dataclasses.dataclass(frozen=True)
class GlobalCount:
    """|noinstantiate|

    |dataclass| an OpenTDB global count object.

    Attributes
    ----------
    category: Union[:class:`.Category`, :class:`str`]
        Category that owns the global count object.
    total: :class:`int`
        Total question count.
    pending: :class:`int`
        Pending question count.
    verified: :class:`int`
        Verified question count.
    rejected: :class:`int`
        Rejected question count.
    """

    category: Union[Category, str]
    total: int
    pending: int
    verified: int
    rejected: int


@dataclasses.dataclass(frozen=True)
class Question:
    """|noinstantiate|

    |dataclass| an OpenTDB question object.

    Attributes
    ----------
    type: :class:`.QuestionType`
        Type of the question object.
    category: :class:`.Category`
        Category of the question object.
    difficulty: :class:`.Difficulty`
        Difficulty of the question object.
    content: :class:`str`
        Content of the question object.
    correct_answer: :class:`str`
        Correct answer for the question content.
    incorrect_answers: List[:class:`str`]
        List of incorrect answers.
    """

    type: QuestionType
    category: Category
    difficulty: Difficulty
    content: str
    correct_answer: str
    incorrect_answers: List[str]

    @property
    def mixed_answers(self) -> List[str]:
        """List[:class:`str`]: List of mixed answers."""

        answers = [self.correct_answer, *self.incorrect_answers]
        random.shuffle(answers)
        return answers
