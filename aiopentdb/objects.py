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

__all__ = ('Category', 'CategoryCount', 'GlobalCount', 'Question')


@dataclasses.dataclass(frozen=True)
class Category:
    name: str
    id: int
    type: CategoryType


@dataclasses.dataclass(frozen=True)
class CategoryCount:
    category: CategoryType
    total: int
    easy: int
    medium: int
    hard: int


@dataclasses.dataclass(frozen=True)
class GlobalCount:
    category: Union[CategoryType, str]
    total: int
    pending: int
    verified: int
    rejected: int


@dataclasses.dataclass(frozen=True)
class Question:
    type: QuestionType
    category: CategoryType
    difficulty: Difficulty
    question: str
    correct_answer: str
    incorrect_answers: List[str]

    @property
    def mixed_answers(self) -> List[str]:
        answers = [self.correct_answer, *self.incorrect_answers]
        random.shuffle(answers)
        return answers
