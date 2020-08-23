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
    """Represents an OpenTDB category object.

    Attributes
    ----------
    name: `str`
        Name of the category object.
    id: `int`
        ID of the category object.
    type: `CategoryType`
        Type of the category object.
    """

    name: str
    id: int
    type: CategoryType


@dataclasses.dataclass(frozen=True)
class Count:
    """Represents an OpenTDB count object.

    Attributes
    ----------
    category: `Category`
        Category that owns the count object.
    total: `int`
        Total question count.
    easy: `int`
        Easy question count.
    medium: `int`
        Medium question count.
    hard: `int`
        Hard question count.
    """

    category: Category
    total: int
    easy: int
    medium: int
    hard: int


@dataclasses.dataclass(frozen=True)
class GlobalCount:
    """Represents an OpenTDB global count object.

    Attributes
    ----------
    category: `Union[Category, str]`
        Category that owns the global count object.
    total: `int`
        Total question count.
    pending: `int`
        Pending question count.
    verified: `int`
        Verified question count.
    rejected: `int`
        Rejected question count.
    """

    category: Union[Category, str]
    total: int
    pending: int
    verified: int
    rejected: int


@dataclasses.dataclass(frozen=True)
class Question:
    """Represents an OpenTDB question object.

    Attributes
    ----------
    type: `QuestionType`
        Type of the question object.
    category: `Category`
        Category of the question object.
    difficulty: `Difficulty`
        Difficulty of the question object.
    content: `str`
        Content of the question object.
    correct_answer: `str`
        Correct answer for the question content.
    incorrect_answers: `List[str]`
        List of incorrect answers.
    mixed_answers: `List[str]`
        List of mixed answers.
    """

    type: QuestionType
    category: Category
    difficulty: Difficulty
    content: str
    correct_answer: str
    incorrect_answers: List[str]

    @property
    def mixed_answers(self) -> List[str]:
        answers = [self.correct_answer, *self.incorrect_answers]
        random.shuffle(answers)
        return answers
